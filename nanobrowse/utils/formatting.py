
import datetime
from utils.network_params import NetworkParamManager

NETWORK_PARAMS = NetworkParamManager().get_params()
NANO_SUPPLY = NETWORK_PARAMS.available_supply


def get_time_ago(timestamp):
    timestamp = 0 if timestamp == "" else int(timestamp)
    current_time = datetime.datetime.now().timestamp()
    diff = current_time - timestamp

    if diff < 60:
        return f"{int(diff)} seconds ago"
    elif diff < 3600:  # Less than an hour
        minutes = int(diff // 60)
        return f"{minutes} minute(s) ago"
    elif diff < 86400:  # Less than a day
        hours = int(diff // 3600)
        return f"{hours} hour(s) ago"
    elif diff < 604800:  # Less than a week
        days = int(diff // 86400)
        return f"{days} day(s) ago"
    elif diff < 2629800:  # Approx. 30.44 days a month on average, so less than a month
        weeks = int(diff // 604800)
        return f"{weeks} weeks ago"
    elif diff < 31557600:  # Approx. 365.25 days a year, accounting for leap years
        months = int(diff // 2629800)
        return f"{months} month(s) ago"
    else:  # More than a year
        years = int(diff // 31557600)
        return f"{years} year(s) ago"


def format_weight(value, base_weight=None, ignore_weight_below=0.01):
    show_weight = False
    base_weight = base_weight or NANO_SUPPLY
    try:
        weight = int(value) / 10 ** 30
        weight_formatted = "Ӿ {:,.2f}".format(weight)
        weight_percent = (int(value) / int(base_weight)) * 100
        weight_percent_formatted = "{:.2f}".format(weight_percent)
        if weight_percent > ignore_weight_below:
            show_weight = True
            return f"{weight_percent_formatted}% ({weight_formatted})", weight_percent, show_weight
        else:
            return "0", 0, show_weight

    except (ValueError, TypeError):
        return "0", 0, show_weight


def format_balance(value, subtype="", default="0"):
    try:
        balance = "{:,.8f}".format(int(value) / 10 ** 30)
        if subtype == "send":
            return "-Ӿ " + balance
        elif subtype == "receive":
            return "+Ӿ " + balance
        elif subtype == "change":
            return "Ӿ " + balance
        elif subtype == "any":
            return "Ӿ " + balance
        else:
            return "Ӿ 0"
    except (ValueError, TypeError):
        return default


def format_account(account_str: str) -> str:

    if not account_str:
        return account_str
    # Split the hash on "_"
    parts = account_str.split("_", 1)

    # If there's only one part or the second part is less than 11 characters, return as is
    if len(parts) != 2 or len(parts[1]) < 11:
        return account_str

    # Return the formatted string with the first 7 characters after "_" and the last 4 characters
    return f"{parts[0]}_{parts[1][:7]}...{parts[1][-4:]}"


def format_hash(block_str: str) -> str:
    if not block_str:
        return block_str

    # If the block string is less than 10 characters, return as is
    if len(block_str) < 15:
        return block_str

    # Return the first 10 characters followed by "..."
    return f"{block_str[:15]}..."


def safe_get(dictionary, *keys, default=None):
    for key in keys:
        try:
            dictionary = dictionary[key]
        except (TypeError, KeyError, IndexError):
            return default
    return dictionary
