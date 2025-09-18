import os
import pandas as pd
import app.utils.db_utils as _db_utils
from config import conf



class DataframeManager():
    def __init__(self) -> None:
        self.df = pd.read_json(os.path.join(conf.static_dir, 'r25/turnus_df_R25.json'))