from datetime import datetime
import pandas as pd

turnuser = [{ 
        "OSL_01": {
            "1": {
                "1": {
                    "navn": "Mandag",
                    "uke": "Uke1",
                    "tid": [
                        "6:00",
                        "14:00"
                    ],
                    "x0": [
                        56.639977344,
                        85.19996592
                    ],
                    "dagsverk": "9324-X"
                },
                "2": {
                    "navn": "Tirsdag",
                    "uke": "Uke1",
                    "tid": [
                        "XX"
                    ],
                    "x0": [
                        134.39994624
                    ],
                    "dagsverk": ""
                },
                "3": {
                    "navn": "Onsdag",
                    "uke": "Uke1",
                    "tid": [
                        "OO"
                    ],
                    "x0": [
                        191.63992334399998
                    ],
                    "dagsverk": ""
                },
                "4": {
                    "navn": "Torsdag",
                    "uke": "Uke1",
                    "tid": [
                        "9:40",
                        "19:06"
                    ],
                    "x0": [
                        239.159904336,
                        271.19989152
                    ],
                    "dagsverk": "1429"
                },
                "5": {
                    "navn": "Fredag",
                    "uke": "Uke1",
                    "tid": [
                        "14:01",
                        "21:42"
                    ],
                    "x0": [
                        304.91987803199993,
                        335.27985182400556
                    ],
                    "dagsverk": "5005-73"
                },
                "6": {
                    "navn": "L\u00f8rdag",
                    "uke": "Uke1",
                    "tid": [
                        "16:07",
                        "22:38"
                    ],
                    "x0": [
                        367.79985288,
                        395.3998277760056
                    ],
                    "dagsverk": "1235"
                },
                "7": {
                    "navn": "S\u00f8ndag",
                    "uke": "Uke1",
                    "tid": [
                        "13:00",
                        "21:00"
                    ],
                    "x0": [
                        418.19983271999996,
                        449.3998061760056
                    ],
                    "dagsverk": "9306"
                }
            },
            "2": {
                "1": {
                    "navn": "Mandag",
                    "uke": "Uke1",
                    "tid": [
                        "TT"
                    ],
                    "x0": [
                        76.919969232
                    ],
                    "dagsverk": ""
                },
                "2": {
                    "navn": "Tirsdag",
                    "uke": "Uke1",
                    "tid": [
                        "8:01",
                        "17:29"
                    ],
                    "x0": [
                        119.39995223999999,
                        151.439939424
                    ],
                    "dagsverk": "5018"
                },
                "3": {
                    "navn": "Onsdag",
                    "uke": "Uke1",
                    "tid": [
                        "6:00",
                        "14:00"
                    ],
                    "x0": [
                        172.439931024,
                        200.9999196
                    ],
                    "dagsverk": "9303"
                },
                "4": {
                    "navn": "Torsdag",
                    "uke": "Uke1",
                    "tid": [
                        "5:30",
                        "15:00"
                    ],
                    "x0": [
                        229.079908368,
                        261.239895504
                    ],
                    "dagsverk": "905301500"
                },
                "5": {
                    "navn": "Fredag",
                    "uke": "Uke1",
                    "tid": [
                        "5:00",
                        "13:00"
                    ],
                    "x0": [
                        285.71988571199995,
                        314.2798602240056
                    ],
                    "dagsverk": "9301"
                },
                "6": {
                    "navn": "L\u00f8rdag",
                    "uke": "Uke1",
                    "tid": [
                        "XX"
                    ],
                    "x0": [
                        365.879853648
                    ],
                    "dagsverk": ""
                },
                "7": {
                    "navn": "S\u00f8ndag",
                    "uke": "Uke1",
                    "tid": [
                        "OO"
                    ],
                    "x0": [
                        423.239830704
                    ],
                    "dagsverk": ""
                }
            },
            "3": {
                "1": {
                    "navn": "Mandag",
                    "uke": "Uke1",
                    "tid": [
                        "XX"
                    ],
                    "x0": [
                        76.559969376
                    ],
                    "dagsverk": ""
                },
                "2": {
                    "navn": "Tirsdag",
                    "uke": "Uke1",
                    "tid": [
                        "OO"
                    ],
                    "x0": [
                        133.79994648000002
                    ],
                    "dagsverk": ""
                },
                "3": {
                    "navn": "Onsdag",
                    "uke": "Uke1",
                    "tid": [
                        "15:00",
                        "23:00"
                    ],
                    "x0": [
                        191.519923392,
                        222.71991091200002
                    ],
                    "dagsverk": "9309"
                },
                "4": {
                    "navn": "Torsdag",
                    "uke": "Uke1",
                    "tid": [
                        "14:00",
                        "22:00"
                    ],
                    "x0": [
                        246.95990121599996,
                        278.15987467200557
                    ],
                    "dagsverk": "9308"
                },
                "5": {
                    "navn": "Fredag",
                    "uke": "Uke1",
                    "tid": [
                        "15:00",
                        "23:00"
                    ],
                    "x0": [
                        307.19987712,
                        338.39985057600563
                    ],
                    "dagsverk": "9329-X"
                },
                "6": {
                    "navn": "L\u00f8rdag",
                    "uke": "Uke1",
                    "tid": [
                        "23:00",
                        "7:00"
                    ],
                    "x0": [
                        384.479846208,
                        415.55981971200566
                    ],
                    "dagsverk": "9312"
                },
                "7": {
                    "navn": "S\u00f8ndag",
                    "uke": "Uke1",
                    "tid": [
                        "23:45",
                        "7:36"
                    ],
                    "x0": [
                        444.11982235199997,
                        474.9597959520056
                    ],
                    "dagsverk": "1775"
                }
            },
            "4": {
                "1": {
                    "navn": "Mandag",
                    "uke": "Uke1",
                    "tid": [],
                    "x0": [],
                    "dagsverk": ""
                },
                "2": {
                    "navn": "Tirsdag",
                    "uke": "Uke1",
                    "tid": [
                        "TT"
                    ],
                    "x0": [
                        134.759946096
                    ],
                    "dagsverk": ""
                },
                "3": {
                    "navn": "Onsdag",
                    "uke": "Uke1",
                    "tid": [
                        "8:01",
                        "17:29"
                    ],
                    "x0": [
                        177.239929104,
                        209.39991623999998
                    ],
                    "dagsverk": "5018"
                },
                "4": {
                    "navn": "Torsdag",
                    "uke": "Uke1",
                    "tid": [
                        "7:13",
                        "15:01"
                    ],
                    "x0": [
                        233.279906688,
                        261.239895504
                    ],
                    "dagsverk": "5014"
                },
                "5": {
                    "navn": "Fredag",
                    "uke": "Uke1",
                    "tid": [
                        "7:17",
                        "15:17"
                    ],
                    "x0": [
                        291.23988350400003,
                        319.79985801600566
                    ],
                    "dagsverk": "1424-Mod1"
                },
                "6": {
                    "navn": "L\u00f8rdag",
                    "uke": "Uke1",
                    "tid": [
                        "XX"
                    ],
                    "x0": [
                        365.879853648
                    ],
                    "dagsverk": ""
                },
                "7": {
                    "navn": "S\u00f8ndag",
                    "uke": "Uke1",
                    "tid": [
                        "OO"
                    ],
                    "x0": [
                        423.239830704
                    ],
                    "dagsverk": ""
                }
            },
            "5": {
                "1": {
                    "navn": "Mandag",
                    "uke": "Uke1",
                    "tid": [
                        "XX"
                    ],
                    "x0": [
                        76.559969376
                    ],
                    "dagsverk": ""
                },
                "2": {
                    "navn": "Tirsdag",
                    "uke": "Uke1",
                    "tid": [
                        "23:37",
                        "7:31"
                    ],
                    "x0": [
                        154.439938224,
                        185.279925888
                    ],
                    "dagsverk": "1576"
                },
                "3": {
                    "navn": "Onsdag",
                    "uke": "Uke1",
                    "tid": [
                        "21:39",
                        "5:45"
                    ],
                    "x0": [
                        207.479917008,
                        238.919904432
                    ],
                    "dagsverk": "1567"
                },
                "4": {
                    "navn": "Torsdag",
                    "uke": "Uke1",
                    "tid": [],
                    "x0": [],
                    "dagsverk": ""
                },
                "5": {
                    "navn": "Fredag",
                    "uke": "Uke1",
                    "tid": [
                        "OO"
                    ],
                    "x0": [
                        307.439877024
                    ],
                    "dagsverk": ""
                },
                "6": {
                    "navn": "L\u00f8rdag",
                    "uke": "Uke1",
                    "tid": [
                        "7:35",
                        "15:47"
                    ],
                    "x0": [
                        349.919860032,
                        378.9598343520056
                    ],
                    "dagsverk": "1607"
                },
                "7": {
                    "navn": "S\u00f8ndag",
                    "uke": "Uke1",
                    "tid": [
                        "7:43",
                        "16:20"
                    ],
                    "x0": [
                        408.119836752,
                        438.11981068800566
                    ],
                    "dagsverk": "1705"
                }
            },
            "6": {
                "1": {
                    "navn": "Mandag",
                    "uke": "Uke1",
                    "tid": [
                        "14:36",
                        "22:23"
                    ],
                    "x0": [
                        74.75997009599999,
                        105.359957856
                    ],
                    "dagsverk": "3008"
                },
                "2": {
                    "navn": "Tirsdag",
                    "uke": "Uke1",
                    "tid": [
                        "13:31",
                        "21:23"
                    ],
                    "x0": [
                        130.07994796799997,
                        160.91993563199998
                    ],
                    "dagsverk": "3006"
                },
                "3": {
                    "navn": "Onsdag",
                    "uke": "Uke1",
                    "tid": [
                        "14:00",
                        "22:00"
                    ],
                    "x0": [
                        189.11992435199997,
                        220.19991191999998
                    ],
                    "dagsverk": "9327-X"
                },
                "4": {
                    "navn": "Torsdag",
                    "uke": "Uke1",
                    "tid": [
                        "TT"
                    ],
                    "x0": [
                        250.559899776
                    ],
                    "dagsverk": ""
                },
                "5": {
                    "navn": "Fredag",
                    "uke": "Uke1",
                    "tid": [
                        "6:00",
                        "15:00"
                    ],
                    "x0": [
                        288.239884704,
                        319.07985830400565
                    ],
                    "dagsverk": "9906001500-H"
                },
                "6": {
                    "navn": "L\u00f8rdag",
                    "uke": "Uke1",
                    "tid": [
                        "XX"
                    ],
                    "x0": [
                        365.879853648
                    ],
                    "dagsverk": ""
                },
                "7": {
                    "navn": "S\u00f8ndag",
                    "uke": "Uke1",
                    "tid": [
                        "OO"
                    ],
                    "x0": [
                        423.239830704
                    ],
                    "dagsverk": ""
                }
            }
        }
    }]



