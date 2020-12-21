# -- Imports --------------------------------------------------------------------------

from sanic import __version__
from sys import version_info
from orjson import loads
from requests import post
from .. import moca_modules as mzk
from .. import core

# -------------------------------------------------------------------------- Imports --

# -- Console --------------------------------------------------------------------------

console = mzk.typer_console


@console.command('version')
def version(only_number: bool = False) -> None:
    """Show the version info of MocaSystem."""
    if only_number:
        mzk.tsecho(core.VERSION)
    else:
        mzk.tsecho(f'MocaVirtualDM ({core.VERSION})')


@console.command('update')
def update() -> None:
    """Update modules."""
    path = mzk.TMP_DIR.joinpath('moca_commands_installed_modules.txt')
    mzk.call(f'{mzk.executable} -m pip freeze > {path}', shell=True)
    mzk.call(f'{mzk.executable} -m pip uninstall -r {path} -y', shell=True)
    mzk.install_requirements_file(core.TOP_DIR.joinpath('requirements.txt'))


@console.command('update-system')
def update_system() -> None:
    """Update system, get latest code from github."""
    mzk.update_use_github(
        core.TOP_DIR,
        'https://github.com/el-ideal-ideas/MocaVirtualDM',
        [
            core.CONFIG_DIR,
            core.LOG_DIR,
            core.STATIC_DIR,
            core.STORAGE_DIR,
            core.TOP_DIR.joinpath('keep'),
            core.TOP_DIR.joinpath('atexit.py'),
            core.TOP_DIR.joinpath('atexit.sh'),
            core.TOP_DIR.joinpath('startup.py'),
            core.TOP_DIR.joinpath('startup.sh'),
        ]
    )


@console.command('reset-system')
def reset_system() -> None:
    """Reset this system."""
    mzk.update_use_github(
        core.TOP_DIR,
        'https://github.com/el-ideal-ideas/MocaVirtualDM',
        []
    )


@console.command('run')
def run(sleep: float = 0) -> None:
    """Run MocaVirtualDM."""
    try:
        mzk.sleep(sleep)
        # run startup script.
        mzk.call(f'{mzk.executable} "{core.TOP_DIR.joinpath("startup.py")}"', shell=True)
        mzk.call(
            f'chmod +x "{core.TOP_DIR.joinpath("startup.sh")}";sh "{core.TOP_DIR.joinpath("startup.sh")}"', shell=True
        )
        from ..server import moca_sanic
        moca_sanic.run()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as error:
        mzk.print_critical(str(error))
        mzk.print_exc()
        mzk.append_str_to_file(core.LOG_DIR.joinpath('critical.log'), str(error))
        mzk.append_str_to_file(core.LOG_DIR.joinpath('critical.log'), mzk.format_exc())
    finally:
        # run atexit script.
        mzk.call(f'{mzk.executable} "{core.TOP_DIR.joinpath("atexit.py")}"', shell=True)
        mzk.call(
            f'chmod +x "{core.TOP_DIR.joinpath("atexit.sh")}";sh "{core.TOP_DIR.joinpath("atexit.sh")}"', shell=True
        )


@console.command('start')
def start(sleep: float = 0) -> None:
    """Run MocaVirtualDM in background."""
    mzk.sleep(sleep)
    mzk.call(
        f'nohup {mzk.executable} "{core.TOP_DIR.joinpath("moca.py")}" run &> /dev/null &',
        shell=True
    )


@console.command('stop')
def stop(sleep: float = 0) -> None:
    """Stop MocaVirtualDM."""
    mzk.sleep(sleep)
    pid = []
    for line in mzk.check_output('ps -ef | grep MocaVirtualDM', shell=True).decode().splitlines():
        pid.append(line.split()[1])
    mzk.call(f'kill {" ".join(pid)} &> /dev/null &', shell=True)


@console.command('restart')
def restart(sleep: float = 0) -> None:
    """Restart MocaVirtualDM."""
    mzk.sleep(sleep)
    mzk.call(f'nohup {mzk.executable} "{core.TOP_DIR.joinpath("moca.py")}" stop &> /dev/null &', shell=True)
    mzk.sleep(3)
    mzk.call(f'nohup {mzk.executable} "{core.TOP_DIR.joinpath("moca.py")}" start &> /dev/null &', shell=True)
    mzk.sleep(3)


@console.command('status')
def show_running_process() -> None:
    """Show all MocaVirtualDM process."""
    print('++++++++++++++++++++++++++++++++++++++++++++++')
    print(f'Python: {version_info.major}.{version_info.minor}.{version_info.micro}')
    print(f'MocaSystem: {core.VERSION}')
    print(f'MocaModules: {mzk.VERSION}')
    print(f'MocaSanic: {mzk.MocaSanic.VERSION}')
    print(f'Sanic: {__version__}')
    print('++++++++++++++++++++++++++++++++++++++++++++++')
    print('PID\tPPID\tNAME')
    for line in mzk.check_output('ps -ef | grep MocaVirtualDM', shell=True).decode().splitlines():
        items = line.split()
        if items[7].startswith('MocaVirtualDM'):
            print(f"{items[1]}\t{items[2]}\t{' '.join(items[7:])}")
    print('++++++++++++++++++++++++++++++++++++++++++++++')


