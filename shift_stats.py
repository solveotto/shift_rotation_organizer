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
                            'turnus' : turnus_navn,
                            'ukedag' : dag_data['navn'],
                            'dag_nr': dag_nr,
                            'uke_nr'   : uke_nr,
                            'start' : start_tid,
                            'slutt' : slutt_tid,
                            'dagsverk' : dag_data['dagsverk'],
                            'poeng' : 0.0
                        }
                        
                        data.append(new_row)
        df = pd.DataFrame(data)
        df.replace('', np.nan, inplace=True)

        return pd.DataFrame(df)
    

    def get_weekend_hours(self):
        df_grpby_turnus = self.turnuser_df.groupby('turnus')
        for turnus_navn, turnus_df in df_grpby_turnus:
            # Sets initial value
            self.points_df.loc[turnus_navn] = 0.0 
            
            turns_df_reset = turnus_df.reset_index()

            # Initialize total weekend hours
            total_weekend_hours = 0
            

            for _index, _dagsverk in turns_df_reset.iterrows():
                if _dagsverk['start'] != _dagsverk['slutt']:     
                    # Checks for bottom of the list
                    if _index + 1 < len(turns_df_reset):
                        start = pd.to_datetime(_dagsverk['start'], format='%H:%M')
                        end = pd.to_datetime(_dagsverk['slutt'], format='%H:%M')
                        ukedag = _dagsverk['ukedag']

                        # Adjust end time if it's on the next day
                        if end < start:
                            end += pd.Timedelta(days=1)

                        # Check if the shift starts on Friday and ends on Saturday
                        if ukedag == 'Fredag' and end.day > start.day:
                            midnight = start.replace(hour=23, minute=59, second=59)
                            saturday_hours = (end - (midnight + pd.Timedelta(seconds=1))).total_seconds() / 3600
                            total_weekend_hours += saturday_hours

                            #### TEST ####
                            #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {saturday_hours}")




                        elif ukedag == 'Søndag':
                            if end.day > start.day:
                                midnight = start.replace(hour=23, minute=59, second=59)
                                sunday_hours = ((midnight + pd.Timedelta(seconds=1)) - start).total_seconds() / 3600
                                total_weekend_hours += sunday_hours
                            else:
                                sunday_hours = (end - start).total_seconds() / 3600
                                total_weekend_hours += sunday_hours

                            #### TEST ####
                            #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {sunday_hours}")
                

                        elif ukedag == 'Lørdag':
                            saturday_hours = (end - start).total_seconds() / 3600
                            total_weekend_hours += saturday_hours

                            #### TEST ####
                            #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {saturday_hours}")

            # Add total hours to turnus_poeng
            self.points_df[turnus_navn] += total_weekend_hours
            
            # # Add to weekend points
            # self.weekend_hours[turnus_navn] = total_weekend_hours



    def get_afternoons(self):
        afternons_df = self.turnuser_df.groupby('turnus')
        for turns_name, turnuser_df in afternons_df:
            afternons_df = turnuser_df.reset_index()

            for _index, turnus in afternons_df.iterrows():
                if turnus['start'] > pd.to_datetime('13:00', format='%H:%M'):
                    print(turns_name, turnus['ukedag'], turnus['uke_nr'], turnus['dag_nr'], turnus['start'])
                    

turnus = Turnus('turnuser_R24.json')

#turnus.get_afternoons()
turnus.get_weekend_hours()

print(turnus.points_df.sort_values())