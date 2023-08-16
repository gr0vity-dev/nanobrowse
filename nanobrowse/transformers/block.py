from quart import Blueprint, jsonify, abort, make_response, jsonify
from deps.rpc_client import nanorpc
from utils.formatting import format_balance, get_time_ago
import logging

logging.basicConfig(level=logging.INFO)

block_transformer = Blueprint('block_transformer', __name__)


@block_transformer.route('/block/<hash>', methods=['GET'])
async def get_block_info(hash):
    data = await fetch_block_info([hash])

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_block_data(data.get(hash, {}), hash)
    return jsonify(transformed_data)


async def fetch_block_info(hashes):

    response = await nanorpc.blocks_info(hashes, json_block="true", source="true", receive_hash="true")
    if "error" in response:
        raise ValueError("Invalid hash")

    return response.get("blocks", {})


def safe_get(dictionary, *keys, default=None):
    for key in keys:
        try:
            dictionary = dictionary[key]
        except (TypeError, KeyError, IndexError):
            return default
    return dictionary


async def fetch_blocks_info(data, hash):
    def validate_hash(hash_value):
        # Assuming valid hashes are not empty and don't consist of only one repeated character
        return hash_value and not all(c == hash_value[0] for c in hash_value)

    receive_hash = None
    send_hash = None
    change_hash = None
    other_hash = None
    # Extract the hashes
    if safe_get(data, "subtype") == "send":
        receive_hash = safe_get(data, "receive_hash")
        send_hash = hash

    elif safe_get(data, "subtype") == "receive":
        receive_hash = hash
        send_hash = safe_get(data, "contents", "link")
    elif safe_get(data, "subtype") == "change":
        raise ValueError("Change blocks not yet supported")
        change_hash = hash
    else:
        subtype = safe_get(data, "subtype")
        raise ValueError(f"{subtype} blocks not yet supported")
        other_hash = hash

    valid_hashes = [h for h in [send_hash,
                                receive_hash, change_hash, other_hash] if validate_hash(h)]

    return await fetch_block_info(valid_hashes), send_hash, receive_hash, change_hash


def process_block_data(block_data, key):
    block = safe_get(block_data, key, default={})
    balance = format_balance(safe_get(block, "balance"))
    amount = format_balance(safe_get(block, "amount"))
    is_confirmed = safe_get(block, "confirmed") == "true"
    left_align = "left-20" if is_confirmed else "left-24"
    status = "Confirmed" if is_confirmed else "Unconfirmed"
    local_timestamp = safe_get(block, "local_timestamp", default="")
    time_ago = get_time_ago(local_timestamp)
    block_type = safe_get(block, "subtype", default="")
    representative = safe_get(block, "contents", "representative", default="")
    hash = key
    hash_exists = True if hash and hash != "0" * 64 else False

    if block_type == "send":
        account = safe_get(block, "contents", "account", default="")
        sender = safe_get(block, "contents", "account",  default="")
        receiver = safe_get(block, "contents", "link_as_account", default="")

    elif block_type == "receive":
        account = safe_get(block, "contents", "account", default="")
        sender = safe_get(block, "source_account", default="")
        receiver = safe_get(block, "contents", "account", default="")
    else:
        account = ""
        sender = ""
        receiver = ""

    return {
        "account": account,
        "sender": sender,
        "receiver": receiver,
        "representative": representative,
        "balance": balance,
        "amount": amount,
        "hash": hash,
        "hash_exists": hash_exists,
        "is_confirmed": is_confirmed,
        "local_timestamp": local_timestamp,
        "time_ago": time_ago,
        "status": status,
        "left_align": left_align
    }


async def transform_block_data(data, hash):

    blocks_info, send_hash, receive_hash, change_hash = await fetch_blocks_info(data, hash)

    logging.info(f"change_hash: {change_hash}")
    # Process block data
    send_block_data = {}
    receive_block_data = {}

    # If there's a send block, process its data
    if send_hash:
        send_block_data = process_block_data(blocks_info, send_hash)
    else:
        send_block_data = process_block_data(blocks_info, "")

    # If there's a receive block, process its data
    if receive_hash:
        receive_block_data = process_block_data(blocks_info, receive_hash)
    else:
        receive_block_data = process_block_data(blocks_info, "0"*64)

    if change_hash:
        change_block_data = process_block_data(blocks_info, change_hash)
    else:
        change_block_data = process_block_data(blocks_info, "0"*64)

    # Calculate duration
    try:
        duration = int(receive_block_data.get("local_timestamp", 0)) - \
            int(send_block_data.get("local_timestamp", 0))
        duration_formatted = str(duration) + "s" if duration > 0 else "<1s"
    except (ValueError, TypeError):
        duration = 0
        duration_formatted = ""

    # Adjusting the extraction of receiver_account

    receiver_account = send_block_data.get("receiver", "")

    result = {
        "sender_account": send_block_data.get("account", ""),
        "sender_balance": send_block_data.get("balance", ""),
        "send_block": send_block_data,
        "duration": duration,
        "duration_formatted": duration_formatted,
        "receive_block": receive_block_data,
        "receiver_account": receiver_account,
        "receiver_balance": receive_block_data.get("balance", ""),
        "is_change": True if change_hash else False,
        "change_block": change_block_data
    }

    return result
