import pdfplumber
import pandas as pd
import copy
from datetime import datetime, time
import xlsxwriter



# Intitial Constants
word_crossover_tolerance = 12
turnus_teller = 1

linje_teller = 0

word_remove_filter = ['Materiell:', 'Ruteterminperiode:', 'start:', 'Rutetermin:', 'Turnus:', 'Stasjoneringssted:']
word_allow_filter = [':', 'XX', 'OO', 'TT']


# Get today's date
turnus_start_dato = datetime(2022, 12, 11)


# Dimensjoner
# Y-pos: top, bottom
turnus_1_pos = [{1:(88, 115)}, {2:(115, 142)}, {3:(142, 168)}, {4:(168, 195)}, {5:(195, 222)}, {6:(222, 248)}]
turnus_2_pos = [{1:(374, 401)}, {2:(402, 427)}, {3:(428, 454)}, {4:(455, 480)}, {5:(481, 507)}, {6:(508, 533)}]
# X-pos:
dag_pos = [{1:(51, 109)}, {2:(110, 167)}, {3:(167, 224)}, {4:(225, 283)}, 
           {5:(284, 340)}, {6:(341, 399)}, {7:(400, 456)}]



###
### Fjernet dag åtte: , {8:(458, 514)}

pdf = pdfplumber.open('turnus.pdf')
page = pdf.pages[0]

text_objects = page.extract_words(x_tolerance = 1, y_tolerance = 1)

turnuser = []

turnus_mal = {1:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}},

            2:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}},
            
            3:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}},
            
            4:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}},
            
            5:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}},
            
            6:{
                1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}, 
                6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]},
                7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':[]}},
            }


