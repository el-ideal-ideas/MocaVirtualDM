# -- Imports --------------------------------------------------------------------------

from sanic import Blueprint
from sanic.request import Request
from sanic.response import HTTPResponse, json as original_json, text
from orjson import dumps as orjson_dumps
from functools import partial
json = partial(original_json, dumps=orjson_dumps)
from sanic.exceptions import Forbidden
from ... import moca_modules as mzk
from ... import core
from .utils import check_root_pass

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


@root.route('/client-count', {'GET', 'POST', 'OPTIONS'})
async def client_count(request: Request) -> HTTPResponse:
    res = await request.app.mysql.execute_aio(core.CLIENT_COUNT_QUERY)
    return text(res[0][0])


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
    if news_type is None:
        raise Forbidden('missing required parameter (news_type).')
    elif news_type == 'simple-text':
        if title is None or detail is None:
            raise Forbidden('missing required parameter (title or detail).')
    else:
        if img_path is None:
            raise Forbidden('missing required parameter (img_path).')
    await request.app.mysql.execute_aio(
        core.ADD_NEWS_QUERY,
        (news_type, title, detail, url, img_path),
        True
    )
    await request.app.redis.delete('news-info-special')
    await request.app.redis.delete('news-info-normal')
    return text('success.')


@root.route('/get-news', {'GET', 'POST', 'OPTIONS'})
async def get_news(request: Request) -> HTTPResponse:
    special = await request.app.redis.get('news-info-special', None)
    normal = await request.app.redis.get('news-info-normal', None)
    if special is not None and normal is not None:
        mzk.shuffle(normal)
        special.extend(normal)
        return json(special)
    res = await request.app.mysql.execute_aio(core.GET_NEWS_QUERY)
    special = []
    normal = []
    if len(res) > 0 and len(res[0]) > 0:
        for id_, news_type, title, detail, url, img_path, special_flag in res:
            news_item = {
                'id': id_,
                'type': news_type,
                'title': title,
                'detail': detail,
                'url': url,
                'img_path': img_path,
            }
            if special_flag:
                special.append(news_item)
            else:
                normal.append(news_item)
    await request.app.redis.set('news-info-special', special)
    await request.app.redis.set('news-info-normal', normal)
    mzk.shuffle(normal)
    special.extend(normal)
    return json(special)


@root.route('/add-slide-ad', {'GET', 'POST', 'OPTIONS'})
async def add_slide_ad(request: Request) -> HTTPResponse:
    url, img_path = mzk.get_args(
        request,
        ('url', str, None, {'max_length': 1024}),
        ('img_path', str, None, {'max_length': 1024}),
    )
    if img_path is None:
        raise Forbidden('img_path parameter format error.')
    await request.app.mysql.execute_aio(
        core.ADD_SLIDE_AD_QUERY,
        (img_path, url),
        True
    )
    await request.app.redis.delete('slide-ad-special')
    await request.app.redis.delete('slide-ad-normal')
    return text('success.')


@root.route('/get-slide-ad', {'GET', 'POST', 'OPTIONS'})
async def get_slide_ad(request: Request) -> HTTPResponse:
    special = await request.app.redis.get('slide-ad-special', None)
    normal = await request.app.redis.get('slide-ad-normal', None)
    if special is not None and normal is not None:
        mzk.shuffle(normal)
        special.extend(normal)
        return json(special)
    res = await request.app.mysql.execute_aio(core.GET_SLIDE_AD_QUERY)
    special = []
    normal = []
    if len(res) > 0 and len(res[0]) > 0:
        for id_, img_path, url, special_flag in res:
            slide_ad = {
                'id': id_,
                'img_path': img_path,
                'url': url
            }
            if special_flag:
                special.append(slide_ad)
            else:
                normal.append(slide_ad)
    await request.app.redis.set('slide-ad-special', special)
    await request.app.redis.set('slide-ad-normal', normal)
    mzk.shuffle(normal)
    special.extend(normal)
    return json(special)


@root.route('/clear-cache', {'GET', 'POST', 'OPTIONS'})
async def clear_cache(request: Request) -> HTTPResponse:
    check_root_pass(request)
    await request.app.redis.delete('slide-ad-special')
    await request.app.redis.delete('slide-ad-normal')
    await request.app.redis.delete('news-info-special')
    await request.app.redis.delete('news-info-normal')
    return text('success.')


@root.route('/screen-name-list', {'GET', 'POST', 'OPTIONS'})
async def screen_name_list(request: Request) -> HTTPResponse:
    return json(request.app.screen_name_list.list)


@root.route('/add-new-ai', {'GET', 'POST', 'OPTIONS'})
async def add_new_ai(request: Request) -> HTTPResponse:
    check_root_pass(request)
    name, twitter, img, icon, bg, url, first_word, details, password = mzk.get_args(
        request,
        ('name', str, None, {'max_length': 16}),
        ('twitter', str, None, {'max_length': 32}),
        ('img', str, None, {'max_length': 4096}),
        ('icon', str, None, {'max_length': 4096}),
        ('bg', str, None, {'max_length': 4096}),
        ('url', str, None, {'max_length': 4096}),
        ('first_word', str, None, {'max_length': 64}),
        ('details', str, None, {'max_length': 512}),
        ('password', str, None, {'max_length': 16}),
    )
    if twitter is None:
        raise Forbidden('twitter parameter format error.')
    if password is None:
        raise Forbidden('password parameter format error.')
    await request.app.mysql.execute_aio(
        core.ADD_AI_QUERY,
        (name, twitter, img, icon, bg, url, first_word, details, password),
        True,
    )
    await request.app.redis.delete('ai-info-list')
    return text('success.')


@root.route('/get-ai-info-list', {'GET', 'POST', 'OPTIONS'})
async def get_ai_info_list(request: Request) -> HTTPResponse:
    res = await request.app.redis.get('ai-info-list', None)
    if res is None:
        res = await request.app.mysql.execute_aio(core.GET_AI_INFO_QUERY)
        await request.app.redis.set('ai-info-list', res)
    data = [{
        'name': item[0],
        'twitter': item[1],
        'bot_name': item[0],
        'img': item[2],
        'icon': item[3],
        'bg': item[4],
        'url': item[5],
        'first_word': item[6],
        'details': item[7],
    } for item in res]
    mzk.shuffle(data)
    return json(data)

# -------------------------------------------------------------------------- Blueprint --
