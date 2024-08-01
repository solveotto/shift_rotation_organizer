from datetime import datetime, time
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


        self.get_shift_stats()
        #self.add_points_to_stats_df()

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
                            'dagsverk' : dag_data['dagsverk']
                        }
                        
                        data.append(new_row)
        df = pd.DataFrame(data)
        df.replace('', np.nan, inplace=True)

        return pd.DataFrame(df)
    


    def get_shift_stats(self):
        df_grpby_turnus = self.turnuser_df.groupby('turnus')
        
        for turnus_navn, turnus_df in df_grpby_turnus:

            turuns_df_reset = turnus_df.reset_index()

            EVENING = time(16,0)

            # Adds new stats to dataframe
            total_weekend_hours = 0
            weekend_daytime_hours = 0
            total_weekends_days = 0
            nights_in_weekend = 0
            evening_in_weekend = 0
            early = 0
            starts_before_6 = 0
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


                        ### WEEKENDS ###


                        if ukedag == 'Fredag' and end.day > start.day:
                            midnight = start.replace(hour=23, minute=59, second=59)
                            saturday_hours = (end - (midnight + pd.Timedelta(seconds=1))).total_seconds() / 3600
                            total_weekend_hours += saturday_hours
                            # fridays over 2 hours into saturday
                            if saturday_hours > 2:
                                total_weekends_days += 1

                        elif ukedag == 'Søndag':
                            if end.day > start.day:
                                midnight = start.replace(hour=23, minute=59, second=59)
                                sunday_hours = ((midnight + pd.Timedelta(seconds=1)) - start).total_seconds() / 3600
                                total_weekend_hours += sunday_hours
                                
                            else:
                                sunday_hours = (end - start).total_seconds() / 3600
                                total_weekend_hours += sunday_hours


                            if start.time() > EVENING:
                                evening_in_weekend += sunday_hours

                            
                            
                            total_weekends_days += 1

                        elif ukedag == 'Lørdag':
                            saturday_hours = (end - start).total_seconds() / 3600
                            total_weekend_hours += saturday_hours
                            total_weekends_days += 1

                            if start.time() > EVENING:
                                evening_in_weekend += saturday_hours

                        
                        ### ENDS BERFORE 1630 ###
                        if end.time() < time(16,20):
                            early += 1
                            ### STARTS BEFORE 6 ####
                            if start.time() < time(6,0):
                                starts_before_6 += 1
                            
                            if _dagsverk['ukedag'] == 'Lørdag':
                                nights_in_weekend += (end - start).total_seconds() / 3600



                        ### AFTERNOONS ENDS AFTER 1620 ###(
                        if end.time() >= time(16,20) or end.date() > start.date():
                            if str(end.date()) == '1900-01-02' and end.time() < time(3,0):
                                afternoon_count += 1
                            elif str(end.date()) == '1900-01-01':
                                afternoon_count += 1
                                      
                                      
                            # ### Afternoons in row ###
                            # next_row_value = turuns_df_reset.iloc[_index + 1]['start']
                            # # Check if the next row's 'column_name' contains a specific value
                            # if next_row_value > pd.to_datetime('13:00', format='%H:%M'):
                            #     afternons_in_row += 1
                                

                #### TEST ####
                #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {sunday_hours}")

            # Adds shift as new row to dataframe
            new_row = pd.DataFrame({
                'turnus': [turnus_navn], 
                'helgetimer': [round(total_weekend_hours,1)], 
                'helgedager': [total_weekends_days],
                'night_wknd_hours': [round(nights_in_weekend,1)],
                'evening_wknd_hours': [round(evening_in_weekend)],
                'tidlig': [early],
                'før_6': [starts_before_6],
                'ettermiddag' : [afternoon_count],
                'natt': [night_count],
                'poeng': 0
                
                })
            
            self.stats_df = pd.concat([self.stats_df, new_row], ignore_index=True)


        #### FLYTTES TIL ANNEN MODUL #####

    # def add_points_to_stats_df(self):

    #     self.stats_df['poeng'] = self.stats_df.apply(lambda x: 
    #                                                  x['helgetimer']*1 + 
    #                                                  x['ettermiddag']*0.5, 
    #                                                  axis=1)
        
    #     # Add points for number of night watches
    #     self.stats_df.loc[self.stats_df['natt'] > 6, 'poeng'] += 1
    #     self.stats_df.loc[self.stats_df['natt'] > 10, 'poeng'] += 5


        

    # def sort_stats(self, keyword, asc=True):
    #     self.stats_df = self.stats_df.sort_values(by=keyword, ascending=asc)
    #     self.stats_df.reset_index(drop=True, inplace=True)

                    

if __name__ == '__main__':
    turnus = Turnus('turnuser_R24.json')

    turnus.stats_df.to_json('turnus_df_R24.json')

    print(turnus.stats_df)
