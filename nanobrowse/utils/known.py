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
            await self.update_known_aliases()
            await asyncio.sleep(KNOWN_REFRESH_INTERVAL)

    async def update_known_accounts(self):
        new_accounts = []
        try:
            new_accounts = await nanoto.known()
        except Exception as e:
            logging.warn(f"nano.to known() unavailable: {e}")

        with open(KNOWN_ACCOUNTS_FILE, 'r', encoding='utf-8') as file:
            known_accounts = json.load(file)

        known_key = "nano_to"
        known_aliases = known_accounts.get(known_key, {})

        updated, update_count = self._updated_known(
            new_accounts, known_aliases)
        if updated:
            known_accounts[known_key] = known_aliases
            with open(KNOWN_ACCOUNTS_FILE, 'w', encoding='utf-8') as file:
                json.dump(known_accounts, file, indent=4)
            logging.info(
                "%s accounts updated in known.json [%s] ", update_count, known_key)

        self.data_sources = known_accounts

    def _updated_known(self, new_accounts, known_accounts):
        updated = False
        update_count = 0
        address_key = "address"
        name_key = "name"
        url_template = "https://nano.to/{name}"

        for account in new_accounts:
            address = account[address_key]
            name = account[name_key]
            if address not in known_accounts or (known_accounts[address].get("name") != name):
                # Dynamically construct the URL based on the template and available account keys
                account_info = {
                    "name": name,
                    "url":  url_template.format(**account) if url_template else None
                }
                known_accounts[address] = account_info
                updated = True
                update_count += 1

        return updated, update_count

    def _updated_aliases(self, new_accounts, known_accounts):
        updated = False
        update_count = 0

        for account in new_accounts:
            address = account["account"]
            if address not in known_accounts:
                account_info = {
                    "name": account["alias"],
                    "url": None
                }
                known_accounts[address] = account_info
                updated = True
                update_count += 1

        return updated, update_count

    async def update_known_aliases(self):
        new_accounts = []
        try:
            new_accounts = await nanoto.aliases()
        except Exception as e:
            logging.warn(f"nano.to known() unavailable: {e}")

        with open(KNOWN_ACCOUNTS_FILE, 'r', encoding='utf-8') as file:
            known_accounts = json.load(file)

        aliases_key = "aliases"
        known_aliases = known_accounts.get(aliases_key, {})

        updated, update_count = self._updated_aliases(
            new_accounts, known_aliases)
        if updated:
            known_accounts[aliases_key] = known_aliases
            with open(KNOWN_ACCOUNTS_FILE, 'w', encoding='utf-8') as file:
                json.dump(known_accounts, file, indent=4)
            logging.info(
                "%s accounts updated in known.json [%s] ", update_count, aliases_key)

        self.data_sources = known_accounts
        return update_count


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
