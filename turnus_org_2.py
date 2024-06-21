from datetime import datetime
import pandas as pd
import json


with open('turnuser_R24.json', 'r') as f:
    turnuser_dict = json.load(f)

FIRDAGER = [['XX'], ['TT'], ['OO'], []]



df = pd.DataFrame()
df_result = pd.DataFrame(columns=['Turnus', 'Poeng'])


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
                df = df._append(new_row, ignore_index = True)


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

turnus_lst = []

df_grpby_turnus = df.groupby('Turnus')
for turnus_navn, turnus_df in df_grpby_turnus:
    poeng = 0

    # 3. helgfri (10p)
    df_helgefri = turnus_df.reset_index()
    frihelg_count = 0

    for _index, _dagsverk in df_helgefri.iterrows():
        if _index + 1 < len(df_helgefri):
            if _dagsverk['dagsverk_type'] == 'FRI' and _dagsverk['ukedag'] == 'Lørdag':
                new_row = df_helgefri.iloc[_index + 1]
                if new_row['dagsverk_type'] == 'FRI' and new_row['ukedag'] == 'Søndag':
                    frihelg_count += 1
    if frihelg_count > 3:
        poeng += 10

    
    #turnus_lst.append({turnus_navn: poeng})


#print(turnus_lst)