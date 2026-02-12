import os
import configparser

# Read config.ini from the same directory as this file
config_dir = os.path.dirname(__file__)
config_path = os.path.join(config_dir, 'config.ini')

config = configparser.ConfigParser()
config.read(config_path)


def get_database_uri():
    """Get database URI based on config.ini settings"""
    db_type = config.get('general', 'db_type', fallback='sqlite')
    
    if db_type == 'sqlite':
        # SQLite for development
        sqlite_path = config.get('sqlite', 'path', fallback='./dummy.db')
        # Convert relative path to absolute
        if not os.path.isabs(sqlite_path):
            sqlite_path = os.path.join(os.path.dirname(__file__), sqlite_path)
        return f"sqlite:///{sqlite_path}"
    
    elif db_type == 'mysql':
        # MySQL for production - reading from config.ini
        host = config.get('mysql', 'host')
        user = config.get('mysql', 'user')
        password = config.get('mysql', 'password')
        database = config.get('mysql', 'database')
        return f"mysql+pymysql://{user}:{password}@{host}/{database}"
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


class AppConfig:
    # Flask settings from INI
    # Use environment variable first, then INI, then fail
    SECRET_KEY = os.environ.get('SECRET_KEY') or config.get('flask', 'secret_key', fallback='PLEASE_SET_SECRET_KEY_IN_CONFIG')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment or config.ini")
    
    # Export config for db_utils to use
    CONFIG = config

    # Database-specific engine options
    db_type = config.get('general', 'db_type', fallback='sqlite')
    if db_type == 'sqlite':
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True
        }
    else:  # mysql
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_recycle': 300,
            'pool_pre_ping': True
        }

    # Paths
    base_dir = os.path.dirname(__file__)
    static_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static'))
    utils_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils'))
    sessions_dir = os.path.abspath(os.path.join(base_dir, 'app', 'utils', 'sessions'))
    log_dir = os.path.abspath(os.path.join(base_dir, 'app', 'logs'))
    turnusfiler_dir = os.path.abspath(os.path.join(base_dir, 'app', 'static', 'turnusfiler'))

