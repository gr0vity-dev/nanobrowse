# account_lookup.py

import logging
import time
import json
from utils.formatting import format_account
from utils.constants import KNOWN_ACCOUNTS_FILE, UPDATE_KNOW_INTERVAL
from deps.rpc_client import nanoto


class KnownAccountManager:
    def __init__(self):
        self.data_sources = {}
        self.last_update_time = 0
        self.data_sources_changes = False

    async def update_known_accounts(self):
        current_time = time.time()
        if current_time - self.last_update_time < UPDATE_KNOW_INTERVAL:
            return

        self.last_update_time = current_time
        self.data_sources_changes = False

        new_accounts = []
        try:
            new_accounts = await nanoto.known()
        except Exception as e:
            logging.warn(f"nano.to known() unavailable: {e}")

        with open(KNOWN_ACCOUNTS_FILE, 'r', encoding='utf-8') as file:
            known_accounts = json.load(file)

        self._update_accounts(new_accounts, known_accounts)

        if self.data_sources_changes:
            logging.info("Updated known.json")
            with open(KNOWN_ACCOUNTS_FILE, 'w', encoding='utf-8') as file:
                json.dump(known_accounts, file, indent=4)

        self.data_sources = known_accounts

    def _update_accounts(self, new_accounts, known_accounts):
        nano_to_key = "nano_to"
        nano_to_section = known_accounts.get(nano_to_key, {})

        for account in new_accounts:
            address = account["address"]
            if address not in nano_to_section:
                nano_to_section[address] = {
                    "name": account["name"],
                    "url": f"https://nano.to/{account['name']}"
                }
                self.data_sources_changes = True

        known_accounts[nano_to_key] = nano_to_section


class AccountLookup:
    def __init__(self):
        self.data_manager = KnownAccountManager()
        self.known_accounts = None

    async def get_all_known(self):
        await self.data_manager.update_known_accounts()

        if not self.known_accounts or self.data_manager.data_sources_changes:
            self.known_accounts = self._aggregate_accounts()

        return self.known_accounts

    def _aggregate_accounts(self):
        aggregated_accounts = []
        for key in self.data_manager.data_sources.keys():
            for account, details in self.data_manager.data_sources[key].items():
                entry = {
                    "source": key,
                    "account": account,
                    "account_formatted": format_account(account),
                    "name": details["name"],
                    "url": details.get("url"),
                    "has_url": details.get("url") is not None
                }
                aggregated_accounts.append(entry)
        return aggregated_accounts

    async def lookup_account(self, account):
        await self.data_manager.update_known_accounts()

        matches = [{"account": account, "name": data[account].get("name"), "url": data[account].get("url")}
                   for source, data in self.data_manager.data_sources.items() if account in data]

        is_known = bool(matches)
        first_known = matches[0] if is_known else {}
        return is_known, first_known
