from quart import Blueprint, render_template, request
import httpx  # Instead of 'requests'

frontend = Blueprint('frontend', __name__,
                     template_folder='../templates', static_folder='../static')


@frontend.route('/')
async def index():
    async with httpx.AsyncClient() as client:
        recent_blocks_resp = await client.get(f'http://127.0.0.1:5000/api/search/confirmation_history')
        reps_online_resp = await client.get(f'http://127.0.0.1:5000/api/reps_online/')
        known_accounts_resp = await client.get(f'http://127.0.0.1:5000/api/search/known_accounts')

    recent_blocks = recent_blocks_resp.json()
    reps_online = reps_online_resp.json()
    known_accounts = known_accounts_resp.json()
    return await render_template("search.html", recent_blocks=recent_blocks, reps_online=reps_online, known_accounts=known_accounts)


@frontend.route('/block/', defaults={'blockhash': None}, methods=["GET"])
@frontend.route('/block/<blockhash>', methods=["GET"])
async def block_viewer(blockhash):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://127.0.0.1:5000/api/block/{blockhash}')

    if response.status_code != 200:
        error_data = response.json()
        # Decide how you want to handle the error, maybe render an error template
        return await render_template("search.html", error=error_data["error"])

    block_data = response.json()
    return await render_template("block_viewer.html", block_data=block_data)


@frontend.route('/account/', defaults={'account': None}, methods=["GET"])
@frontend.route('/account/<account>', methods=["GET"])
async def account_viewer(account):
    async with httpx.AsyncClient() as client:
        response = await client.get(f'http://127.0.0.1:5000/api/account/{account}')

    if response.status_code != 200:
        error_data = response.json()
        # Decide how you want to handle the error, maybe render an error template
        return await render_template("search.html", error=error_data["error"])

    account_data = response.json()
    return await render_template("account_viewer.html", account_data=account_data)


@frontend.route('/delegators/', defaults={'account': None}, methods=["GET"])
@frontend.route('/delegators/<account>', methods=["GET"])
async def delegators(account):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'http://127.0.0.1:5000/api/delegators/{account}')

    if response.status_code != 200:
        error_data = response.json()
        # Decide how you want to handle the error, maybe render an error template
        return await render_template("search.html", error=error_data["error"])

    account_data = response.json()
    return await render_template("account_viewer/delegators_table.html", account_data=account_data)


# @frontend.route('/reps_online/', methods=["GET"])
# async def reps_online():
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         response = await client.get(f'http://127.0.0.1:5000/api/reps_online/')

#     if response.status_code == 400:
#         error_data = response.json()
#         # Decide how you want to handle the error, maybe render an error template
#         return await render_template("search.html", error=error_data["error"])

#     reps_online = response.json()
#     return await render_template("reps_online.html", reps_online=reps_online)
