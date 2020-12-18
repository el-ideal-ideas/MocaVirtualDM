# -- Imports --------------------------------------------------------------------------

from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json as original_json, text
from orjson import dumps as orjson_dumps
from functools import partial
json = partial(original_json, dumps=orjson_dumps)
from sanic.exceptions import Forbidden
from pathlib import Path
from ... import moca_modules as mzk
from ... import core

# -------------------------------------------------------------------------- Imports --

# -- Blueprint --------------------------------------------------------------------------

root: Blueprint = Blueprint('root', None)


@root.route('/init', {'GET', 'POST', 'OPTIONS'})
async def init(request: Request) -> HTTPResponse:
    client_type, client_id = mzk.get_args(
        request,
        ('client_type|client', str, None, {'is_in': ['web', 'app']}),
        ('client_id|id', str, None, {'max_length': 36, 'min_length': 36})
    )
    if client_type is None:
        raise Forbidden('client_type parameter format error.')
    if client_id is None:
        raise Forbidden('client_id parameter format error.')
    await request.app.mysql.execute_aio(
        core.CLIENT_INIT_QUERY,
        (client_id, client_type, mzk.get_remote_address(request)),
        True
    )
    return text('success.')


@root.route('/configs', {'GET', 'POST', 'OPTIONS'})
async def configs(request: Request) -> HTTPResponse:
    client_type, *_ = mzk.get_args(
        request,
        ('client_type|client', str, None, {'is_in': ['web', 'app']}),
    )
    if client_type == 'web':
        return json(request.app.web_client_config.dict)
    elif client_type == 'app':
        return json(request.app.app_client_config.dict)
    else:
        raise Forbidden('client_type parameter format error.')


@root.route('/add-news', {'GET', 'POST', 'OPTIONS'})
async def add_news(request: Request) -> HTTPResponse:
    news_type, title, detail, url, img_path = mzk.get_args(
        request,
        ('news_type|type', str, None, {'is_in': ['simple-text', 'one-image']}),
        ('title', str, None, {'max_length': 16}),
        ('detail', str, None, {'max_length': 256}),
        ('url', str, None, {'max_length': 1024}),
        ('img_path', str, None, {'max_length': 1024}),
    )
    await request.app.mysql.execute_aio(
        core.ADD_NEWS_QUERY,
        (news_type, title, detail, url, img_path),
        True
    )
    await request.app.redis.delete('news-info')
    return text('success.')


@root.route('/get-news', {'GET', 'POST', 'OPTIONS'})
async def get_news(request: Request) -> HTTPResponse:
    res = await request.app.redis.get('news-info', list, None)
    if res is not None:
        return json(res)
    res = await request.app.mysql.execute_aio(core.GET_NEWS_QUERY)
    special = []
    data = []
    if len(res) > 0 and len(res[0]) > 0:
        for id_, news_type, title, detail, url, img_path, special in res:            
            news_item = {
                'id': id_,
                'type': news_type,
                'title': title,
                'detail': detail,
                'url': url,
                'img_path': img_path,
            }
            if special:
                special.append(news_item)
            else:
                data.append(news_item)
    mzk.shuffle(data)
    special.extend(data)
    return json(special)

# -------------------------------------------------------------------------- Blueprint --
