# -- Imports --------------------------------------------------------------------------

from pathlib import Path
from .. import moca_modules as mzk

# -------------------------------------------------------------------------- Imports --

# -- Variables --------------------------------------------------------------------------

# version
VERSION: str = mzk.get_str_from_file(Path(__file__).parent.joinpath('.version'))

# path
TOP_DIR: Path = Path(__file__).parent.parent.parent
CONFIG_DIR: Path = TOP_DIR.joinpath('configs')
LOG_DIR: Path = TOP_DIR.joinpath('logs')
SRC_DIR: Path = TOP_DIR.joinpath('src')
STATIC_DIR: Path = TOP_DIR.joinpath('static')
STORAGE_DIR: Path = TOP_DIR.joinpath('storage')

# create directories if not exists.
for __dir in [CONFIG_DIR, LOG_DIR, STATIC_DIR, STORAGE_DIR]:
    __dir.mkdir(parents=True, exist_ok=True)
del __dir

# configs
SYSTEM_CONFIG: Path = CONFIG_DIR.joinpath('system.json')
SERVER_CONFIG: dict = mzk.load_json_from_file(CONFIG_DIR.joinpath('server.json'))
SANIC_CONFIG: dict = mzk.load_json_from_file(CONFIG_DIR.joinpath('sanic.json'))
DB_CONFIG: dict = mzk.load_json_from_file(CONFIG_DIR.joinpath('database.json'))
MAIL_CONFIG: dict = mzk.load_json_from_file(CONFIG_DIR.joinpath('mail.json'))
IP_BLACKLIST_FILE: Path = CONFIG_DIR.joinpath('ip_blacklist.json')
API_KEY_FILE: Path = CONFIG_DIR.joinpath('api_key.json')
SCREEN_NAME_LIST_FILE: Path = CONFIG_DIR.joinpath('screen_name_list.json')
APP_CLIENT_CONFIG_FILE: Path = CONFIG_DIR.joinpath('app_client_config.json')
WEB_CLIENT_CONFIG_FILE: Path = CONFIG_DIR.joinpath('web_client_config.json')
system_config: mzk.MocaConfig = mzk.MocaConfig(SYSTEM_CONFIG, manual_reload=True)
ip_blacklist: mzk.MocaSynchronizedJSONListFile = mzk.MocaSynchronizedJSONListFile(
    IP_BLACKLIST_FILE, manual_reload=True, remove_duplicates=True,
)
api_key_config: mzk.MocaSynchronizedJSONListFile = mzk.MocaSynchronizedJSONListFile(
    API_KEY_FILE, manual_reload=True
)
screen_name_list: mzk.MocaSynchronizedJSONListFile = mzk.MocaSynchronizedJSONListFile(
    SCREEN_NAME_LIST_FILE, manual_reload=True
)

CLIENT_INIT_QUERY = mzk.get_str_from_file(Path(__file__).parent.joinpath('client_init.sql')).replace(
    '[el]#moca_prefix#', DB_CONFIG['mysql']['prefix']
)
CLIENT_COUNT_QUERY = mzk.get_str_from_file(Path(__file__).parent.joinpath('client_count.sql')).replace(
    '[el]#moca_prefix#', DB_CONFIG['mysql']['prefix']
)
ADD_NEWS_QUERY = mzk.get_str_from_file(Path(__file__).parent.joinpath('add_news.sql')).replace(
    '[el]#moca_prefix#', DB_CONFIG['mysql']['prefix']
)
GET_NEWS_QUERY = mzk.get_str_from_file(Path(__file__).parent.joinpath('get_news.sql')).replace(
    '[el]#moca_prefix#', DB_CONFIG['mysql']['prefix']
)
ADD_SLIDE_AD_QUERY = mzk.get_str_from_file(Path(__file__).parent.joinpath('add_slide_ad.sql')).replace(
    '[el]#moca_prefix#', DB_CONFIG['mysql']['prefix']
)
GET_SLIDE_AD_QUERY = mzk.get_str_from_file(Path(__file__).parent.joinpath('get_slide_ad.sql')).replace(
    '[el]#moca_prefix#', DB_CONFIG['mysql']['prefix']
)

# -------------------------------------------------------------------------- Variables --
