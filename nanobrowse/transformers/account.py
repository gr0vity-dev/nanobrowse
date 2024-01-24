from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_weight, format_balance, format_hash, format_account
from utils.known import AccountLookup
import logging

logging.basicConfig(level=logging.INFO)

account_transformer = Blueprint('account_transformer', __name__)
account_lookup = AccountLookup()


@account_transformer.route('/account/<account>', methods=['GET'])
async def get_account_history(account):
    data = await fetch_account_history(account)

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_account_data(data)
    return jsonify(transformed_data)


async def fetch_account_history(account):

    try:
        response = await nanorpc.account_history(account, count="500", raw="true") or {}
        response["account_info"] = await nanorpc.account_info(account, include_confirmed="true", representative="true", receivable="true", weight="true")
        response["receivable"] = await nanorpc.receivable(account, source="true", include_only_confirmed="false", sorting="true")
       # response["delegators"] = await nanorpc.delegators(account, threshold="1000000000000000000000000000000000", count="200")

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
            grouped_history[key]['total_amount'] = int(entry['amount'])
            # Initialize transaction count
            grouped_history[key]['transaction_count'] = 1
        else:
            grouped_history[key]['total_amount'] += int(entry['amount'])
            # Increment transaction count
            grouped_history[key]['transaction_count'] += 1
            # Update 'time_ago' to the most recent time
            if entry['timestamp'] > grouped_history[key]['timestamp']:
                grouped_history[key]['time_ago'] = entry['time_ago']
                grouped_history[key]['timestamp'] = entry['timestamp']

    # Sort the grouped history by type and account in ascending order
    sorted_grouped_history = sorted(
        grouped_history.values(), key=lambda x: (x['type'], x['total_amount']), reverse=True)

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
        type = entry.get("subtype")

        amount = entry.get("amount")
        if type == "change":
            amount_formatted = "new rep"
        else:
            amount_formatted = format_balance(amount, type)

        is_known_account, known_account = await account_lookup.lookup_account(
            account)
        account_formatted = known_account["name"] if is_known_account else format_account(
            account)

        transformed_history.append({
            "type": type,
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


async def transform_delegator_data(delegators):
    transformed_delegators = []
    # Sort the raw delegators data to get top 50 by weight
    top_50_delegators = sorted(delegators["delegators"].items(
    ), key=lambda x: int(x[1]), reverse=True)[:50]

    # Transform the top 50 delegators
    for delegator, weight in top_50_delegators:
        is_known_delegator, known_delegator = await account_lookup.lookup_account(
            delegator)
        delegator_formatted = known_delegator["name"] if is_known_delegator else format_account(
            delegator)

        formatted_weight, weight_percent, show_weight = format_weight(weight)

        transformed_delegators.append({
            "delegator": delegator,
            "is_known_delegator": is_known_delegator,
            "known_delegator": known_delegator,
            "delegator_formatted": delegator_formatted,
            "weight": weight,
            "weight_formatted": formatted_weight
        })

    return transformed_delegators


async def transform_receivable_data(blocks):

    if not blocks or len(blocks) == 0:
        return []
    transformed_blocks = []
    trimmed_blocks = list(blocks.items())[:50]

    # Transform the block data
    for block_hash, block_data in trimmed_blocks:
        amount = block_data.get("amount")
        source = block_data.get("source")

        amount_formatted = format_balance(amount, "any")
        is_known_source, known_source = await account_lookup.lookup_account(source)
        source_formatted = known_source["name"] if is_known_source else format_account(
            source)
        hash_formatted = format_hash(block_hash)

        transformed_blocks.append({
            "hash": block_hash,
            "hash_formatted": hash_formatted,
            "amount": amount,
            "amount_formatted": amount_formatted,
            "source": source,
            "is_known_source": is_known_source,
            "known_source": known_source,
            "source_formatted": source_formatted
        })

    return transformed_blocks


async def transform_account_data(data):
    if not account_lookup.data_sources:
        await account_lookup.initialize_default_sources()

    history = data.get('history', [])
    # delegators = data.get('delegators', {})
    account_info = data.get('account_info', {})
    account_receivable = data.get("receivable", {})

    transformed_history = await transform_history_data(history)
    grouped_history = group_and_sort_history(transformed_history)
    transformed_receivable = await transform_receivable_data(account_receivable["blocks"])
    # transformed_delegators = await transform_delegator_data(delegators)

    receivable = account_info.get("receivable", 0)
    receivable_formatted = format_balance(receivable, "any")
    show_receivable = True if int(receivable) > 0 else False
    receivable_count = len(
        account_receivable["blocks"]) if account_receivable and "blocks" in account_receivable else 0

    formatted_weight, weight_percent, show_weight = format_weight(
        account_info.get("weight"))
    main_account = data.get("account")
    representative = account_info.get("representative")
    is_known_account, known_account = await account_lookup.lookup_account(
        main_account)
    is_known_representative, known_representative = await account_lookup.lookup_account(
        representative)

    representative_formatted = known_representative["name"] if is_known_representative else format_account(
        representative)
    account_formatted = known_account["name"] if is_known_account else format_account(
        main_account)

    response = {
        "account": main_account,
        "account_formatted": account_formatted,
        "is_known_account": is_known_account,
        "known_account": known_account,
        "confirmed_balance": format_balance(account_info.get("confirmed_balance", 0), "any"),
        "show_receivable": show_receivable,
        "receivable": receivable,
        "receivables": transformed_receivable,
        "receivable_formatted": receivable_formatted,
        "receivable_count": receivable_count,
        "block_count": account_info.get("block_count", 0),
        "confirmed_blocks": account_info.get("confirmed_height", 0),
        "unconfirmed_blocks": int(account_info.get("block_count", 0)) - int(account_info.get("confirmed_height", 0)),
        "frontier": account_info.get("confirmed_frontier"),
        "frontier_formatted": format_hash(account_info.get("confirmed_frontier")),
        "open_block": account_info.get("open_block"),
        "open_block_formatted": format_hash(account_info.get("open_block")),
        "representative": representative,
        "representative_formatted": representative_formatted,
        "is_known_representative": is_known_representative,
        "known_representative": known_representative,
        "history": transformed_history[:50],
        "grouped_history": grouped_history,
        # "delegators": transformed_delegators,
        "previous": data.get("previous"),
        "weight": account_info.get("weight"),
        "weight_percent": weight_percent,
        "weight_formatted": formatted_weight,
    }

    response["show_receivable"] = True if int(
        response["receivable"]) > 0 else False
    response["show_unconfirmed_count"] = True if int(
        response["unconfirmed_blocks"]) > 0 else False
    response["show_weight"] = show_weight
    response["is_pr"] = True if response["show_weight"] and weight_percent > 0.1 else False

    return response
