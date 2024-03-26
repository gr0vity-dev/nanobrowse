from deps.rpc_client import get_nanorpc_client
from utils.formatting import format_weight, format_account, format_uptime, get_time_ago, format_version
from utils.rpc_execution import execute_and_handle_errors
from utils.known import AccountLookup
from utils.constants import REP_REFRESH_INTERVAL
import asyncio
from utils.logger import logger


class RepsManager:

    online_reps = {}  # Online Reps shared by all instances

    def __init__(self):

        self.account_lookup = AccountLookup()
        self.nanorpc = get_nanorpc_client()

    def get_online_reps(self):
        return [rep for rep in RepsManager.online_reps.values()]

    async def run(self):
        asyncio.create_task(self.background_update_task())

    async def background_update_task(self):
        while True:
            await self.refresh_representatives_online()
            await asyncio.sleep(REP_REFRESH_INTERVAL)

    async def refresh_representatives_online(self):
        data = await self.fetch_reps_online()
        transformed_data = await self.transform_reps_online_data(data)
        keys_to_ignore = ['last_telemetry_report',
                          'weight_formatted', 'weight_percent', 'node_uptime']

        for rep in transformed_data:
            existing_rep = RepsManager.online_reps.get(rep["account"], {})
            # Directly use the utility function to compare and get changed keys
            changed_keys = self._get_changed_keys(
                rep, existing_rep, keys_to_ignore)

            if changed_keys:
                if existing_rep:  # avoid logging initial rep population
                    logger.info(
                        f"Rep {rep['account']} changed {', '.join(changed_keys)}")
                RepsManager.online_reps[rep["account"]] = rep

    async def fetch_reps_online(self):
        tasks = {
            "online_reps": self.nanorpc.representatives_online(weight=True),
            "telemetry": self.nanorpc.telemetry(raw=True),
            "confirmation_quorum": self.nanorpc.confirmation_quorum(peer_details=True)
        }

        return await execute_and_handle_errors(tasks)

    def extend_telemetry_with_account(self, telemetry_peers, confirmation_quorum_peers):
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

    async def transform_reps_online_data(self, data):
        representatives = data["online_reps"].get("representatives", {})
        confirmation_quorum = data["confirmation_quorum"]
        confirmation_quorum_peers = confirmation_quorum.get("peers")
        telemetry_peers = data["telemetry"].get("metrics")

        extended_telemetry = self.extend_telemetry_with_account(
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
            is_known_account, known_account = await self.account_lookup.lookup_account(account)

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

    def _get_changed_keys(self, dict1, dict2, ignore_keys):
        changed_keys = []
        # Check for changes in dict1 compared to dict2
        for key in dict1:
            if key not in ignore_keys and dict1.get(key) != dict2.get(key):
                changed_keys.append(key)
        return changed_keys