def sorter_turnus_side(page):
    text_objects = page.extract_words(x_tolerance = 1, y_tolerance = 1)

    turnus_1_navn = text_objects[21]["text"][:-1] + " " + text_objects[23]["text"]
    turnus_2_navn = text_objects[164]["text"][:-1] + " " + text_objects[166]["text"]
    turnus1 = copy.deepcopy(turnus_mal)
    turnus2 = copy.deepcopy(turnus_mal)


    for word in text_objects:
        

        # Filtrerer ut hva som skal med videre fra pdf-en
        if (":" in word["text"] or any(sub in word["text"] for sub in word_allow_filter)) and word["text"] not in word_remove_filter:

            
            # Siler ut hvilken turnus (1 eller 2)
            if int(word['top']) >= turnus_1_pos[0][1][0] and int(word['bottom']) <= turnus_1_pos[5][6][1]:
                
                for uker in turnus_1_pos:  
                    for uke, uke_verdi in uker.items():
                        if word['top'] >= uke_verdi[0] and word['bottom'] <= uke_verdi[1]:
                            
                            for dager in dag_pos:
                                for dag, verdi in dager.items():
                                    if word['x0'] >= verdi[0] and word['x1'] <= verdi[1]+word_crossover_tolerance:
                                        

                
                                        if dag == 8:
                                            pass

                                        if (uke == 1 and dag == 1) or word['text'] in word_allow_filter:
                                            turnus1[uke][dag]['tid'].append(word['text'])
                                            turnus1[uke][dag]['x0'].append(word['x0'])
                                        
                                        elif uke > 1 and dag == 1:
                                            if word['x0'] in turnus1[uke-1][7]['x0']:
                                                pass
                                            if any(val in turnus1[uke-1][7]['tid'] for val in word_allow_filter):
                                                turnus1[uke][dag]['tid'].append(word['text'])
                                                turnus1[uke][dag]['x0'].append(word['x0'])
                                            elif len(turnus1[uke-1][7]['tid']) == 1:
                                                turnus1[uke-1][7]['tid'].append(word['text'])
                                                turnus1[uke-1][7]['x0'].append(word['x0'])
                                            else:
                                                turnus1[uke][dag]['tid'].append(word['text'])
                                                turnus1[uke][dag]['x0'].append(word['x0'])

                                        
                                        elif uke >= 1 and dag > 1:
                                            if word['x0'] in turnus1[uke][dag-1]['x0']:
                                                pass
                                            elif any(val in turnus1[uke][dag-1]['tid'] for val in word_allow_filter):
                                                turnus1[uke][dag]['tid'].append(word['text'])
                                                turnus1[uke][dag]['x0'].append(word['x0'])
                                            elif len(turnus1[uke][dag-1]['tid']) == 1:
                                                turnus1[uke][dag-1]['tid'].append(word['text'])
                                                turnus1[uke][dag-1]['x0'].append(word['x0'])
                                            else:
                                                turnus1[uke][dag]['tid'].append(word['text'])
                                                turnus1[uke][dag]['x0'].append(word['x0'])

                                        else:
                                            turnus1[uke][dag]['tid'].append(word['text'])
                                            turnus1[uke][dag]['x0'].append(word['x0'])   




            elif int(word['top']) >= turnus_2_pos[0][1][0]:
                
                for uker in turnus_2_pos:  
                    for uke, uke_verdi in uker.items():
                        if word['top'] >= uke_verdi[0] and word['bottom'] <= uke_verdi[1]:
                            
                            for dager in dag_pos:
                                for dag, verdi in dager.items():
                                    if word['x0'] >= verdi[0] and word['x1'] <= verdi[1]+word_crossover_tolerance:
                
                                        if dag == 8:
                                            pass
                                        
                                        if (uke == 1 and dag == 1) or word['text'] in word_allow_filter:
                                            turnus2[uke][dag]['tid'].append(word['text'])
                                            turnus2[uke][dag]['x0'].append(word['x0'])
                                            
                                        
                                        elif uke > 1 and dag == 1:
                                            if word['x0'] in turnus2[uke-1][7]['x0']:
                                                pass
                                            if any(val in turnus2[uke-1][7]['tid'] for val in word_allow_filter):
                                                turnus2[uke][dag]['tid'].append(word['text'])
                                                turnus2[uke][dag]['x0'].append(word['x0'])
                                            elif len(turnus2[uke-1][7]['tid']) == 1:
                                                turnus2[uke-1][7]['tid'].append(word['text'])
                                                turnus2[uke-1][7]['x0'].append(word['x0'])
                                            else:
                                                turnus2[uke][dag]['tid'].append(word['text'])
                                                turnus2[uke][dag]['x0'].append(word['x0'])

                                        
                                        elif uke >= 1 and dag > 1:
                                            if word['x0'] in turnus2[uke][dag-1]['x0']:
                                                pass
                                            elif any(val in turnus2[uke][dag-1]['tid'] for val in word_allow_filter):
                                                turnus2[uke][dag]['tid'].append(word['text'])
                                                turnus2[uke][dag]['x0'].append(word['x0'])
                                            elif len(turnus2[uke][dag-1]['tid']) == 1:
                                                turnus2[uke][dag-1]['tid'].append(word['text'])
                                                turnus2[uke][dag-1]['x0'].append(word['x0'])
                                            else:
                                                turnus2[uke][dag]['tid'].append(word['text'])
                                                turnus2[uke][dag]['x0'].append(word['x0'])

                                        else:
                                            turnus2[uke][dag]['tid'].append(word['text'])
                                            turnus2[uke][dag]['x0'].append(word['x0'])  



    #sidens_turnuser =  [{turnus_1_navn:turnus1}, {turnus_2_navn:turnus2}]
    turnuser.append({turnus_1_navn:turnus1})
    turnuser.append({turnus_2_navn:turnus2})               


