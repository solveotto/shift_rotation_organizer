import pdfplumber

# Intitial Constants
word_crossover_tolerance = 20
turnus_teller = 1

linje_teller = 0


# Dimensjoner

# Y-pos: top, bottom
uke_pos = [(88, 114), (115, 141), (142, 167), (168, 194), (195, 221), (222, 247), 
           (374, 401), (402, 427), (428, 454), (455, 480), (481, 506), (507, 533)]
# X-pos: left, right. Man, Tirs, Ons, Tors, Fred, Lørd, Sønd, Mand2
dag_pos = [(51, 109), (110, 167), (167, 225),]

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


def sort_days(word, uke, dag, uke_xy_verdi, dag_xy_verdi):
    print(word,uke,dag)
    if word["x0"] > dag_pos[dag][0] and word['x1'] < dag_pos[dag][0]+word_crossover_tolerance:
        new_table_dict[uke][dag].append(word["text"])


for word in text_objects:
    print(word["text"], text_objects.index(word))
    for linje in uke_pos:
        if word["top"] >= linje[0] and word["bottom"] <= linje[1]:
            for dag in dag_pos:
                if word["x0"] >= dag[0]+word_crossover_tolerance and word["x1"] <= dag[1]+word_crossover_tolerance:
                    if uke_pos.index(linje) >= 0 and uke_pos.index(linje) <= 6:
                        if dag_pos.index(dag) == 0:
                            new_table_dict["turnus1"]["Mandag"].append(word["text"])
                        elif dag_pos.index(dag) == 1:
                            new_table_dict["turnus1"]["Tirsdag"].append(word["text"])
                    break


        # if word["x0"] > dag_pos["Mandag"][0] and word['x1'] < dag_pos["Mandag"][1]+word_crossover_tolerance:
        #     new_table_dict["uke1"]["Mandag"].append(word["text"])
        # elif word["x0"] > dag_pos["Tirsdag"][0] and word['x1'] < dag_pos["Tirsdag"][1]+word_crossover_tolerance:
        #     new_table_dict["uke1"]["Tirsdag"].append(word["text"])
        # elif word["x0"] > dag_pos["Onsdag"][0] and word['x1'] < dag_pos["Onsdag"][1]+word_crossover_tolerance:
        #     new_table_dict["uke1"]["Onsdag"].append(word["text"])


print(text_objects[23]["text"])
print(text_objects[21]["text"] + text_objects[22]["text "])