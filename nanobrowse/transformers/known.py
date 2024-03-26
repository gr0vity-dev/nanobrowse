from quart import Blueprint, jsonify, abort
from utils.known import KnownAccountManager
from utils.logger import logger

known_transformer = Blueprint('known_transformer', __name__)
account_manager = KnownAccountManager()


@known_transformer.route('/update_aliases', methods=['GET'])
async def update_aliases():
    update_kount = await account_manager.update_known_aliases()
    logger.info(
        f"Manual alias update. {update_kount} updated aliases")
    return jsonify({"success": "true", "msg": f"{update_kount} aliases updated"})
