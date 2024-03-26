from os import getenv


KNOWN_ACCOUNTS_FILE = "/app/utils/known.json"
KNOWN_REFRESH_INTERVAL = getenv("KNOWN_REFRESH_INTERVAL") or 600  # 10 minutes
REP_REFRESH_INTERVAL = getenv("REP_REFRESH_INTERVAL") or 600  # 10 minutes
RPC_URL = getenv("RPC_URL")
AUTH_USERNAME = getenv("AUTH_USERNAME")
AUTH_PASSWORD = getenv("AUTH_PASSWORD")
NANO_TO_AUTH_KEY = getenv("NANO_TO_AUTH_KEY")  # optinal
APP_NAME = getenv("APP_NAME") or "nanobrowse.com"
APP_EMAIL = getenv("APP_EMAIL") or "iq.cc@pm.me"
