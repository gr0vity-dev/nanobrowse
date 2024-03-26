from quart import Blueprint, jsonify, abort, jsonify
from deps.rpc_client import nanorpc
from utils.formatting import get_time_ago, format_hash
from utils.rpc_execution import execute_and_handle_errors
from utils.known import AccountLookup
from utils.logger import logger

search_transformer = Blueprint('search_transformer', __name__)
account_lookup = AccountLookup()


@search_transformer.route('/search/known_accounts', methods=['GET'])
async def search_known_accounts():
    data = await account_lookup.get_all_known_formatted()

    if not data:
        abort(500, description="Error communicating with RPC server")

    return jsonify(data)


@search_transformer.route('/search/confirmation_history', methods=['GET'])
async def search_confirmation_history():
    data = await fetch_confirmation_history()

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = transform_confirmation_history(data)
    return jsonify(transformed_data)


async def fetch_confirmation_history():

    tasks = {
        "response": nanorpc.confirmation_history()
    }
    response = await execute_and_handle_errors(tasks)
    return response["response"]


def transform_confirmation_history(confirmations_data):
    ELECTION_COUNT = 50

    confirmations_data = confirmations_data.get(
        "confirmations", [])
    show_block_count = min(ELECTION_COUNT, len(confirmations_data))
    confirmations = []

    for i in range(0, show_block_count):
        confimration_data = confirmations_data[i]

        transformed_data = {
            "hash": confimration_data.get("hash"),
            "hash_formatted": format_hash(confimration_data.get("hash")),
            "voters": confimration_data.get("voters", 0) + " Votes",
            "conf_duration": confimration_data.get("duration", 0) + " ms",
            "time_ago": get_time_ago(int(confimration_data.get("time", 0))/1000)
        }
        confirmations.append(transformed_data)
    confirmations.reverse()
    return confirmations
