import pdfplumber

# Intitial Constants
word_crossover_tolerance = 20
turnus_teller = 1

linje_teller = 0

word_remove_filter = ['Materiell:', 'Ruteterminperiode:', 'start:', 'Rutetermin:', 'Turnus:', 'Stasjoneringssted:']
word_allow_filter = [':', 'XX', 'OO', 'TT']

# Dimensjoner

# Y-pos: top, bottom
turnus_1_pos = [{'Uke1':(88, 115)}, {'Uke2':(115, 142)}, {'Uke3':(142, 168)}, {'Uke4':(168, 195)}, {'Uke5':(195, 222)}, {'Uke6':(222, 248)}]
turnus_2_pos = [{'Uke1':(374, 401)}, {'Uke2':(402, 427)}, {'Uke3':(428, 454)}, {'Uke4':(455, 480)}, {'Uke5':(481, 506)}, {'Uke6':(507, 533)}]
# X-pos:
dag_pos = [{'Mandag':(51, 109)}, {'Tirsdag':(110, 167)}, {'Onsdag':(167, 224)}, {'Torsdag':(225, 283)}, 
           {'Fredag':(284, 340)}, {'Lørdag':(341, 399)}, {'Søndag':(400, 456)}, {'Mandag-2':(458, 514)}]

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

turnus_1_navn = text_objects[21]["text"] + " " + text_objects[23]["text"]
turnus_2_navn = text_objects[164]["text"] + " " + text_objects[166]["text"]

side = [{turnus_1_navn: [{'Uke1':[]}]}]

for word in text_objects:
    # Filtrerer ut hva som skal med videre fra pdf-en
    if (":" in word["text"] or any(sub in word["text"] for sub in word_allow_filter)) and word["text"] not in word_remove_filter:
        
        # Siler ut hvilken turnus (1 eller 2)
        if word['top'] >= turnus_1_pos[0]["Uke1"][0] and word['bottom'] <= turnus_1_pos[5]['Uke6'][1]:
            
            for uke in turnus_1_pos:  
                for key, value in uke.items():
                    if word['top'] >= value[0] and word['bottom'] <= value[1]:
                        #print(word['text'], ' - ', key)
                        
                        for dager in dag_pos:
                            for dag, verdi in dager.items():
                                if word['x0'] >= verdi[0] and word['x1'] <= verdi[1]:
                                    print(word['text'], '-', dag, verdi)
                                    print(key)
                                    side[0][turnus_1_navn][key].append[word['text']]
                        



    
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


print(side)

# for dag_x in dag_pos:
#     print(dag_x)
#     for key, value in dag_x.items():
#         print(key, value[1])