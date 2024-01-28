import time
import logging
import json
from deps.rpc_client import nanoto
from utils.formatting import format_account

logging.basicConfig(level=logging.INFO)


class AccountLookup:

    def __init__(self):
        # To store the data of all files
        # Structure: {source: {key_field: value_field, "url": url}}
        self.data_sources = {}
        self.last_update_time = 0  # Time of the last update
        self.data_sources_changes = False
        self.known_accounts = None

    async def get_all_known(self):
        await self.update_known_accounts()

        if not self.known_accounts or self.data_sources_changes:
            self.known_accounts = []
            for key in self.data_sources.keys():
                for account, details in self.data_sources[key].items():
                    entry = {
                        "source": key,
                        "account": account,
                        "account_formatted": format_account(account),
                        "name": details["name"],
                        "url": details.get("url"),
                        "has_url": details.get("url") is not None
                    }
                    self.known_accounts.append(entry)
        return self.known_accounts

    async def lookup_account(self, account):
        await self.update_known_accounts()

        matches = [{"account": account, "name": data[account].get("name"), "url": data[account].get("url")}
                   for source, data in self.data_sources.items() if account in data]

        is_known = bool(matches)
        first_known = matches[0] if is_known else {}
        logging.info(f"Known lookup {first_known} {is_known}")
        return is_known, first_known

    async def initialize_default_sources(self):
        await self.update_known_accounts()

    async def update_known_accounts(self):
        current_time = time.time()
        self.data_sources_changes = False
        if current_time - self.last_update_time < 600:  # 10 minutes
            return

        self.last_update_time = current_time
        file_path = "/app/utils/known.json"

        new_accounts = []
        try:
            new_accounts = await nanoto.known()
        except:
            logging.warn("nano.to known() unavailable")

        with open(file_path, 'r') as file:
            known_accounts = json.load(file)
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

        if self.data_sources_changes:
            logging.info("Updated known.json")
            known_accounts[nano_to_key] = nano_to_section

            with open(file_path, 'w') as file:
                json.dump(known_accounts, file, indent=4)

        self.data_sources = known_accounts
