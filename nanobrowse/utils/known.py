import asyncio
import logging
import json
from utils.formatting import format_account
from utils.constants import KNOWN_ACCOUNTS_FILE, KNOWN_REFRESH_INTERVAL
from deps.rpc_client import nanoto


class KnownAccountManager:
    def __init__(self):
        self.data_sources = None

    async def get_known_accounts(self):
        return self.data_sources

    async def run(self):
        asyncio.create_task(self.background_update_task())

    async def background_update_task(self):
        while True:
            await self.update_known_accounts()
            await asyncio.sleep(KNOWN_REFRESH_INTERVAL)

    async def update_known_accounts(self):
        new_accounts = []
        try:
            new_accounts = await nanoto.known()
        except Exception as e:
            logging.warn(f"nano.to known() unavailable: {e}")

        with open(KNOWN_ACCOUNTS_FILE, 'r', encoding='utf-8') as file:
            known_accounts = json.load(file)

        if self._update_accounts(new_accounts, known_accounts):
            logging.info("Updated known.json")
            with open(KNOWN_ACCOUNTS_FILE, 'w', encoding='utf-8') as file:
                json.dump(known_accounts, file, indent=4)

        self.data_sources = known_accounts

    def _update_accounts(self, new_accounts, known_accounts):
        nano_to_key = "nano_to"
        nano_to_section = known_accounts.get(nano_to_key, {})
        updated = False

        for account in new_accounts:
            address = account["address"]
            if address not in nano_to_section:
                nano_to_section[address] = {
                    "name": account["name"],
                    "url": f"https://nano.to/{account['name']}"
                }
                updated = True

        known_accounts[nano_to_key] = nano_to_section
        return updated


class AccountLookup:
    def __init__(self):
        self.known_accounts = None

    def get_known_accounts(self):
        with open(KNOWN_ACCOUNTS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)

    async def get_all_known(self):
        known_accounts = self.get_known_accounts()
        self.known_accounts = self._aggregate_accounts(known_accounts)

        return self.known_accounts

    def _aggregate_accounts(self, known_accounts: dict):
        aggregated_accounts = []
        for key in known_accounts.keys():
            for account, details in known_accounts[key].items():
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
        known_accounts = self.get_known_accounts()

        matches = [{"account": account, "name": data[account].get("name"), "url": data[account].get("url")}
                   for source, data in known_accounts.items() if account in data]

        is_known = bool(matches)
        first_known = matches[0] if is_known else {}
        return is_known, first_known
