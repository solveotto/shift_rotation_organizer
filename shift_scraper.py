import pdfplumber
import pandas as pd
import copy
from datetime import datetime
import xlsxwriter
import json



class PdfScraper():
    def __init__(self, pdf_path) -> None:
        

        ### Intitial Constants ###

        # Dagens dato
        self.TURNUS_START_DATO = datetime(2022, 12, 11)
        # Dimensjoner for hver tabellen
        # Y-akse: fra øverste til nederste verdi
        self.TURNUS_1_POS = [{1:(88, 115)}, {2:(115, 142)}, {3:(142, 168)}, {4:(168, 195)}, 
                        {5:(195, 222)}, {6:(222, 248)}]
        self.TURNUS_2_POS = [{1:(374, 401)},{2:(402, 427)}, {3:(428, 454)}, {4:(455, 480)}, 
                        {5:(481, 507)}, {6:(508, 533)}]
        # X-akse: fra venstre til høyre
        self.DAG_POS = [{1:(51, 109)}, {2:(109, 167)}, {3:(167, 224)}, {4:(224, 283)}, {5:(283, 340)}, 
                    {6:(340, 399)}, {7:(399, 514)}]
        self.REMOVE_FILTER = ['Materiell:', 'Ruteterminperiode:', 'start:', 'Rutetermin:',
                            'Turnus:', 'Stasjoneringssted:', 'OSL', 'HLD']
        self.ALLOW_FILTER = [':', 'XX', 'OO', 'TT']
        self.FRIDAG_FILTER = ['XX', 'OO', 'TT']
        self.INPUT_PATH = pdf_path
        self.OUTPUT_PATH = 'turnuser_R24.xlsx'
        PDF = pdfplumber.open(pdf_path)
        self.PAGES_IN_PDF = PDF.pages


        self.turnuser = []

        

        # Lager JSON-fil
        with open('turnuser_R24.json', 'w') as f:
            json.dump(turnuser, f, indent=4)

        # Lager excel av de sorterte turnusene
        create_excel(turnuser)


    def scrape_pdf(self):
        # Sorterer objektene som er tatt ut av PDF-en
        for page in self.PAGES_IN_PDF:
            sorterte_turnuser = self.sorter_side(page)
            for sortert_turnus in sorterte_turnuser:
                self.turnuser.append(sortert_turnus)



    def sorter_side(self, page):

        def sorter_turnus(search_obj):
            for txt_obj in text_objects:
                if int(txt_obj['x0']) >= DAG_POS[0][1][0] and int(txt_obj['x1']) <= DAG_POS[6][7][1]:
                    # Siler ut hvilken turnus (1 eller 2)
                    if int(txt_obj['top']) >= TURNUS_1_POS[0][1][0] and int(txt_obj['bottom']) <= TURNUS_1_POS[5][6][1]:
                        uker_dag_iterering(txt_obj, TURNUS_1_POS, turnus1, search_obj)
                    elif int(txt_obj['top']) >= TURNUS_2_POS[0][1][0] and int(txt_obj['bottom']) <= TURNUS_2_POS[5][6][1]:    
                        uker_dag_iterering(txt_obj, TURNUS_2_POS, turnus2, search_obj)


        # Sjekker om objektet er innenfor verdiene til tabellen
        def objektet_innenfor_uke_dag(word, uke_verdi, dag_verdi):
            return (
                word['top'] >= uke_verdi[0]
                and word['bottom'] <= uke_verdi[1]
                and word['x0'] >= dag_verdi[0]
                and word['x0'] <= dag_verdi[1]
                and word['text'] not in REMOVE_FILTER
            )
        
        # Pakker ut uker og dager og mater det inn i plasseringslogikk
        def uker_dag_iterering(text_obj, turnus_pos, turnus, search_obj):
            for uker in turnus_pos:
                for uke, uke_verdi in uker.items():
                    for dager in DAG_POS:
                        for dag, dag_verdi in dager.items():
                            if objektet_innenfor_uke_dag(text_obj, uke_verdi, dag_verdi):
                                if search_obj == 'tid':
                                    plasseringslogikk_tid(text_obj, uke, dag, turnus)
                                elif search_obj == 'dagsverk':
                                    plasseringslogikk_dagsverk(text_obj, uke, dag, turnus)


        def plasseringslogikk_tid(word, uke, dag, turnus):
            # Siler ut objektene som inneholder :, XX, OO, eller TT.
            if any(sub in word["text"] for sub in ALLOW_FILTER):
                # Hvis det er uke1 og dag 1 så skal det ikke sjekkes om objektet finnes i uken og dagen før,
                # men lagres i nåværende dag og uke.
                if (uke == 1 and dag == 1) or word['text'] in ALLOW_FILTER:
                    turnus[uke][dag]['tid'].append(word['text'])
                    turnus[uke][dag]['x0'].append(word['x0'])

                # Hvis det mandag men ikke uke1.
                elif uke != 1 and dag == 1:
                    # Hopper over objekter på mandag hvis søndagen før har to objekter,
                    # mandagen har null objekter og objektet på søndag er likt det som skal plasseres.
                    if (len(turnus[uke-1][7]['tid']) == 2 and
                        len(turnus[uke][dag]['tid']) == 0 and
                        word['text'] == turnus[uke-1][7]['tid'][1]):
                        pass
                    # hvis objektet er :, XX, OO eller TT: lagre i nåværede dag og uke
                    elif any(val in turnus[uke-1][7]['tid'] for val in ALLOW_FILTER):
                        turnus[uke][dag]['tid'].append(word['text'])
                        turnus[uke][dag]['x0'].append(word['x0'])
                    # Hvis det bare er et objekt på søndag uke over: legg objekt til søndag
                    elif len(turnus[uke-1][7]['tid']) == 1:
                        turnus[uke-1][7]['tid'].append(word['text'])
                        turnus[uke-1][7]['x0'].append(word['x0'])
                    else:
                        turnus[uke][dag]['tid'].append(word['text'])
                        turnus[uke][dag]['x0'].append(word['x0'])

                # Hvis det ikke er dag1
                elif uke >= 1 and dag > 1:
                    # Putter objekt i nåværende dag hvis dagen før er :, XX, TT, eller OO.
                    if any(val in turnus[uke][dag-1]['tid'] for val in ALLOW_FILTER):
                        turnus[uke][dag]['tid'].append(word['text'])
                        turnus[uke][dag]['x0'].append(word['x0'])
                    # Putter objekt i dagen før hvis det kun er en verdi der.
                    elif len(turnus[uke][dag-1]['tid']) == 1:
                        turnus[uke][dag-1]['tid'].append(word['text'])
                        turnus[uke][dag-1]['x0'].append(word['x0'])
                    else:
                        turnus[uke][dag]['tid'].append(word['text'])
                        turnus[uke][dag]['x0'].append(word['x0'])


        def plasseringslogikk_dagsverk(word, uke, dag, turnus):                 
            # Hopper over iterering hvis de inneholder :, XX, OO eller TT.
            if any(sub in word["text"] for sub in ALLOW_FILTER):
                pass
            else:
                # Hvis det er uke1 og dag1, lagres objektet i nåværende dag og uke.
                if (uke == 1 and dag == 1) and word['text'] not in REMOVE_FILTER:
                    turnus[uke][dag]['dagsverk'] = word['text']
                
                # Mandager som ikke er uke1
                elif uke != 1 and dag == 1:
                    # Hopper over iterering hvis dagsverket er likt dagsverket i søndagen uka før
                    # og tidene i de to dagene ikke er like.
                    if (word['text'] == turnus[uke-1][7]['dagsverk'] and 
                        turnus[uke][dag]['tid'] != turnus[uke-1][7]['tid']):
                        pass
                    # Hvis det er to verdier av TID og ingen i DAGSVERK søndag uka før, 
                    elif len(turnus[uke-1][7]['tid']) == 2 and turnus[uke-1][7]['dagsverk'] == "":
                        turnus[uke][dag-1]['dagsverk'] =  word['text']
                    else:
                        turnus[uke][dag]['dagsverk'] = word['text']
                                    
                # Hvis det ikke er dag1
                elif uke >= 1 and dag > 1:
                    if len(turnus[uke][dag-1]['tid']) == 2 and turnus[uke][dag-1]['dagsverk'] == "":
                        turnus[uke][dag-1]['dagsverk'] =  word['text']
                    else:
                        turnus[uke][dag]['dagsverk'] =  word['text']


        def generer_turnus_mal():
            uke_mal = {1:{'navn':'Mandag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""}, 
                        2:{'navn':'Tirsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""}, 
                        3:{'navn':'Onsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""}, 
                        4:{'navn':'Torsdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""},
                        5:{'navn':'Fredag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""}, 
                        6:{'navn':'Lørdag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""},
                        7:{'navn':'Søndag', 'uke':'Uke1', 'tid':[], 'x0':[], 'dagsverk':""}}
            turnus = {}

            for uke in range(1,7):
                mal_kopi = copy.deepcopy(uke_mal)
                turnus.update({uke:mal_kopi})

            return turnus


        # Henter ut alle objektene i pdf-en
        text_objects = page.extract_words(x_tolerance = 1, y_tolerance = 1)

        # Finne og navgi turns.
        for turnus_name in text_objects:
            word_pos = text_objects.index(turnus_name)
            
            if turnus_name["text"] == 'OSL':
                if turnus_name['top'] > 0 and turnus_name['top'] < 70:
                    if text_objects[word_pos+1]['text'] in ['Ramme', 'RAMME', 'Utland', 'UTLAND']:
                        turnus_1_navn = text_objects[word_pos]['text']+'_'+text_objects[word_pos+1]['text']+'_'+text_objects[word_pos+2]['text']
                    else:
                        turnus_1_navn = text_objects[word_pos]['text']+'_'+text_objects[word_pos+1]['text']
                    
                elif turnus_name['top'] > 340 and turnus_name['top'] < 360:
                    if text_objects[word_pos+1]['text'] in ['Ramme', 'RAMME', 'Utland', 'UTLAND']:
                        turnus_2_navn = text_objects[word_pos]['text']+'_'+text_objects[word_pos+1]['text']+'_'+text_objects[word_pos+2]['text']
                        print(turnus_1_navn, turnus_2_navn)
                    else:
                        turnus_2_navn = text_objects[word_pos]['text']+'_'+text_objects[word_pos+1]['text']
            else:
                pass
        turnus1 = generer_turnus_mal()
        turnus2 = generer_turnus_mal()

        # Sorterer først tiden. Sorteringen av dagsverk basserer seg på sortertetidener.
        sorter_turnus('tid')
        sorter_turnus('dagsverk')

        sorterte_turnuser_lst = []

        try:
            sorterte_turnuser_lst.append({turnus_1_navn:turnus1})
            sorterte_turnuser_lst.append({turnus_2_navn:turnus2})
        except UnboundLocalError:
            pass

        return sorterte_turnuser_lst



    def create_excel(data):
            # Lager et DataFrame av turnusene som er lagret i en Dict.
            df_dict = {}
            
            for turnus in data:
                for turnus_navn, turnus_verdi in turnus.items():
                    df_data = {'Uke': [1, 2, 3, 4, 5, 6],
                    'Mandag': [], 'Tirsdag': [], 'Onsdag': [], 'Torsdag': [],
                    'Fredag': [], 'Lørdag': [], 'Søndag': []}
                    
                    # Pakker opp turnuser i uker og dager og legger de i rikigt ukedag
                    for uke in turnus_verdi.values():
                        for dag in uke.values():
                            if len(dag['tid']) == 0:
                                df_data[dag['navn']].append('')
                            else:
                                df_data[dag['navn']].append(" - ".join(dag['tid'])+ " " + dag['dagsverk'])
                                
                    df_dict.update({turnus_navn : pd.DataFrame(df_data)})

            # Lagrer DataFrame som Excel-fil og lager et sheet i excel-filen per turnus i dataframe
            with pd.ExcelWriter(OUTPUT_PATH, engine='xlsxwriter') as writer:
                for sheet_name, df in df_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    workbook  = writer.book
                    worksheet = writer.sheets[sheet_name]
                        
                    # Define a format for the cell background color.
                    hdag_format = workbook.add_format({'bg_color': '#dbcc27',
                                                    'font_color': '#000000'})
                    tidlig_format = workbook.add_format({'bg_color': '#7abfff',
                                                        'font_color': '#000000'})
                    tidlig_kveld_format = workbook.add_format({'bg_color': '#d68f6d',
                                                        'font_color': '#000000'})
                    kveld_format = workbook.add_format({'bg_color': '#fa7f7f',
                                                        'font_color': '#000000'})
                    natt_format = workbook.add_format({'bg_color': '#c34fe3',
                                                        'font_color': '#000000'})
                    turnusfri_format = workbook.add_format({'bg_color': '#13bd57',
                                                        'font_color': '#000000'})
                    skjult_fridag_format = workbook.add_format({'bg_color': '#cc9fe3',
                                                        'font_color': '#000000',
                                                        'border':2,
                                                        'border_color': '#c34fe3'})
                    
                    centered_format = workbook.add_format({
                                                        'align': 'center',
                                                        'valign': 'vcenter',
                                                        'border':1,
                                                        'text_wrap': True})

                    # Setter høyden på COLUMNS.
                    worksheet.set_column('B:H', 12) 
                    worksheet.set_column('A:A', 4)

                    # Setter bredden på ROWS
                    for row in range(1,7):
                        worksheet.set_row(row, 40)
                    
                    # Apply centered text and borders for the range 'A1:H6'.
                    for row in range(6):
                        for col, column_label in enumerate(df.columns):
                            cell_value = df.at[row, column_label]
                            worksheet.write(row + 1, col, cell_value, centered_format)

                    
                    # Logikken for formatering av celler.
                    for col in range(1, 8):  # Columns B(1) through H(7)
                        for row in range(1, 7):  # Rows 2 through 7
                            cell = xlsxwriter.utility.xl_rowcol_to_cell(row, col)
                            
                            ## Formater ##
                            # H-Dager
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=RIGHT(' + cell +', 1)="H"',
                                                                'format': hdag_format})
                            # Tidligvakt
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=3)' 
                                                                'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1)) < 16)'
                                                                'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) < 16)'
                                                                'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) > 3)',
                                                                'format': tidlig_format})
                            # Tidlig og kveld
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=3)'
                                                                'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1)) <= 8)'
                                                                'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) >= 16)',
                                                                'format': tidlig_kveld_format})
                            # Kveld                
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=9)'
                                                                'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))<=18)',
                                                                #'AND (VALUE(MID(' + cell + ', SEARCH(":", ' + cell + ', SEARCH(":", ' + cell + ')+1)-2, 2)) >= 16)',
                                                                'format': kveld_format})
                            # Natt
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=(VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))>=18)'
                                                                'AND (VALUE(LEFT(' + cell + ',SEARCH(":",' + cell + ')-1))<=23)',
                                                                'format': natt_format})
                            # Tomme celler
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=(' + cell + '="")',
                                                                'format': skjult_fridag_format})
                            # XX, OO og TT celler
                            worksheet.conditional_format(cell, {'type': 'formula',
                                                                'criteria': '=(' + cell + '="XX ")' 'OR (' + cell + '="OO ")' 'OR (' + cell + '="TT ")',
                                                                'format': turnusfri_format})



if __name__ == '__main__':
    pdfScraper = PdfScraper('turnuser_R24.pdf')