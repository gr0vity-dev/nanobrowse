from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
from utils.formatting import format_weight, format_account, format_uptime, get_time_ago, format_version
from utils.known import AccountLookup
from utils.rpc_execution import execute_and_handle_errors
from asyncio import gather

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
    tasks = {
        "online_reps": nanorpc.representatives_online(weight=True),
        "telemetry": nanorpc.telemetry(raw=True),
        "confirmation_quorum": nanorpc.confirmation_quorum(peer_details=True)
    }

    return await execute_and_handle_errors(tasks)


def extend_telemetry_with_account(telemetry_peers, confirmation_quorum_peers):
    # Prepare IP and port from telemetry data for matching
    telemetry_dict = {
        f"[{peer['address']}]:{peer['port']}": peer for peer in telemetry_peers
    }

    # Prepare IP from confirmation quorum peers for matching
    formatted_peers = {
        f"{peer['ip']}": peer["account"]
        for peer in confirmation_quorum_peers
    }

    # Create a dictionary with the account as key, merging data from both sources
    merged_data = {}
    for ip, account in formatted_peers.items():
        telemetry_info = {}
        telemetry_info["account"] = account
        telemetry_info["ip"] = ip
        if ip in telemetry_dict:
            telemetry_info.update(telemetry_dict[ip])
            # Assign the telemetry info directly to the account in the merged_data dictionary
            merged_data[account] = telemetry_info

    return merged_data


async def transform_reps_online_data(data):
    representatives = data["online_reps"].get("representatives", {})
    confirmation_quorum = data["confirmation_quorum"]
    confirmation_quorum_peers = confirmation_quorum.get("peers")
    telemetry_peers = data["telemetry"].get("metrics")

    extended_telemetry = extend_telemetry_with_account(
        telemetry_peers, confirmation_quorum_peers)

    # Ensure representatives is a dictionary
    if not isinstance(representatives, dict):
        return []  # or handle the error as appropriate for your application

    # Calculate the total weight
    total_weight = sum(int(rep.get("weight", 0))
                       for rep in representatives.values())

    # Sort representatives by weight in descending order
    sorted_reps = sorted(representatives.items(),
                         key=lambda x: int(x[1].get("weight", 0)), reverse=True)

    transformed_data = []
    for account, info in sorted_reps:
        account_weight = int(info.get("weight", 0))
        address_formatted = format_account(account)
        tac = extended_telemetry.get(account, {})  # elemetry_account_data
        node_version_telemetry = format_version(tac.get("major_version"), tac.get(
            "minor_version"), tac.get("patch_version"), tac.get("pre_release_version"))
        node_maker_telemetry = tac.get("maker")
        node_uptime = format_uptime(tac.get("uptime", 0))
        telemetry_timestamp = round(int(tac.get("timestamp", "0")) / 1000)
        last_telemetry_report = get_time_ago(telemetry_timestamp)
        node_id = tac.get("node_id")

        # Perform account lookup
        is_known_account, known_account = await account_lookup.lookup_account(account)

        # Format the weight
        formatted_weight, weight_percent, show_weight = format_weight(
            account_weight, total_weight, 0.0005)

        alias = known_account["name"] if is_known_account else address_formatted
        # Add the transformed data
        transformed_data.append({
            "account": account,
            "is_known_account": is_known_account,
            "account_formatted": alias,
            "alias": alias,  # assure compatibility with numsu vote visualizer
            "votingweight": account_weight,  # assure compatibility with numsu vote visualizer
            "weight_formatted": formatted_weight,
            "weight_percent": weight_percent,
            "show_weight": show_weight,
            "node_version": node_version_telemetry,
            "node_uptime": node_uptime,
            "node_maker": node_maker_telemetry,
            "node_id": node_id,
            "node_ip": tac.get("ip", ""),
            "last_telemetry_report": last_telemetry_report
        })

    return transformed_data
