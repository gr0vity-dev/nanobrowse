from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_weight, format_balance, format_hash, format_account
from utils.rpc_execution import execute_and_handle_errors
from utils.known import AccountLookup
import logging

logging.basicConfig(level=logging.INFO)

account_transformer = Blueprint('account_transformer', __name__)
account_lookup = AccountLookup()


@account_transformer.route('/account/<account>', methods=['GET'])
async def get_account_info(account):
    data = await fetch_account_info(account)

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_account_data(data)
    return jsonify(transformed_data)


async def fetch_account_info(account):

    tasks = {
        "account_info": nanorpc.account_info(account, include_confirmed="true", representative="true", receivable="true", weight="true")
    }
    response = await execute_and_handle_errors(tasks)
    response["account"] = account

    return response


async def transform_account_data(data):
    account_info = data.get('account_info', {})
    main_account = data.get("account")

    receivable = account_info.get("receivable", 0)
    receivable_formatted = format_balance(receivable, "any")
    show_receivable = True if int(receivable) > 0 else False

    formatted_weight, weight_percent, show_weight = format_weight(
        account_info.get("weight"))

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
        "receivable_formatted": receivable_formatted,
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
