from quart import Blueprint, jsonify, request, abort
from deps.rpc_client import nanorpc
import datetime

account_transformer = Blueprint('account_transformer', __name__)
NANO_SUPPLY = 133246401824662258600496820004700378675


@account_transformer.route('/account/<account>', methods=['GET'])
async def get_account_history(account):
    data = await fetch_account_history(account)

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = transform_account_data(data)
    return jsonify(transformed_data)


async def fetch_account_history(account):

    response = await nanorpc.account_history(account, count="25") or {}
    response["account_info"] = await nanorpc.account_info(account, include_confirmed="true", representative="true", pending="true", weight="true")

    if "error" in response:
        raise ValueError("Invalid hash")

    return response


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


def transform_account_data(data):
    history = data.get('history', [])
    account_info = data.get('account_info', {})
    transformed_history = []
    for entry in history:
        time_ago = get_time_ago(int(entry.get("local_timestamp")))
        transformed_history.append({
            "type": entry.get("type"),
            "account": entry.get("account"),
            "amount": format_balance(entry.get("amount"), entry.get("type")),
            "timestamp": entry.get("local_timestamp"),
            "height": entry.get("height"),
            "hash": entry.get("hash"),
            "confirmed": entry.get("confirmed"),
            "time_ago": time_ago
        })

    formatted_weight, weight_percent = format_weight(
        account_info.get("weight"))
    response = {
        "account": data.get("account"),
        "confirmed_balance": format_balance(account_info.get("confirmed_balance", 0)),
        "receivable": account_info.get("receivable", 0),
        "block_count": account_info.get("block_count", 0),
        "confirmed_blocks": account_info.get("confirmed_height", 0),
        "unconfirmed_blocks": int(account_info.get("block_count", 0)) - int(account_info.get("confirmed_height", 0)),
        "frontier": account_info.get("confirmed_frontier"),
        "open_block": account_info.get("open_block"),
        "representative": account_info.get("representative"),
        "history": transformed_history,
        "previous": data.get("previous"),
        "weight": account_info.get("weight"),
        "weight_percent": weight_percent,
        "weight_formatted": formatted_weight,
    }

    response["show_receivable"] = True if int(
        response["receivable"]) > 0 else False
    response["show_unconfirmed_count"] = True if int(
        response["unconfirmed_blocks"]) > 0 else False
    response["show_weight"] = True if response["weight"] != "0" else False
    response["is_pr"] = True if response["show_weight"] and weight_percent > 0.1 else False

    return response


def get_time_ago(timestamp):
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
