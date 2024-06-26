from datetime import datetime
import pandas as pd
import numpy as np
import json



class Turnus():
    def __init__(self, json_path) -> None:
        self.turnuser_df = self.JsonToDataframe(json_path)
        self.points_df = pd.Series()
        




    def JsonToDataframe(self, turnus_json):
        with open(turnus_json, 'r') as f:
            json_data = json.load(f)

        data = []

        for turnus in json_data:
            for turnus_navn, turnus_dict in turnus.items():
                for uke_nr, uke_data in turnus_dict.items():
                    for dag_nr, dag_data in uke_data.items():
                        
                        # Konverterer tiden til datetime
                        if len(dag_data['tid']) == 2:
                            start_tid = pd.to_datetime(dag_data['tid'][0], format='%H:%M')
                            slutt_tid = pd.to_datetime(dag_data['tid'][1], format='%H:%M')
                        else:
                            start_tid = pd.to_datetime("00:00", format='%H:%M')
                            slutt_tid = pd.to_datetime("00:00", format='%H:%M')
                            

                        new_row = {
                            'Turnus' : turnus_navn,
                            'ukedag' : dag_data['navn'],
                            'dag_nr': dag_nr,
                            'uke_nr'   : uke_nr,
                            'Start' : start_tid,
                            'Slutt' : slutt_tid,
                            'dagsverk' : dag_data['dagsverk'],
                            'poeng' : 0.0
                        }
                        
                        data.append(new_row)
        df = pd.DataFrame(data)
        df.replace('', np.nan, inplace=True)

        return pd.DataFrame(df)


    def get_afternoons(self):
        afternons_df = self.turnuser_df.groupby('Turnus')
        for turns_name, turnuser_df in afternons_df:
            afternons_df = turnuser_df.reset_index()

            for _index, turnus in afternons_df.iterrows():
                if turnus['Start'] > pd.to_datetime('13:00', format='%H:%M'):
                    print(turns_name, turnus['ukedag'], turnus['uke_nr'], turnus['dag_nr'], turnus['Start'])
                    

turnus = Turnus('turnuser_R24.json')

turnus.get_afternoons()

print(turnus.turnuser_df.tail(1000))