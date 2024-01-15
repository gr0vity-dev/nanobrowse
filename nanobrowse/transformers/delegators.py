from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_weight, format_balance, format_hash, format_account
from utils.known import AccountLookup
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

    try:
        response = {}
        response["base_weight"] = await nanorpc.account_weight(account)
        # optimisation possible, return early if < 0.01% (outsource this show_weight_threshold to common module, as it's checkedin multiple places)
        # response["delegators_count"] = await nanorpc.delegators_count(account)
        response["delegators"] = await nanorpc.delegators(account, threshold="1000000000000000000000000000000000", count="1000")

        if "error" in response:
            raise ValueError("Invalid account")
    except Exception as exc:
        raise ValueError("Timeout...\nPlease try again later.")

    return response


async def transform_delegator_data(delegators, base_weight):
    transformed_delegators = []
    if not delegators or delegators == "":
        return []
    # Sort the raw delegators data to get top 50 by weight
    top_50_delegators = sorted(
        delegators.items(), key=lambda x: int(x[1]), reverse=True)[:50]

    # Transform the top 50 delegators
    for delegator, weight in top_50_delegators:
        is_known_delegator, known_delegator = account_lookup.lookup_account(
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
    if not account_lookup.data_sources:
        await account_lookup.initialize_default_sources()

    delegators = data.get('delegators', {}).get("delegators", {})
    # delegators_count = data.get('delegators_count', 0)
    base_weight = data.get('base_weight', {}).get("weight", 0)
    transformed_delegators = await transform_delegator_data(delegators, base_weight)

    response = {
        # "delegators_count": delegators_count,
        "delegators": transformed_delegators
    }

    return response
