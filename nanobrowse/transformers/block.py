from quart import Blueprint, jsonify, abort, make_response, jsonify
from deps.rpc_client import nanorpc
from utils.formatting import format_balance, get_time_ago, format_hash, format_account, safe_get
from utils.known import AccountLookup
import json
from utils.logger import logger

block_transformer = Blueprint('block_transformer', __name__)
account_lookup = AccountLookup()


@block_transformer.route('/block/<hash>', methods=['GET'])
async def get_block_info(hash):
    data = await fetch_block_info([hash])

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_block_data(data.get(hash, {}), hash)
    return jsonify(transformed_data)


def validate_hash(hash):
    return len(hash) == 64 and all(c in '0123456789abcdef' for c in hash.lower())


def is_valid_hash(hashes):
    return all(validate_hash(hash) for hash in hashes)


async def fetch_block_info(hashes):
    if not is_valid_hash(hashes):
        invalid_hashes = "\n".join(
            [f"{hash}" for hash in hashes if not validate_hash(hash)])
        raise ValueError(f"Invalid Blockhash! \n{invalid_hashes}")
    try:
        response = await nanorpc.blocks_info(hashes, json_block="true", source="true", receive_hash="true")
    except Exception as exc:
        raise ValueError("Timeout...\nPlease try again later.")

    if "error" in response:
        not_found_hashes = "\n".join(
            [f"{hash}" for hash in hashes])
        raise ValueError(f"Blockhash not found!\n {not_found_hashes}")

    return response.get("blocks", {})


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
        change_hash = hash
    else:
        subtype = safe_get(data, "subtype")
        if not subtype:
            legacy_type = safe_get(data, "contents", "type")
            subtype = f"legacy_{legacy_type}"
        raise ValueError(
            f"{subtype} blocks not yet supported\n {json.dumps(data, indent=2)}")
        # other_hash = hash

    valid_hashes = [h for h in [send_hash,
                                receive_hash, change_hash, other_hash] if validate_hash(h)]

    return await fetch_block_info(valid_hashes), send_hash, receive_hash, change_hash


async def process_block_data(block_data, key):
    block = safe_get(block_data, key, default={})
    block_type = safe_get(block, "subtype", default="")
    balance = format_balance(safe_get(block, "balance"), "any")
    amount = safe_get(block, "amount")
    amount_formatted = format_balance(amount, subtype=block_type)
    is_confirmed = safe_get(block, "confirmed") == "true"
    left_align = "left-20" if is_confirmed else "left-24"
    status = "Confirmed" if is_confirmed else "Unconfirmed"
    local_timestamp = safe_get(block, "local_timestamp", default="")
    time_ago = get_time_ago(local_timestamp)

    representative = safe_get(block, "contents", "representative", default="")
    previous = safe_get(block, "contents", "previous", default="")
    successor = safe_get(block, "successor", default="")
    hash = key
    hash_exists = True if hash and hash != "0" * 64 else False
    receive_type = True if block_type == "receive" else False
    is_send = True if block_type == "send" else False
    is_open = True if receive_type and previous == "0" * 64 else False
    is_receive = True if receive_type and not is_open else False
    is_change = True if block_type == "change" else False
    is_epoch = True if block_type == "epoch" else False

    if block_type == "send":
        account = safe_get(block, "contents", "account", default="")
        sender = safe_get(block, "contents", "account",  default="")
        receiver = safe_get(block, "contents", "link_as_account", default="")

    elif block_type == "receive":
        account = safe_get(block, "contents", "account", default="")
        sender = safe_get(block, "source_account", default="")
        receiver = safe_get(block, "contents", "account", default="")
    else:
        account = safe_get(block, "contents", "account", default="")
        sender = safe_get(block, "contents", "account", default="")
        receiver = safe_get(block, "contents", "account", default="")

    is_known_account, known_account = await account_lookup.lookup_account(
        account)
    is_known_sender, known_sender = await account_lookup.lookup_account(
        sender)
    is_known_receiver, known_receiver = await account_lookup.lookup_account(
        receiver)
    is_known_representative, known_representative = await account_lookup.lookup_account(
        representative)

    response = {
        "account": account,
        "account_formatted": format_account(account),
        "is_known_account": is_known_account,
        "known_account": known_account,
        "sender": sender,
        "sender_formatted": format_account(sender),
        "is_known_sender": is_known_sender,
        "known_sender": known_sender,
        "receiver": receiver,
        "receiver_formatted": format_account(receiver),
        "is_known_receiver": is_known_receiver,
        "known_receiver": known_receiver,
        "representative": representative,
        "representative_formatted": format_account(representative),
        "is_known_representative": is_known_representative,
        "known_representative": known_representative,
        "balance": balance,
        "amount": amount,
        "amount_formatted": amount_formatted,
        "hash": hash,
        "hash_formatted": format_hash(hash),
        "previous_hash": previous,
        "next_hash": successor,
        "hash_exists": hash_exists,
        "is_confirmed": is_confirmed,
        "local_timestamp": local_timestamp,
        "time_ago": time_ago,
        "is_receive": is_receive,
        "is_open": is_open,
        "is_send": is_send,
        "status": status,
        "left_align": left_align,
        "block_type": "send block" if is_send else "receive block" if is_receive else "open block" if is_open else "change block" if is_change else "epoch block" if is_epoch else ""
    }

    return response


async def transform_block_data(data, hash):
    blocks_info, send_hash, receive_hash, change_hash = await fetch_blocks_info(data, hash)

    # Process block data
    is_change = False

    # If there's a send block, process its data
    if send_hash:
        send_block_data = await process_block_data(blocks_info, send_hash)
    else:
        send_block_data = await process_block_data(blocks_info, "")

    # If there's a receive block, process its data
    if receive_hash:
        receive_block_data = await process_block_data(blocks_info, receive_hash)
    else:
        receive_block_data = await process_block_data(blocks_info, "0"*64)

    if change_hash:
        change_block_data = await process_block_data(blocks_info, change_hash)
        is_change = True
    else:
        change_block_data = await process_block_data(blocks_info, "0"*64)

    # Calculate duration
    try:
        duration = int(receive_block_data.get("local_timestamp", 0)) - \
            int(send_block_data.get("local_timestamp", 0))
        duration_formatted = str(duration) + "s" if duration > 0 else "<1s"
    except (ValueError, TypeError):
        duration = 0
        duration_formatted = ""

    result = {
        "sender_balance": send_block_data.get("balance", ""),
        "send_block": send_block_data,
        "duration": duration,
        "duration_formatted": duration_formatted,
        "receive_block": receive_block_data,
        "receiver_balance": receive_block_data.get("balance", ""),
        "change_block": change_block_data,
        "is_change": is_change,
        "send_block_json": json.dumps(blocks_info.get(send_block_data.get("hash")), indent=2),
        "receive_block_json": json.dumps(blocks_info.get(receive_block_data.get("hash")), indent=2),
        "change_block_json": json.dumps(blocks_info.get(change_block_data.get("hash")), indent=2)
    }
    return result
