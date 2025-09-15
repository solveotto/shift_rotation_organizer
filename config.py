import os

class conf:
    SECRET_KEY = 'secret'

    CURRENT_TURNUS = 'r25'

    base_dir = os.path.dirname(__file__)
    static_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static'))
    utils_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils'))
    sessions_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils', 'sessions'))
    log_dir = os.path.abspath(os.path.join(base_dir, 'app', 'logs'))
    turnus_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static', CURRENT_TURNUS))