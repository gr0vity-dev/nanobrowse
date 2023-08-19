import httpx
import logging
import json

logging.basicConfig(level=logging.INFO)


class AccountLookup:

    def __init__(self):
        # To store the data of all files
        # Structure: {source: {key_field: value_field, "url": url}}
        self.data_sources = {}

    def lookup_account(self, account):
        """
        Lookup an account across all loaded files.
        Returns a list of (account, source, url) tuples.
        """
        matches = [{"account": account, "name": data[account].get("name"), "url":data[account].get("url")}
                   for source, data in self.data_sources.items() if account in data]

        is_known = True if matches else False
        first_known = matches[0] if is_known else {}
        return is_known, first_known

    async def initialize_default_sources(self):
        with open("/app/utils/known.json", 'r') as file:
            self.data_sources = json.load(file)
