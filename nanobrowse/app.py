from quart import Quart, make_response, jsonify, request
from transformers import block, search, account, delegators, representatives as reps
from utils.known import KnownAccountManager
from frontend.views import frontend
import logging

app = Quart(__name__)
logging.basicConfig(level=logging.INFO)

account_manager = KnownAccountManager()


@app.before_serving
async def startup():
    await account_manager.run()


@app.errorhandler(ValueError)
async def handle_value_error(error):
    logging.error("Handling ValueError")
    error_split = str(error).split("\n")

    error_dict = {
        "header": "Error: " + error_split.pop(0) if error_split else "Error!",
        "body": "\n" + "\n".join(error_split)
    }
    logging.info(error_dict["header"])
    return await make_response(jsonify(error=error_dict), 400)


@app.route('/test-error')
async def test_error():
    raise ValueError("This is a test error")

app.register_blueprint(frontend)
app.register_blueprint(account.account_transformer, url_prefix='/api')
app.register_blueprint(block.block_transformer, url_prefix='/api')
app.register_blueprint(search.search_transformer,  url_prefix='/api')
app.register_blueprint(delegators.delegators_transformer,  url_prefix='/api')
app.register_blueprint(reps.rep_transformer,  url_prefix='/api')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
