import datetime
from utils.network_params import NetworkParams


def format_error(error):
    if not error:
        return None
    error_split = str(error).split("\n")
    error_dict = {
        "header": "Error: " + error_split.pop(0) if error_split else "Error!",
        "body": "\n" + "\n".join(error_split),
    }
    return error_dict


def get_time_ago(timestamp):
    timestamp = 0 if timestamp == "" else int(timestamp)
    if timestamp == 0:
        return "Unknown"

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


def format_uptime(uptime_seconds):

    uptime_seconds = 0 if uptime_seconds == "" else int(uptime_seconds)
    if uptime_seconds == 0:
        return "Unknown"
    # Constants for time unit conversions
    MINUTE = 60
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR
    WEEK = 7 * DAY
    MONTH = 30 * DAY  # Approximation
    YEAR = 365 * DAY  # Approximation

    # Calculate the time units
    years = uptime_seconds // YEAR
    months = (uptime_seconds % YEAR) // MONTH
    weeks = (uptime_seconds % YEAR % MONTH) // WEEK
    days = (uptime_seconds % WEEK) // DAY
    hours = (uptime_seconds % DAY) // HOUR
    minutes = (uptime_seconds % HOUR) // MINUTE

    if years > 0:
        # Format as years, months, weeks
        return f"{years} years, {months} months"
    elif months > 0:
        # Format as years, months, weeks
        return f"{months} months, {weeks} weeks"
    elif weeks > 0:
        # Format as weeks, days, hours, minutes
        return f"{weeks} weeks, {days} days"
    elif days > 0:
        # If uptime is less than a week but more than a day
        return f"{days} days, {hours} hours"
    elif hours > 0:
        # If uptime is less than a day but more than an hour
        return f"{hours} hours, {minutes} minutes"
    elif minutes > 0:
        # If uptime is less than an hour but more than a minute
        return f"{minutes} minutes"
    else:
        # If uptime is less than a minute
        return "Less than a minute"


def format_version(major, minor, patch, pre_release):
    # List of version parts
    version_numbers = [major, minor, pre_release]
    # Filter out any None values
    valid_versions = [str(v) for v in version_numbers if v is not None]

    # Join the remaining parts with dots, or return a default value if empty
    return ".".join(valid_versions) if valid_versions else "Unknown"


def format_weight(value, base_weight=None, ignore_weight_below=0.01):
    show_weight = False
    base_weight = base_weight or NetworkParams.get_total_weight()
    try:
        weight = int(value) / 10**30
        weight_formatted = "Ӿ {:,.2f}".format(weight)
        weight_percent = (int(value) / int(base_weight)) * 100
        weight_percent_formatted = "{:.2f}".format(weight_percent)
        if weight_percent > ignore_weight_below:
            show_weight = True
            return (
                f"{weight_percent_formatted}% ({weight_formatted})",
                weight_percent,
                show_weight,
            )
        else:
            return "0", 0, show_weight

    except (ValueError, TypeError):
        return "0", 0, show_weight


def format_balance(value, subtype="", default="0"):
    try:
        balance = "{:,.8f}".format(int(value) / 10**30)
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
