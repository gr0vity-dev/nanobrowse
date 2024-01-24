import time
import logging
import json
import aiofiles
from deps.rpc_client import nanoto

logging.basicConfig(level=logging.INFO)


class AccountLookup:

    def __init__(self):
        # To store the data of all files
        # Structure: {source: {key_field: value_field, "url": url}}
        self.data_sources = {}
        self.last_update_time = 0  # Time of the last update

    async def lookup_account(self, account):
        current_time = time.time()
        if current_time - self.last_update_time > 600:  # 10 minutes
            await self.update_known_accounts()
            self.last_update_time = current_time

        matches = [{"account": account, "name": data[account].get("name"), "url": data[account].get("url")}
                   for source, data in self.data_sources.items() if account in data]

        is_known = bool(matches)
        first_known = matches[0] if is_known else {}
        return is_known, first_known

    async def initialize_default_sources(self):
        await self.update_known_accounts()

    async def update_known_accounts(self):
        file_path = "/app/utils/known.json"
        new_accounts = await nanoto.known()  # Fetch new accounts asynchronously

        with open(file_path, 'r') as file:
            known_accounts = json.load(file)

        nano_to_section = known_accounts.get("nano_to", {})

        for account in new_accounts:
            address = account["address"]
            if address not in nano_to_section:
                nano_to_section[address] = {
                    "name": account["name"],
                    "url": f"https://nano.to/{account['name']}"
                }

        known_accounts["nano_to"] = nano_to_section

        with open(file_path, 'w') as file:
            json.dump(known_accounts, file, indent=4)

        self.data_sources = known_accounts
