from quart import Blueprint, render_template
import httpx  # Instead of 'requests'

frontend = Blueprint('frontend', __name__,
                     template_folder='../templates', static_folder='../static')


@frontend.route('/')
async def index(error=None):
    async with httpx.AsyncClient() as client:
        recent_blocks_resp = await client.get(f'http://127.0.0.1:5000/api/search/confirmation_history')
        reps_online_resp = await client.get('http://127.0.0.1:5000/api/reps_online/')

    recent_blocks = recent_blocks_resp.json()
    reps_online = reps_online_resp.json()
    return await render_template("search.html", reps_online=reps_online, recent_blocks=recent_blocks, error=error)


@frontend.route('/block/', defaults={'blockhash': None}, methods=["GET"])
@frontend.route('/block/<blockhash>', methods=["GET"])
async def block_viewer(blockhash):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://127.0.0.1:5000/api/block/{blockhash}')

    if response.status_code != 200:
        error_data = response.json()
        return await index(error_data["error"])

    block_data = response.json()
    return await render_template("block_viewer.html", block_data=block_data)


@frontend.route('/account/', defaults={'account': None}, methods=["GET"])
@frontend.route('/account/<account>', methods=["GET"])
async def account_viewer(account):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'http://127.0.0.1:5000/api/account/{account}')

    if response.status_code != 200:
        error_data = response.json()
        return await index(error_data["error"])

    account_data = response.json()
    return await render_template("account_viewer.html", account_data=account_data)


@frontend.route('/account_history/', defaults={'account': None}, methods=["GET"])
@frontend.route('/account_history/<account>', methods=["GET"])
async def account_history_viewer(account):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'http://127.0.0.1:5000/api/account_history/{account}')

    if response.status_code != 200:
        error_data = response.json()
        return await index(error_data["error"])

    account_history = response.json()
    return await render_template("account_viewer/history_table.html", account_history=account_history)


@frontend.route('/delegators/', defaults={'account': None}, methods=["GET"])
@frontend.route('/delegators/<account>', methods=["GET"])
async def delegators(account):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'http://127.0.0.1:5000/api/delegators/{account}')

    if response.status_code != 200:
        error_data = response.json()
        return await index(error_data["error"])

    delegators = response.json()
    return await render_template("account_viewer/delegators_table.html", delegators=delegators)


@frontend.route('/receivables/', defaults={'account': None}, methods=["GET"])
@frontend.route('/receivables/<account>', methods=["GET"])
async def receivables(account):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'http://127.0.0.1:5000/api/receivables/{account}')

    if response.status_code != 200:
        error_data = response.json()
        return await index(error_data["error"])

    receivables = response.json()
    return await render_template("account_viewer/receivable_table.html", receivables=receivables)


@frontend.route('/confirmation_history/', methods=["GET"])
async def confirmation_history():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:5000/api/search/confirmation_history')

    if response.status_code != 200:
        error_data = response.json()
        return await index(error_data["error"])

    recent_blocks = response.json()
    return await render_template("search/confirmation_history.html", recent_blocks=recent_blocks)
