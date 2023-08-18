import httpx
import logging
import json

logging.basicConfig(level=logging.INFO)


class AccountLookup:

    def __init__(self):
        # To store the data of all files
        # Structure: {source: {key_field: value_field, "url": url}}
        self.data_sources = {}

    # async def load_file(self, filepath_or_url, address_field, name_field, url_template=None):
    #     """
    #     Load a file or fetch from a URL and specify the fields to be used for lookup and value return.
    #     """
    #     logging.info(f"called with {filepath_or_url}")

    #     if filepath_or_url.startswith(('http://', 'https://')):
    #         # It's an URL, fetch content asynchronously
    #         async with httpx.AsyncClient() as client:
    #             response = await client.get(filepath_or_url)
    #             # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    #             response.raise_for_status()
    #             data = response.json()
    #     else:
    #         with open(filepath_or_url, 'r') as file:
    #             data = json.load(file)

    #     transformed_data = {}
    #     for entry in data:
    #         address = entry[address_field]
    #         name = entry[name_field]
    #         if url_template:
    #             # Using the entire entry to format the string
    #             url = url_template.format(**entry)
    #         else:
    #             url = None
    #         transformed_data[address] = {"name": name, "url": url}

    #         self.data_sources[filepath_or_url] = transformed_data

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

        # await self.load_file("https://raw.githubusercontent.com/fwd/nano-to/master/known.json", "address", "name", "https://nano.to/{name}")
        # await self.load_file("https://raw.githubusercontent.com/running-coder/nanolooker/master/server/cron/knownAccounts.json", "account", "alias", None)
        # await self.load_file("nanobrowse/utils/known-accounts.json", "account", "alias", None)
