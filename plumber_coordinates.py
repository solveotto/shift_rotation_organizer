import pdfplumber

# Intitial Constants
word_crossover_tolerance = 20
turnus_teller = 1

linje_teller = 0

word_remove_filter = ['Materiell:', 'Ruteterminperiode:', 'start:', 'Rutetermin:', 'Turnus:', 'Stasjoneringssted:']
word_allow_filter = [':', 'XX', 'OO', 'TT']

# Dimensjoner

# Y-pos: top, bottom
turnus_1_pos = [{1:(88, 115)}, {2:(115, 142)}, {3:(142, 168)}, {4:(168, 195)}, {5:(195, 222)}, {6:(222, 248)}]
turnus_2_pos = [{7:(374, 401)}, {8:(402, 427)}, {9:(428, 454)}, {10:(455, 480)}, {11:(481, 506)}, {12:(507, 533)}]
# X-pos:
dag_pos = [{1:(51, 109)}, {2:(110, 167)}, {3:(167, 224)}, {4:(225, 283)}, 
           {5:(284, 340)}, {6:(341, 399)}, {7:(400, 456)}, {8:(458, 514)}]

new_table_dict = {"turnus1":
                  {"Mandag":[], "Tirsdag":[], "Onsdag":[], 
                   "Torsdag":[], "Fredag":[], "Lørdag":[], "Søndag":[], "Mandag_2":[]},
                  "turnus2": 
                  {"Mandag":[], "Tirsdag":[], "Onsdag":[], 
                   "Torsdag":[], "Fredag":[], "Lørdag":[], "Søndag":[], "Mandag_2":[]}
                   }



pdf = pdfplumber.open('turnus.pdf')
page = pdf.pages[0]

text_objects = page.extract_words(x_tolerance = 1, y_tolerance = 1)

turnuser = []

turnus_mal = {1:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                2:{'navn':'Tirdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                5:{'navn': 'Fredag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}},

            2:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                2:{'navn':'Tirdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}},
            
            3:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                2:{'navn':'Tirdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}},
            
            4:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                2:{'navn':'Tirdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}},
            
            5:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                2:{'navn':'Tirdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}},
            
            6:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                2:{'navn':'Tirdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'dagsverk':[]}},
            }


def sorter_turnus_side(page):
    text_objects = page.extract_words(x_tolerance = 1, y_tolerance = 1)

    turnus_1_navn = text_objects[21]["text"] + " " + text_objects[23]["text"]
    turnus_2_navn = text_objects[164]["text"] + " " + text_objects[166]["text"]

    sidens_turnuser =  [{turnus_1_navn:turnus_mal}, {turnus_2_navn:turnus_mal}]

    for word in text_objects:
        # Filtrerer ut hva som skal med videre fra pdf-en
        if (":" in word["text"] or any(sub in word["text"] for sub in word_allow_filter)) and word["text"] not in word_remove_filter:
            
            # Siler ut hvilken turnus (1 eller 2)
            if word['top'] >= turnus_1_pos[0][1][0] and word['bottom'] <= turnus_1_pos[5][6][1]:
                
                for uker in turnus_1_pos:  
                    for uke, uke_verdi in uker.items():
                        if word['top'] >= uke_verdi[0] and word['bottom'] <= uke_verdi[1]:
                            
                            for dager in dag_pos:
                                for dag, verdi in dager.items():
                                    if word['x0'] >= verdi[0] and word['x1'] <= verdi[1]+word_crossover_tolerance:
                
                                        if dag == 8:
                                            dag = 7

                                        sidens_turnuser[0][turnus_1_navn][uke][dag]['tid'].append(word['text'])
    turnuser.append(sidens_turnuser)                      

                                    

sorter_turnus_side(page)      
                        

for turnus in turnuser[0]:
    for turnus, turnus_value in turnus.items():
        for uke_nr, uke_value in turnus_value.items():
            for g, h in uke_value.items():
                print(turnus, uke_nr, h['tid'])
                print(" ")

    
    # for linje in uke_pos:
    #     if word["top"] >= linje[0] and word["bottom"] <= linje[1]:
    #         for dag in dag_pos:
    #             if word["x0"] >= dag[0]+word_crossover_tolerance and word["x1"] <= dag[1]+word_crossover_tolerance:
    #                 if uke_pos.index(linje) >= 0 and uke_pos.index(linje) <= 6:
    #                     if dag_pos.index(dag) == 0:
    #                         new_table_dict["turnus1"]["Mandag"].append(word["text"])
    #                     elif dag_pos.index(dag) == 1:
    #                         new_table_dict["turnus1"]["Tirsdag"].append(word["text"])
    #                 break


        # if word["x0"] > dag_pos["Mandag"][0] and word['x1'] < dag_pos["Mandag"][1]+word_crossover_tolerance:
        #     new_table_dict["uke1"]["Mandag"].append(word["text"])
        # elif word["x0"] > dag_pos["Tirsdag"][0] and word['x1'] < dag_pos["Tirsdag"][1]+word_crossover_tolerance:
        #     new_table_dict["uke1"]["Tirsdag"].append(word["text"])
        # elif word["x0"] > dag_pos["Onsdag"][0] and word['x1'] < dag_pos["Onsdag"][1]+word_crossover_tolerance:
        #     new_table_dict["uke1"]["Onsdag"].append(word["text"])

