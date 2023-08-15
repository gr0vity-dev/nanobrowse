
import datetime

NANO_SUPPLY = 133246401824662258600496820004700378675


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


def format_weight(value):
    ignore_weight_below = 0.01  # percent
    try:
        weight = int(value) / 10 ** 30
        weight_formatted = "{:.0f} Ӿ".format(weight)
        weight_percent = (int(value) / NANO_SUPPLY) * 100
        weight_percent_formatted = "{:.2f}".format(weight_percent)
        if weight_percent > ignore_weight_below:
            return f"{weight_percent_formatted}% ({weight_formatted})", weight_percent
        else:
            return "0", 0

    except (ValueError, TypeError):
        return "0"


def format_balance(value, subtype="", default="0"):
    try:
        balance = "{:.8f}".format(int(value) / 10 ** 30)
        if subtype == "send":
            return "- " + balance
        elif subtype == "receive":
            return "+ " + balance
        elif subtype == "":
            return balance
    except (ValueError, TypeError):
        return default
