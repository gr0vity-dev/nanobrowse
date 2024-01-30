from quart import Blueprint, jsonify, abort
from deps.rpc_client import nanorpc
from utils.formatting import format_balance, format_hash, format_account
from utils.known import AccountLookup
import logging

logging.basicConfig(level=logging.INFO)

receivables_transformer = Blueprint('receivables_transformer', __name__)
account_lookup = AccountLookup()


@receivables_transformer.route('/receivables/<account>', methods=['GET'])
async def get_receivables(account):
    data = await fetch_receivables(account)

    if not data:
        abort(500, description="Error communicating with RPC server")

    transformed_data = await transform_data(data)
    return jsonify(transformed_data)


async def fetch_receivables(account):

    try:
        response = {}
        response["receivable"] = await nanorpc.receivable(account, source="true", include_only_confirmed="false", sorting="true")

        if "error" in response:
            raise ValueError("Invalid account")
    except Exception as exc:
        logging.error(str(exc))
        raise ValueError("Timeout...\nPlease try again later.")

    return response


async def transform_data(data):

    account_receivable = data.get("receivable", {})
    receivable_count = len(
        account_receivable["blocks"]) if account_receivable and "blocks" in account_receivable else 0
    transformed_receivable = await transform_receivable_data(account_receivable["blocks"])

    response = {
        "receivables": transformed_receivable,
        "receivable_count": receivable_count,
    }
    return response


async def transform_receivable_data(blocks):

    if not blocks or len(blocks) == 0:
        return []
    transformed_blocks = []
    trimmed_blocks = list(blocks.items())[:50]

    # Transform the block data
    for block_hash, block_data in trimmed_blocks:
        amount = block_data.get("amount")
        source = block_data.get("source")

        amount_formatted = format_balance(amount, "any")
        is_known_source, known_source = await account_lookup.lookup_account(source)
        source_formatted = known_source["name"] if is_known_source else format_account(
            source)
        hash_formatted = format_hash(block_hash)

        transformed_blocks.append({
            "hash": block_hash,
            "hash_formatted": hash_formatted,
            "amount": amount,
            "amount_formatted": amount_formatted,
            "source": source,
            "is_known_source": is_known_source,
            "known_source": known_source,
            "source_formatted": source_formatted
        })

    return transformed_blocks
