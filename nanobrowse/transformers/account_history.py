from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_weight, format_balance, format_hash, format_account
from utils.known import AccountLookup
from utils.rpc_execution import execute_and_handle_errors
from utils.logger import logger

HISTORY_COUNT = 2500  # if you use a proxy, make sure it allows this many

account_history_transformer = Blueprint(
    'account_history_transformer', __name__)
account_lookup = AccountLookup()


@account_history_transformer.route('/account_history/<account>', methods=['GET'])
async def get_account_history(account):
    data = await fetch_account_history(account)

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_account_data(data)
    return jsonify(transformed_data)


async def fetch_account_history(account):

    tasks = {"response": nanorpc.account_history(
        account, count=HISTORY_COUNT, raw="true")}
    response = await execute_and_handle_errors(tasks)
    return response["response"] or {}


def format_entry_amount(amount, block_type):
    if block_type == "change":
        return "new rep"
    else:
        return format_balance(amount, block_type)


def group_and_sort_history(transformed_history):
    grouped_history = {}
    for entry in transformed_history:
        key = (entry['type'], entry['account'])
        amount = int(entry.get('amount', '0') or '0')
        if key not in grouped_history:
            grouped_entry = entry.copy()
            grouped_entry['total_amount'] = amount
            grouped_entry['transaction_count'] = 1
        else:
            grouped_entry = grouped_history[key]
            grouped_entry['total_amount'] += amount
            grouped_entry['transaction_count'] += 1
            if entry['timestamp'] > grouped_entry['timestamp']:
                grouped_entry['time_ago'] = entry['time_ago']
                grouped_entry['timestamp'] = entry['timestamp']
        grouped_history[key] = grouped_entry

    sorted_grouped_history = sorted(
        grouped_history.values(),
        key=lambda x: x['total_amount'],
        reverse=True
    )

    for entry in sorted_grouped_history:
        entry['amount_formatted'] = format_entry_amount(
            entry['total_amount'], entry['type'])
        entry.pop('amount', None)
        entry.pop('hash', None)
        entry.pop('height', None)

    return sorted_grouped_history


async def transform_history_entry(entry):
    time_ago = get_time_ago(entry.get("local_timestamp"))
    account = entry.get("account") or entry.get("representative")
    confirmed = entry.get("confirmed")
    block_type = entry.get("subtype")
    amount = entry.get("amount")
    block_hash = entry.get("hash")
    block_hash_formatted = format_hash(block_hash)
    block_type_formatted = f"{block_type} ⌛" if confirmed == "false" else block_type

    is_known_account, known_account = await account_lookup.lookup_account(account)
    account_formatted = known_account["name"] if is_known_account else format_account(
        account)

    transformed_entry = {
        "type": block_type,
        "account": account,
        "is_known_account": is_known_account,
        "known_account": known_account,
        "amount": amount,
        "timestamp": entry.get("local_timestamp"),
        "height": entry.get("height"),
        "hash": block_hash,
        "hash_formatted": block_hash_formatted,
        "time_ago": time_ago,
        "type_formatted": block_type_formatted,
        "account_formatted": account_formatted,
        "amount_formatted": format_entry_amount(amount, block_type),
        "confirmed": confirmed
    }

    return transformed_entry


async def transform_history_data(history):
    transformed_history = []
    for entry in history:
        transformed_entry = await transform_history_entry(entry)
        transformed_history.append(transformed_entry)
    return transformed_history


async def transform_account_data(data):
    history = data.get('history', [])
    history_cutoff_hash = data.get('previous', "0" * 64)

    transformed_history = await transform_history_data(history)
    grouped_history = group_and_sort_history(transformed_history)

    response = {
        "history": transformed_history,
        "grouped_history": grouped_history,
        "cutoff_hash": history_cutoff_hash
    }
    if not transformed_history:
        response["warning"] = "No transaction history is available for this account."

    return response
