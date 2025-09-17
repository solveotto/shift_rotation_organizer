import os
import pandas as pd
import app.utils.db_utils as _db_utils
from config import conf



class DataframeManager():
    def __init__(self) -> None:
        self.df = pd.read_json(os.path.join(conf.static_dir, 'r25/turnus_df_R25.json'))
        self.username, self.user_id = 'solve', 4
        
        self.helgetimer_dagtid_multip = 0

        self.sort_by_btn_txt = 'Navn'
        self.sort_by_ascending = True
        self.sort_by_prev_type = None


        self.df['poeng'] = 0
        self.sort_by('turnus', inizialize=True)
        self.get_all_user_points()
        

    def get_all_user_points(self):
        try:
            stored_user_points = _db_utils.get_all_ratings(self.user_id)
            
            for shift_title, shift_value in stored_user_points:
                if shift_title in self.df['turnus'].values:
                    self.df.loc[self.df['turnus'] == shift_title, 'poeng'] += shift_value
        except TypeError:
            pass


 
    def sort_by(self, _type, inizialize=False):
        # Alters the name for the button text
        if _type == 'turnus':
            sort_name = 'Navn'
        else:
            sort_name = _type.replace("_", " ")
        self.sort_by_btn_txt = sort_name.title()

        if inizialize == True:
            self.sort_by_ascending = True
        else:
            if self.sort_by_prev_type == _type:
                self.sort_by_ascending = not self.sort_by_ascending
            else:
                self.sort_by_ascending = True
            self.sort_by_prev_type = _type

        self.df = self.df.sort_values(by=_type, ascending=self.sort_by_ascending)
        
        

    def calc_multipliers(self, _type, multip):
        self.df['poeng'] = round(self.df['poeng'] + self.df[_type] * multip, 1)


    def calc_thresholds(self, _type, _th, multip):
        for index, row in self.df.iterrows():
            if row[_type] > _th:
                self.df.at[index, 'poeng'] += (row[_type] - _th) * multip