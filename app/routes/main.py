import os
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import Blueprint
from config import conf
from app.utils import df_utils

# Global variables that need to be shared across Blueprints
df_manager = df_utils.DataframeManager()

# Load turnus data
with open(os.path.join(conf.static_dir, 'r25/turnuser_R25.json'), 'r') as f:
    turnus_data = json.load(f)

# Configure logging
os.makedirs(conf.log_dir, exist_ok=True)
log_file_path = os.path.join(conf.log_dir, 'app.log')
rotating_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5)
rotating_handler.setLevel(logging.WARNING)
rotating_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

logging.basicConfig(level=logging.WARNING, handlers=[
    rotating_handler,
    logging.StreamHandler()
])

# Create a lock object for favorites
from threading import Lock
favorite_lock = Lock()

# Import all Blueprints
from app.routes.auth import auth
from app.routes.shifts import shifts
from app.routes.admin import admin
from app.routes.api import api
from app.routes.downloads import downloads

# List of all Blueprints to register
blueprints = [auth, shifts, admin, api, downloads] 