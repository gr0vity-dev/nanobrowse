from quart import Quart, make_response, jsonify, request
from transformers import account_transformer, block_transformer
from frontend.views import frontend
import logging

app = Quart(__name__)
logging.basicConfig(level=logging.INFO)


@app.errorhandler(ValueError)
async def handle_value_error(error):
    logging.error("Handling ValueError")
    return await make_response(jsonify({"error": str(error)}), 400)


@app.route('/test-error')
async def test_error():
    raise ValueError("This is a test error")

app.register_blueprint(
    account_transformer.account_transformer, url_prefix='/api')
app.register_blueprint(block_transformer.block_transformer, url_prefix='/api')
app.register_blueprint(frontend)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
