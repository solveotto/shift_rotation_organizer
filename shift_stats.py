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
                            'ukedag' : dag_data['ukedag'],
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
            shift_cnt = 0
            helgetimer = 0
            helgetimer_dagtid = 0
            helgedager = 0
            helgetimer_natt = 0
            helgetimer_ettermiddag = 0
            tidlig = 0
            before_6 = 0
            afternoon_count = 0
            afternoon_ends_before_20 = 0
            afternons_in_row = 0
            night_count = 0
            

            for _index, _dagsverk in turuns_df_reset.iterrows():
                if _dagsverk['start'] != _dagsverk['slutt']:     
                    # Checks for bottom of the list
                    if _index + 1 < len(turuns_df_reset):
                        shift_cnt += 1
                        start = pd.to_datetime(_dagsverk['start'], format='%H:%M')
                        end = pd.to_datetime(_dagsverk['slutt'], format='%H:%M')
                        ukedag = _dagsverk['ukedag']
                        midnight = start.replace(hour=23, minute=59, second=59)

                        # Adjust end time if it's on the next day
                        if end < start:
                            end += pd.Timedelta(days=1)
                            # Counts night shifts
                            if _dagsverk['slutt'] > pd.to_datetime('03:00', format='%H:%M'):
                                night_count += 1


                        ### WEEKENDS ###
                        if ukedag == 'Fredag' and end.day > start.day:
                            saturday_hours = (end - (midnight + pd.Timedelta(seconds=1))).total_seconds() / 3600
                            helgetimer += saturday_hours
                            # fridays over 2 hours into saturday
                            if saturday_hours > 0:
                                helgedager += 1

                        elif ukedag == 'Lørdag':
                            saturday_hours = (end - start).total_seconds() / 3600
                            helgetimer += saturday_hours
                            helgedager += 1

                            if start.time() > EVENING:
                                helgetimer_ettermiddag += saturday_hours

                            # Counts daytime hours in weekend
                            if start.time() < time(14,0):
                                helgetimer_dagtid +=  saturday_hours

                        elif ukedag == 'Søndag':
                            # counts hours before midnight and excludes hours after midnight in night shifts
                            if end.day > start.day:
                                sunday_hours = ((midnight + pd.Timedelta(seconds=1)) - start).total_seconds() / 3600
                                helgetimer += sunday_hours
                                    
                                # Counts evning hours
                                if start.time() > EVENING:
                                    helgetimer_ettermiddag += sunday_hours

                            # Counts sunday weekend hours    
                            else:
                                sunday_hours = (end - start).total_seconds() / 3600
                                helgetimer += sunday_hours
                                
                                # Counts evning hours
                                if start.time() > EVENING:
                                    helgetimer_ettermiddag += sunday_hours

                                # Counts daytime hours in weekend
                                if start.time() < time(14,0):
                                    helgetimer_dagtid += sunday_hours

                            helgedager += 1




                        ### ENDS BERFORE 16 ###
                        if end.time() < time(16,00) and start.time() < time(12,00):
                            tidlig += 1
                            ### STARTS BEFORE 6 ####
                            if start.time() < time(6,0):
                                before_6 += 1
                            
                            if _dagsverk['ukedag'] == 'Lørdag':
                                helgetimer_natt += (end - start).total_seconds() / 3600



                        ### AFTERNOONS ENDS AFTER 16 ###(
                        if end.time() >= time(16,00) or end.date() > start.date():
                            if str(end.date()) == '1900-01-02' and end.time() < time(3,0):
                                afternoon_count += 1
                            elif str(end.date()) == '1900-01-01':
                                afternoon_count += 1
                                if end.time() <= time(20):
                                    afternoon_ends_before_20 += 1
                                    


                            
                                      
                                      
                            # ### Afternoons in row ###
                            # next_row_cnt = 0
                            # next_row_is_afternoon = True
                            # while next_row_is_afternoon == True:
                            #     next_row_value = turuns_df_reset.iloc[_index + 1]['start']
                            #     # Check if the next row's 'column_name' contains a specific value
                            #     if next_row_value > pd.to_datetime('16:00', format='%H:%M'):
                            #         next_row_cnt += 1
                            #     else:
                            #         next_row_is_afternoon = False
                                    
                            # afternons_in_row += next_row_cnt
                                

                #### TEST ####
                #print(f"{_dagsverk['turnus']}, {_dagsverk['uke_nr']}, {_dagsverk['ukedag']}, {sunday_hours}")

            # Adds shift as new row to dataframe
            new_row = pd.DataFrame({
                'turnus': [turnus_navn], 
                'shift_cnt': [shift_cnt],
                'tidlig': [tidlig],
                'ettermiddag' : [afternoon_count],
                'natt': [night_count],
                'helgetimer': [round(helgetimer,1)], 
                'helgedager': [helgedager],
                'helgetimer_dagtid': [round(helgetimer_dagtid,1)],
                'helegtimer_natt': [round(helgetimer_natt,1)],
                'helgetimer_ettermiddag': [round(helgetimer_ettermiddag)],
                'before_6': [before_6],
                'afternoon_ends_before_20': [afternoon_ends_before_20],
                'afternoons_in_row': [afternons_in_row],
                'poeng': 0
                
                })
            
            self.stats_df = pd.concat([self.stats_df, new_row], ignore_index=True)


if __name__ == '__main__':
    turnus = Turnus('turnuser_R24.json')

    turnus.stats_df.to_json('turnus_df_R24.json')

    #print(turnus.stats_df)
