from quart import Quart, make_response, jsonify, request, send_from_directory
from transformers import block, search, account, receivables, delegators, known
from transformers import representatives as reps, account_history as acc_hist
from utils.known import KnownAccountManager, AccountLookup
from utils.network_params import NetworkParamManager
from utils.formatting import format_error
from utils.feature_toggle import FeatureToggle
from frontend.views import frontend
import logging
from os import path

app = Quart(__name__)
logging.basicConfig(level=logging.INFO)

feature_toggle = FeatureToggle()
account_manager = KnownAccountManager()
account_lookup = AccountLookup()
network_params = NetworkParamManager()


@app.before_serving
async def startup():
    feature_toggle.log_feature_statuses()
    account_manager.register_observer(account_lookup)
    if feature_toggle.is_enabled("REFRESH_KNOWN"):
        await account_manager.run()
    await network_params.run()


@app.context_processor
def inject_feature_toggles():
    return {'ft': feature_toggle}


@app.errorhandler(ValueError)
async def handle_value_error(error):
    logging.error(str(error))
    error_dict = format_error(error)
    return await make_response(jsonify(error=error_dict), 400)


@app.route('/favicon.ico')
async def favicon():
    return await send_from_directory(path.join(app.root_path, 'static'),
                                     'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/test-error')
async def test_error():
    raise ValueError("This is a test error")

app.register_blueprint(frontend)
app.register_blueprint(account.account_transformer, url_prefix='/api')
app.register_blueprint(
    acc_hist.account_history_transformer,  url_prefix='/api')
app.register_blueprint(block.block_transformer, url_prefix='/api')
app.register_blueprint(search.search_transformer,  url_prefix='/api')
app.register_blueprint(delegators.delegators_transformer,  url_prefix='/api')
app.register_blueprint(reps.rep_transformer,  url_prefix='/api')
app.register_blueprint(receivables.receivables_transformer,  url_prefix='/api')
app.register_blueprint(known.known_transformer,  url_prefix='/api')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
