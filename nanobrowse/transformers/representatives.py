from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import format_weight, format_account
from utils.known import AccountLookup
import logging

logging.basicConfig(level=logging.INFO)

rep_transformer = Blueprint('rep_transformer', __name__)
account_lookup = AccountLookup()


@rep_transformer.route('/reps_online/', methods=['GET'])
async def get_representatives_online():

    data = await fetch_reps_online()

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_reps_online_data(data)
    return jsonify(transformed_data)


async def fetch_reps_online():
    try:
        response = await nanorpc.representatives_online(weight=True)

        if "error" in response:
            raise ValueError("Unexpected error ")
    except Exception as exc:
        raise ValueError("Timeout...\nPlease try again later.")

    return response


async def transform_reps_online_data(data):
    representatives = data["representatives"]

    # Calculate the total weight
    total_weight = sum(int(rep["weight"]) for rep in representatives.values())

    # Sort representatives by weight in descending order
    sorted_reps = sorted(representatives.items(),
                         key=lambda x: int(x[1]["weight"]), reverse=True)

    transformed_data = []
    for account, info in sorted_reps:
        account_weight = int(info["weight"])
        address_formatted = format_account(account)

        # Perform account lookup
        is_known_account, known_account = await account_lookup.lookup_account(
            account)

        # Format the weight
        formatted_weight, weight_percent, show_weight = format_weight(
            account_weight, total_weight, 0.0005)

        # Add the transformed data
        transformed_data.append({
            "account": account,
            "is_known_account": is_known_account,
            "account_formatted": known_account["name"] if is_known_account else address_formatted,
            "weight_raw": account_weight,
            "weight_formatted": formatted_weight,
            "weight_percent": weight_percent,
            "show_weight": show_weight
        })

    return transformed_data
