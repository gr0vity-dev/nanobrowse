from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_weight, format_balance, format_hash, format_account
from utils.known import AccountLookup
from utils.rpc_execution import execute_and_handle_errors
from asyncio import gather
import logging

logging.basicConfig(level=logging.INFO)

delegators_transformer = Blueprint('delegators_transformer', __name__)
account_lookup = AccountLookup()


@delegators_transformer.route('/delegators/<account>', methods=['GET'])
async def get_delegators(account):
    data = await fetch_delegators(account)

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_delegators_data(data)
    return jsonify(transformed_data)


async def fetch_delegators(account):
    tasks = {
        "base_weight": nanorpc.account_weight(account),
        "delegators": nanorpc.delegators(account, threshold=1000 * 10**30, count="1000")
    }

    return await execute_and_handle_errors(tasks)


async def transform_delegator_data(delegators, base_weight):
    transformed_delegators = []
    if not delegators or delegators == "":
        return []
    # Sort the raw delegators data to get top 50 by weight
    top_50_delegators = sorted(
        delegators.items(), key=lambda x: int(x[1]), reverse=True)[:50]

    # Transform the top 50 delegators
    for delegator, weight in top_50_delegators:
        is_known_delegator, known_delegator = await account_lookup.lookup_account(
            delegator)
        delegator_formatted = known_delegator["name"] if is_known_delegator else format_account(
            delegator)

        formatted_weight, weight_percent, show_weight = format_weight(
            weight, base_weight)

        transformed_delegators.append({
            "delegator": delegator,
            "is_known_delegator": is_known_delegator,
            "known_delegator": known_delegator,
            "delegator_formatted": delegator_formatted,
            "weight": weight,
            "weight_formatted": formatted_weight
        })

    return transformed_delegators


async def transform_delegators_data(data):
    delegators = data.get('delegators', {}).get("delegators", {})
    # delegators_count = data.get('delegators_count', 0)
    base_weight = data.get('base_weight', {}).get("weight", 0)
    transformed_delegators = await transform_delegator_data(delegators, base_weight)

    response = {
        # "delegators_count": delegators_count,
        "delegators": transformed_delegators
    }

    return response
