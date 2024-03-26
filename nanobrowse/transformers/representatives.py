from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import format_weight, format_account, format_uptime, get_time_ago, format_version
from utils.known import AccountLookup
from utils.rpc_execution import execute_and_handle_errors
from asyncio import gather
from utils.representatives import RepsManager

rep_transformer = Blueprint('rep_transformer', __name__)
account_lookup = AccountLookup()
reps_manager = RepsManager()


@rep_transformer.route('/reps_online/', methods=['GET'])
async def get_representatives_online():

    data = reps_manager.get_online_reps()
    return jsonify(data)
