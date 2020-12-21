# -- Imports --------------------------------------------------------------------------

from .core import (
    VERSION, TOP_DIR, CONFIG_DIR, LOG_DIR, SRC_DIR, STATIC_DIR, STORAGE_DIR, SYSTEM_CONFIG, SANIC_CONFIG, SERVER_CONFIG,
    IP_BLACKLIST_FILE, API_KEY_FILE, system_config, ip_blacklist, APP_CLIENT_CONFIG_FILE, WEB_CLIENT_CONFIG_FILE,
    DB_CONFIG, MAIL_CONFIG, CLIENT_INIT_QUERY, ADD_NEWS_QUERY, GET_NEWS_QUERY, ADD_SLIDE_AD_QUERY, GET_SLIDE_AD_QUERY,
    CLIENT_COUNT_QUERY, SCREEN_NAME_LIST_FILE, screen_name_list, ADD_AI_QUERY, GET_AI_INFO_QUERY
)
from .db import mysql, cursor, redis
from .. import moca_modules as mzk
from pathlib import Path
from warnings import catch_warnings, simplefilter

# -------------------------------------------------------------------------- Imports --

# -- Init --------------------------------------------------------------------------

__users_table = mzk.get_str_from_file(Path(__file__).parent.joinpath('clients_table.sql'))
__news_table = mzk.get_str_from_file(Path(__file__).parent.joinpath('news_table.sql'))
__slide_ad_table = mzk.get_str_from_file(Path(__file__).parent.joinpath('slide_ad_table.sql'))
__ai_list_table = mzk.get_str_from_file(Path(__file__).parent.joinpath('ai_list_table.sql'))
with catch_warnings():
    simplefilter("ignore")
    cursor.execute(__users_table % (DB_CONFIG['mysql']['prefix'],))
    mysql.commit()
    cursor.execute(__news_table % (DB_CONFIG['mysql']['prefix'],))
    mysql.commit()
    cursor.execute(__slide_ad_table % (DB_CONFIG['mysql']['prefix'],))
    mysql.commit()
    cursor.execute(__ai_list_table % (DB_CONFIG['mysql']['prefix'],))
    mysql.commit()
del __users_table


# -------------------------------------------------------------------------- Init --
