from datetime import datetime
import pandas as pd
import numpy as np
import json

'''
- Fridays that goes over 2 hours into saturay counts as weekend days.
'''




class Turnus():
    def __init__(self, json_path) -> None:
        self.turnuser_df = self.JsonToDataframe(json_path)
        self.stats_df = pd.DataFrame()


        
        



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
    

    def add_or_update_points(self, df, **kwargs):
        if 'turnus' not in kwargs:
            raise ValueError("The primary key 'turnus' must be provided as a keyword argument.")
        
        turnus = kwargs['turnus']

        if turnus in df['turnus'].values:
            for key, value in kwargs.items():
                df.loc[df['turnus'] == turnus, key] += value
        else:
            new_row = pd.DataFrame([kwargs])
            df = df.dropna(axis=1, how='all')
            df = pd.concat([df, new_row], ignore_index=True)
        
        return df
    


    def get_shift_stats(self):
        df_grpby_turnus = self.turnuser_df.groupby('turnus')
        for turnus_navn, turnus_df in df_grpby_turnus:

            turuns_df_reset = turnus_df.reset_index()


            total_weekend_hours = 0
            total_weekends_days = 0
            afternoon_count = 0
            afternons_in_row = 0
            night_count = 0
            

            for _index, _dagsverk in turuns_df_reset.iterrows():
                if _dagsverk['start'] != _dagsverk['slutt']:     
                    # Checks for bottom of the list
                    if _index + 1 < len(turuns_df_reset):
                        start = pd.to_datetime(_dagsverk['start'], format='%H:%M')
                        end = pd.to_datetime(_dagsverk['slutt'], format='%H:%M')
                        
                        ukedag = _dagsverk['ukedag']

                        # Adjust end time if it's on the next day
                        if end < start:
                            end += pd.Timedelta(days=1)
                            # Counts night shifts
                            if _dagsverk['slutt'] > pd.to_datetime('03:00', format='%H:%M'):
                                night_count += 1


                        ### Weekends ###
                        # Check if the shift starts on Friday and ends on Saturday
                        if ukedag == 'Fredag' and end.day > start.day:
                            midnight = start.replace(hour=23, minute=59, second=59)
                            saturday_hours = (end - (midnight + pd.Timedelta(seconds=1))).total_seconds() / 3600
                            total_weekend_hours += saturday_hours
                            # fridays over 2 hours into saturday
                            if saturday_hours > 2:
                                total_weekends_days += 1

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
                            total_weekends_days += 1

                            #### TEST ####
                            #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {sunday_hours}")
                

                        elif ukedag == 'Lørdag':
                            saturday_hours = (end - start).total_seconds() / 3600
                            total_weekend_hours += saturday_hours
                            total_weekends_days += 1

                            #### TEST ####
                            #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {saturday_hours}")


                        ### AFTERNOONS ###
                        # creates a string version of the end date to check if i
                        end_str = f'{end.year}-{end.month}-{end.day}'
                        start_time = start.time()
                        end_time = end.time()
                        if start > pd.to_datetime('12:00', format='%H:%M'):
                            if end == '1900-1-2':
                                if end < pd.to_datetime('03:00', format='%H:%M'):
                                    afternoon_count += 1
                            elif end < pd.to_datetime('23:59', format='%H:%M'):
                                    afternoon_count += 1

                                    print(start_time)
                                    print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}")
                                      
                            

                            # ### Afternoons in row ###
                            # next_row_value = turuns_df_reset.iloc[_index + 1]['start']
                            # # Check if the next row's 'column_name' contains a specific value
                            # if next_row_value > pd.to_datetime('13:00', format='%H:%M'):
                            #     afternons_in_row += 1
                                

            # Adds shift as new row to dataframe
            new_row = pd.DataFrame({
                'turnus': [turnus_navn], 
                'weekend_hours': [round(total_weekend_hours,1)], 
                'weekend_days': [total_weekends_days],
                'nights': [night_count],
                'afternoons' : [afternoon_count],
                'afternoons_in_row' : [afternons_in_row]
                })
            
            self.stats_df = pd.concat([self.stats_df, new_row], ignore_index=True)

                    

turnus = Turnus('turnuser_R24.json')

#turnus.get_afternoons()
turnus.get_shift_stats()
#turnus.get_afternoons()

print(turnus.stats_df.sort_values(by='weekend_hours'))