@console.command('turn-on')
def turn_on() -> None:
    """Stop maintenance mode."""
    core.system_config.set_config('maintenance_mode', False)
    mzk.tsecho('Stopped maintenance mode. MocaSanic is working.', fg=mzk.tcolors.GREEN)


@console.command('turn-off')
def turn_off() -> None:
    """Start maintenance mode."""
    core.system_config.set_config('maintenance_mode', True)
    mzk.tsecho('MocaSystem is currently undergoing maintenance. All requests will receive 503.', fg=mzk.tcolors.GREEN)


@console.command('clear-logs')
def clear_logs() -> None:
    """Clear log files."""
    mzk.call(f'rm -rf {core.LOG_DIR}/*', shell=True)


@console.command('__create-and-update-bots', hidden=True)
def __create_and_update_bots() -> None:
    """Create and update bots, use screen_name_list.json"""
    moca_api = core.system_config.get_config('moca_api')
    moca_twitter_status = mzk.wcheck(moca_api['url']['moca_twitter'] + '/status')
    moca_bot_status = mzk.wcheck(moca_api['url']['moca_bot'] + '/status')
    mzk.tsecho(f'API Status: MocaTwitterUtil<{moca_twitter_status}>, MocaBot<{moca_bot_status}>')
    if moca_twitter_status and moca_bot_status:
        for screen_name in core.screen_name_list.list:
            path = core.STORAGE_DIR.joinpath(screen_name + '-bot-data.json')
            if path.is_file():
                data = mzk.load_json_from_file(path)
            else:
                data = []
            print(f'old-data: {len(data)}')
            new = []
            res = mzk.get_text_from_url(
                moca_api['url']['moca_twitter'] + '/moca-twitter/get-latest-tweets',
                headers={
                    'API-KEY': moca_api['api_key']['moca_twitter'],
                    'SCREEN-NAME': screen_name,
                }
            )
            if res == '':
                mzk.tsecho(f'Get latest tweets failed. <{screen_name}>', fg=mzk.tcolors.RED)
                continue
            else:
                json_data = loads(res)
                for item in json_data:
                    if 'RT' in item[2]:
                        continue
                    for text in item[2].split():
                        if '@' in text:
                            continue
                        elif '#' in text:
                            continue
                        elif 'http' in text:
                            continue
                        elif len(text) < 3:
                            continue
                        elif text.isdigit():
                            continue
                        else:
                            if text not in data:
                                new.append(text)
            error_flag = False
            # if not exists create a new bot.
            post(
                moca_api['url']['moca_bot'] + '/moca-bot/create-bot',
                json={
                    'api_key': moca_api['api_key']['moca_bot'],
                    'name': screen_name,
                    'root_pass': moca_api['moca_bot_root_pass'],
                }
            )
            mzk.sleep(3)
            data.extend(new)
            while len(new) > 0:
                message_list = new[:8000]
                new[:8000] = []
                res = post(
                    moca_api['url']['moca_bot'] + '/moca-bot/study',
                    json={
                        'api_key': moca_api['api_key']['moca_bot'],
                        'name': screen_name,
                        'message_list': message_list,
                        'root_pass': moca_api['moca_bot_root_pass'],
                    }
                )
                if res.status_code != 200:
                    mzk.tsecho(f'Send text to MocaBot API failed. <{screen_name}>', fg=mzk.tcolors.RED)
                    mzk.tsecho(f'Status: {res.status_code}, Body: {res.text}', fg=mzk.tcolors.RED)
                    error_flag = True
                    break
            if not error_flag:
                print(f'current-data: {len(data)}')
                mzk.dump_json_to_file(data, path)
                mzk.tsecho(f'Update bot successfully. <{screen_name}>', fg=mzk.tcolors.GREEN)
    else:
        mzk.tsecho(f'Please start MocaTwitterUtil and MocaBot api server.', fg=mzk.tcolors.RED)


@console.command('__keep-bots-update', hidden=True)
def __keep_bots_update(interval: int) -> None:
    """Create and update bots, use screen_name_list.json"""
    mzk.set_process_name(f'MocaVirtualDM({core.VERSION}) -- keep-update-bots')
    while True:
        mzk.call(
            f'nohup {mzk.executable} "{core.TOP_DIR.joinpath("moca.py")}" __create-and-update-bots &> /dev/null &',
            shell=True
        )
        mzk.sleep(interval)


@console.command('keep-bots-update')
def keep_bots_update(interval: int) -> None:
    """Create and update bots, use screen_name_list.json"""
    mzk.call(
        f'nohup {mzk.executable} "{core.TOP_DIR.joinpath("moca.py")}" __keep-bots-update {interval} &> /dev/null &',
        shell=True
    )

# -------------------------------------------------------------------------- Console --