def create_excel(turnus):
    
    df_dict = {}
    
    



    for turnus_navn, turnus_verdi in turnus.items():
        data = {
        'Uke': [1, 2, 3, 4, 5, 6],
        'Mandag': [],
        'Tirsdag': [],
        'Onsdag': [],
        'Torsdag': [],
        'Fredag': [],
        'Lørdag': [],
        'Søndag': []}
        
        for uke_nr, uke in turnus_verdi.items():
            for dag_nr, dag in uke.items():
                
                if len(dag['tid']) == 0:
                    data[dag['navn']].append('')
                else:
                    
   
                    data[dag['navn']].append(" - ".join(dag['tid']))

        df_dict[turnus_navn] = pd.DataFrame(data)



    
    with pd.ExcelWriter("output.xlsx", engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            print(df)

            df.to_excel(writer, sheet_name=sheet_name, index=False)
            workbook  = writer.book
            worksheet = writer.sheets[sheet_name]
            
        


            # Define a format for the cell background color.
            tidlig_format = workbook.add_format({'bg_color': '#7abfff',
                                                'font_color': '#000000'})
            tidlig_kveld_format = workbook.add_format({'bg_color': '#e6bc4c',
                                                'font_color': '#000000'})
            kveld_format = workbook.add_format({'bg_color': '#ed7777',
                                                'font_color': '#000000'})
            natt_format = workbook.add_format({'bg_color': '#4a4a4a',
                                                'font_color': '#ffffff'})
            fridag_format = workbook.add_format({'bg_color': '#13bd57',
                                                'font_color': '#ffffff'})
            centered_format = workbook.add_format({
                                                'align': 'center',
                                                'valign': 'vcenter',
                                                'border':1})

            # Get the default column width for the Age column.
            col_width = max(df['Tirsdag'].astype(str).apply(len))



            # Set column width and conditional format for the Age column.
            worksheet.set_column('B:H', col_width + 2)  # Add 2 for aesthetics.
            
            
            # Apply centered text and borders for the range 'A1:H6'.
            for row in range(6):
                for col, column_label in enumerate(df.columns):
                    cell_value = df.at[row, column_label]
                    worksheet.write(row + 1, col, cell_value, centered_format) # +1 to account for header row

            
            # Logikken for hvilke celler som blir farget.
            for col in range(1, 8):  # Columns B(1) through H(7)
                for row in range(1, 7):  # Rows 2 through 7
                    cell = xlsxwriter.utility.xl_rowcol_to_cell(row, col)
                    worksheet.conditional_format(cell, {'type': 'formula',
                                                        'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=3)' 
                                                        'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1)) < 16)'
                                                        'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) < 16)',
                                                        'format': tidlig_format})
                    worksheet.conditional_format(cell, {'type': 'formula',
                                                        'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=3)'
                                                        'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1)) <= 8)'
                                                        'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) >= 16)',
                                                        'format': tidlig_kveld_format})                
                    worksheet.conditional_format(cell, {'type': 'formula',
                                                        'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=9)'
                                                        'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))<=17)'
                                                        'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) >= 16)',
                                                        'format': kveld_format})
                    worksheet.conditional_format(cell, {'type': 'formula',
                                                        'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=18)'
                                                        'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))<=23)',
                                                        'format': natt_format})
                    worksheet.conditional_format(cell, {'type': 'formula',
                                                        'criteria': '=(' + cell + '="")',
                                                        'format': natt_format})
                    worksheet.conditional_format(cell, {'type': 'formula',
                                                        'criteria': '=(' + cell + '="XX")' 'OR (' + cell + '="OO")' 'OR (' + cell + '="TT")',
                                                        'format': fridag_format})

                             

sorter_turnus_side(page)      

for turnus_lst in turnuser:
    create_excel(turnus_lst)





# for turnus in turnuser[0]:
    
#     for turnus, turnus_value in turnus.items():

#             for uke_nr, uke_value in turnus_value.items():
#                 for g, h in uke_value.items():
#                     print(turnus, uke_nr, g, h['tid'], "-", h['x0'])
#                     print(" ")
