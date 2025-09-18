import os
import configparser

# Read config.ini
config = configparser.ConfigParser()
config.read('config.ini')

class conf:
    # Flask settings from INI
    # Use environment variable first, then INI, then fail
    SECRET_KEY = os.environ.get('SECRET_KEY') or config.get('flask', 'secret_key', fallback='PLEASE_SET_SECRET_KEY_IN_CONFIG')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment or config.ini")
    CURRENT_TURNUS = config.get('flask', 'current_turnus', fallback='r25')
    if not CURRENT_TURNUS:
        raise ValueError("CURRENT_TURNUS must be set in config.ini")

    # Paths
    base_dir = os.path.dirname(__file__)
    static_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static'))
    utils_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils'))
    sessions_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils', 'sessions'))
    log_dir = os.path.abspath(os.path.join(base_dir, 'app', 'logs'))
    turnus_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static', CURRENT_TURNUS))