FIRDAGER = [['XX'], ['TT'], ['OO'], []]


def create_dataframe(dict):

    df = pd.DataFrame()


    for turnus in dict:
        for turnus_navn, turnus_data in turnus.items():
            for uke, uke_data in turnus_data.items():
                for dag, dag_data in uke_data.items():
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
                    df = df._append(new_row, ignore_index = True)

    return df

df = create_dataframe(turnuser)

df_search = df.copy()

df_search['Start'] = pd.to_datetime(df['Start'], format="%H:%M")
df_search['Slutt'] = pd.to_datetime(df['Slutt'], format="%H:%M")

df_start = df_search.set_index('Start')
df_start = df_start.between_time('09:00', '18:00')

df_slutt = df_search.set_index('Slutt')
df_slutt = df_slutt.between_time('21:00', '22:00')


# Find entries that are in both DataFrames
df_filtered = pd.merge(df_start, df_slutt, how='inner')




mask_lordag = df.isin(['Lørdag']).any(axis=1)
mask_sondag = df.isin(['Søndag']).any(axis=1)
mask_fri = df.isin(['FRI']).any(axis=1)


df_lordag_and_fri = df[mask_lordag & mask_fri]
df_sondag_and_fri = df[mask_sondag & mask_fri]

print(len(df_lordag_and_fri))
print(df)