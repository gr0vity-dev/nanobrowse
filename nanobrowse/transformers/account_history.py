from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_weight, format_balance, format_hash, format_account
from utils.known import AccountLookup
import logging

logging.basicConfig(level=logging.INFO)

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

    try:
        response = await nanorpc.account_history(account, count=HISTORY_COUNT, raw="true") or {}

        if "error" in response:
            raise ValueError("Invalid account")
    except Exception as exc:
        raise ValueError("Timeout...\nPlease try again later.")

    return response


def group_and_sort_history(transformed_history):
    grouped_history = {}
    for entry in transformed_history:
        key = (entry['type'], entry['account'])
        if key not in grouped_history:
            # Create a new entry for the group
            grouped_history[key] = entry.copy()
            grouped_history[key]['total_amount'] = int(entry['amount'] or 0)
            # Initialize transaction count
            grouped_history[key]['transaction_count'] = 1
        else:
            grouped_history[key]['total_amount'] += int(entry['amount'] or 0)
            # Increment transaction count
            grouped_history[key]['transaction_count'] += 1
            # Update 'time_ago' to the most recent time
            if entry['timestamp'] > grouped_history[key]['timestamp']:
                grouped_history[key]['time_ago'] = entry['time_ago']
                grouped_history[key]['timestamp'] = entry['timestamp']

    # Sort the grouped history by type and account in ascending order
    sorted_grouped_history = sorted(
        grouped_history.values(),
        key=lambda x: (
            x['total_amount'] if x['total_amount'] is not None else 0
        ),
        reverse=True
    )

    # Format the final output
    for entry in sorted_grouped_history:
        entry['amount_formatted'] = format_balance(
            str(entry['total_amount']), entry['type'])
        # Remove individual entry fields that are not needed in grouped view
        entry.pop('amount', None)
        entry.pop('hash', None)
        entry.pop('height', None)

    return sorted_grouped_history


async def transform_history_data(history):

    transformed_history = []
    for entry in history:
        time_ago = get_time_ago(entry.get("local_timestamp"))
        account = entry.get("account") or entry.get("representative")
        confirmed = entry.get("confirmed")
        block_type = entry.get("subtype")

        block_type_formatted = block_type
        if confirmed == "false":
            block_type_formatted = block_type + " ⌛"

        amount = entry.get("amount")
        if block_type == "change":
            amount_formatted = "new rep"
        else:
            amount_formatted = format_balance(amount, block_type)

        is_known_account, known_account = await account_lookup.lookup_account(
            account)
        account_formatted = known_account["name"] if is_known_account else format_account(
            account)

        transformed_history.append({
            "type": block_type,
            "type_formatted": block_type_formatted,
            "account": account,
            "is_known_account": is_known_account,
            "known_account": known_account,
            "account_formatted": account_formatted,
            "amount": amount,
            "amount_formatted": amount_formatted,
            "timestamp": entry.get("local_timestamp"),
            "height": entry.get("height"),
            "hash": entry.get("hash"),
            "hash_formatted": format_hash(entry.get("hash")),
            "confirmed": entry.get("confirmed"),
            "time_ago": time_ago
        })
    return transformed_history


async def transform_account_data(data):
    history = data.get('history', [])
    history_cutoff_hash = data.get('previous', "0" * 64)

    transformed_history = await transform_history_data(history)
    grouped_history = group_and_sort_history(transformed_history)

    response = {
        "history": transformed_history[:50],
        "grouped_history": grouped_history,
        "cutoff_hash": history_cutoff_hash
    }

    return response
