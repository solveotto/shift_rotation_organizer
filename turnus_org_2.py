from datetime import datetime
import pandas as pd
import json



FIRDAGER = [['XX'], ['TT'], ['OO'], []]



class Turnus():
    def __init__(self) -> None:
        self.turnuser_poeng = pd.Series()
        self.turnuser_dict = self.get_json()
        self.turnuser_df = pd.DataFrame()

        self.weekend_hours = pd.Series()
        #self.afternoon_hours = self.get_afternoons(start_time= pd.to_datetime("12:00", format="%H:%M"))
        self.night_hours = self.get_nights()

        

        # Create dataframe of turnuser
        for turnus in self.turnuser_dict:
            for turnus_navn, turnus_df in turnus.items():
                for uke, uke_data in turnus_df.items():
                    for dag, dag_data in uke_data.items():

                        # Konverterer tiden til datetime
                        if dag_data['tid'] not in FIRDAGER:
                            new_time = [datetime.strptime(time, '%H:%M') for time in dag_data['tid']]
                            start_tid = new_time[0].strftime("%H:%M")
                            slutt_tid = new_time[1].strftime("%H:%M")
                            dagsverk_type = 'ARB'
                        else:
                            start_tid = ''
                            slutt_tid = ''
                            if dag_data['tid'] == []:
                                dagsverk_type = 'SKJ'
                            else:
                                dagsverk_type = 'FRI'

                        new_row = {
                            'Turnus' : turnus_navn,
                            'ukedag' : dag_data['navn'],
                            'ukedag_nr': dag,
                            'uke_nr'   : uke,
                            'dagsverk_type'   : dagsverk_type,
                            'Start' : start_tid,
                            'Slutt' : slutt_tid,
                            'dagsverk' : dag_data['dagsverk']
                        }

                        self.turnuser_df = self.turnuser_df._append(new_row, ignore_index = True)
    
    def get_json(self):
        with open('turnuser_R24.json', 'r') as f:
            data = json.load(f)
        return data
    
    
    def get_weekend_hours(self):
        df_grpby_turnus = self.turnuser_df.groupby('Turnus')
        for turnus_navn, turnus_df in df_grpby_turnus:
            # Sets initial value
            self.turnuser_poeng.loc[turnus_navn] = 0.0 
            
            turns_df_reset = turnus_df.reset_index()

            # Initialize total weekend hours
            total_weekend_hours = 0
            

            # Helgefri. 5p for lørdag og søndag
            for _index, _dagsverk in turns_df_reset.iterrows():
                if _index + 1 < len(turns_df_reset):
                    if len(_dagsverk['Start']) > 0:
                        start = pd.to_datetime(_dagsverk['Start'], format='%H:%M')
                        end = pd.to_datetime(_dagsverk['Slutt'], format='%H:%M')
                        ukedag = _dagsverk['ukedag']

                        # Adjust end time if it's on the next day
                        if end < start:
                            end += pd.Timedelta(days=1)

                        # Check if the shift starts on Friday and ends on Saturday
                        if ukedag == 'Fredag' and end.day > start.day:
                            midnight = start.replace(hour=23, minute=59, second=59)
                            saturday_hours = (end - (midnight + pd.Timedelta(seconds=1))).total_seconds() / 3600
                            total_weekend_hours += saturday_hours

                        elif ukedag == 'Søndag':
                            if end.day > start.day:
                                midnight = start.replace(hour=23, minute=59, second=59)
                                sunday_hours = ((midnight + pd.Timedelta(seconds=1)) - start).total_seconds() / 3600
                                total_weekend_hours += sunday_hours
                            else:
                                sunday_hours = (end - start).total_seconds() / 3600
                                total_weekend_hours += sunday_hours
                
                        elif ukedag == 'Lørdag':
                            saturday_hours = (end - start).total_seconds() / 3600
                            total_weekend_hours = saturday_hours


                    
            self.turnuser_df = turns_df_reset.loc[turnus_navn, 'helgedager'] = total_weekend_hours

            # Add total hours to turnus_poeng
            self.turnuser_poeng[turnus_navn] += total_weekend_hours
            # Add to weekend points
            self.weekend_hours[turnus_navn] = total_weekend_hours



    def get_afternoons(self, start_time):
        self.start_time = start_time



        for _index, _dagsverk in self.turnuser_df.iterrows():
            print(_dagsverk['Turnus'])
            

    def get_nights(self):
        pass


    def calculate_total_score(self, **args):
        pass
            



turnus = Turnus()
turnus.get_afternoons(start_time= pd.to_datetime("12:00", format="%H:%M"))
# print(turnus.turnuser_df)



#turnus.get_weekend_hours()
#print(turnus.weekend_hours.sort_values())



#### TESTS #####

# print(poeng_df.sort_values())


# for i, x in poeng_df.items():
#     # Given number
#     total_time = x

#     # Extract whole hours
#     hours = int(total_time)

#     # Calculate minutes from the fractional part
#     minutes = int((total_time - hours) * 60)

#     #print(f"Tunrus: {i}, Hours: {hours}, Minutes: {minutes}, {x}")