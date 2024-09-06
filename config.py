import os

class Config:
    SECRET_KEY = 'secret'

    base_dir = os.path.dirname(__file__)
    static_dir = os.path.join(base_dir, 'app', 'static')
    static_dir = os.path.abspath(static_dir)