import os

class conf:
    SECRET_KEY = 'secret'

    base_dir = os.path.dirname(__file__)
    static_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static'))
    utils_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils'))