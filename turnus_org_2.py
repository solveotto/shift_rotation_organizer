from datetime import datetime
import pandas as pd
import json


with open('turnuser_R24.json', 'r') as f:
    turnuser_dict = json.load(f)

FIRDAGER = [['XX'], ['TT'], ['OO'], []]



turnuser_df = pd.DataFrame()
poeng_df = pd.Series()


for turnus in turnuser_dict:
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
                    
                # Gi poeng til vakta


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
                turnuser_df = turnuser_df._append(new_row, ignore_index = True)


# df_search = df.copy()

# df_search['Start'] = pd.to_datetime(df['Start'], format="%H:%M")
# df_search['Slutt'] = pd.to_datetime(df['Slutt'], format="%H:%M")

# df_start = df_search.set_index('Start')
# df_start = df_start.between_time('09:00', '18:00')

# df_slutt = df_search.set_index('Slutt')
# df_slutt = df_slutt.between_time('21:00', '22:00')


# # Find entries that are in both DataFrames
# df_filtered = pd.merge(df_start, df_slutt, how='inner')




# mask_lordag = df.isin(['Lørdag'])
# mask_sondag = df.isin(['Søndag']).any(axis=1)
# mask_fri = df.isin(['FRI']).any(axis=1)


# df_lordag_and_fri = df[mask_lordag]
# df_sondag_and_fri = df[mask_sondag & mask_fri]


# df_test = df[(df['ukedag'] == 'Lørdag') & (df['dagsverk_type'] == 'ARB') & (df['Start'] < '10:00')]
# print(df_test)


df_grpby_turnus = turnuser_df.groupby('Turnus')
for turnus_navn, turnus_df in df_grpby_turnus:
    poeng_df.loc[turnus_navn] = 0.0 

    turns_df_reset = turnus_df.reset_index()

    # Initialize total weekend hours
    total_weekend_hours = 0
    

    #### TEST ####
    test_turnus = "OSL_Ramme_03"

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
                friday_hours = (midnight - start).total_seconds() / 3600
                saturday_hours = (end - (midnight + pd.Timedelta(seconds=1))).total_seconds() / 3600
                total_weekend_hours += saturday_hours

                if turnus_navn == test_turnus:
                    print(_dagsverk['ukedag'], _dagsverk['uke_nr'], saturday_hours)

            elif ukedag == 'Søndag':
                if end.day > start.day:
                    midnight = start.replace(hour=23, minute=59, second=59)
                    sunday_hours = ((midnight + pd.Timedelta(seconds=1)) - start).total_seconds() / 3600
                    total_weekend_hours += sunday_hours

                    if turnus_navn == test_turnus:
                        print(_dagsverk['ukedag'], _dagsverk['uke_nr'], sunday_hours)


                else:
                    hours = (end - start).total_seconds() / 3600
                    total_weekend_hours += hours


                    if turnus_navn == test_turnus:
                        print(_dagsverk['ukedag'], _dagsverk['uke_nr'], hours)


     
            elif ukedag == 'Lørdag':
                # Calculate total hours for shifts fully within the weekend
                hours = (end - start).total_seconds() / 3600
                total_weekend_hours += hours

                if turnus_navn == test_turnus:
                    print(_dagsverk['ukedag'], _dagsverk['uke_nr'], hours)

                
    total_hours = int(total_weekend_hours)  # Get the whole hours
    total_minutes = int((total_weekend_hours - total_hours) * 60)  # Convert the fractional hours to minutes


    # Add it to poeng_df as a new column
    poeng_df[turnus_navn] += total_weekend_hours
    #print(f"{turnus_navn}: Total weekend hours: {type(total_weekend_hours)}")
    # print(f"{turnus_navn}: Hours: {total_hours}, Minutes: {total_minutes}")


for i, x in poeng_df.items():
    # Given number
    total_time = x

    # Extract whole hours
    hours = int(total_time)

    # Calculate minutes from the fractional part
    minutes = int((total_time - hours) * 60)

    #print(f"Tunrus: {i}, Hours: {hours}, Minutes: {minutes}, {x}")


print(poeng_df.sort_values())