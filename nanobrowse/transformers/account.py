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
        response = await nanorpc.account_history(account, count="25", raw="true") or {}
        response["account_info"] = await nanorpc.account_info(account, include_confirmed="true", representative="true", receivable="true", weight="true")
    
        if "error" in response:
            raise ValueError("Invalid account")
    except Exception as exc:
        raise ValueError("Timeout...\nPlease try again later.")
        
           
    return response


async def transform_account_data(data):
    if not account_lookup.data_sources:
        await account_lookup.initialize_default_sources()

    history = data.get('history', [])
    account_info = data.get('account_info', {})
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

        is_known_account, known_account = account_lookup.lookup_account(
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

    formatted_weight, weight_percent, show_weight = format_weight(
        account_info.get("weight"))
    main_account = data.get("account")
    representative = account_info.get("representative")
    is_known_account, known_account = account_lookup.lookup_account(
        main_account)
    is_known_representative, known_representative = account_lookup.lookup_account(
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
        "receivable": account_info.get("receivable", 0),
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
        "history": transformed_history,
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
