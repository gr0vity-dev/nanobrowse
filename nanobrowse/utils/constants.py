from os import getenv


KNOWN_ACCOUNTS_FILE = "/app/utils/known.json"
KNOWN_REFRESH_INTERVAL = getenv("KNOWN_REFRESH_INTERVAL") or 600  # 10 minutes
