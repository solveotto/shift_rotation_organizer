import pdfplumber
import pandas as pd



def combine_close_texts(text_objects, y_tolerance=1):
    """
    Combine text fragments that are close together vertically.
    """
    combined_texts = []
    current_text = text_objects[0]['text']
    current_bottom = text_objects[0]['bottom']
    
    for obj in text_objects[1:]:
        if abs(obj['top'] - current_bottom) < y_tolerance:
            current_text += obj['text']
            current_bottom = obj['bottom']
        else:
            combined_texts.append(current_text)
            current_text = obj['text']
            current_bottom = obj['bottom']
    
    combined_texts.append(current_text)
    return combined_texts

def get_time_in_string(string_chk):
    
    result_lst = []
    
    for chr in string_chk:
        if chr == ":":
            chr_nr = x.index(chr)
            start = chr_nr - 2
            end = chr_nr + 3
            result_lst.append(string_chk[start:end])
        
    return result_lst

def chk_for_time(string_to_ckeck):
    for chr in string_to_ckeck:
        if chr == ":":
            return True
        else:
            return False

def chk_for_fridag(string_to_check):
    if "OO" or "XX" in string_to_check:
        return True
    else:
        return False
        



pdf = pdfplumber.open("turnus.pdf")
table=pdf.pages[0].extract_table()

new_dict = {"Uke": ["1", "2", "3"], "Mandag": [], "Tirsdag": [], "Onsdag": []}



main_lst = []
for line in table[2:7]:
    count = 0
    lst = []

    
    
    
    for cell in line[:-2]:
        mod_cell = cell.splitlines()
        result = sum([s.split() for s in mod_cell], [])
        lst.append(result)

    main_lst.append(lst)



times_dict = {"Uke":[], "Mandag":[], "Tirsdag":[], "Onsdag":[]}

#print(main_lst)


for uke in main_lst:
    times_dict["Uke"].append(uke[0][0])
    row_counter = 1
    
    for line in uke:

        for item in line:
            if item == "XX" or item == "OO":
                times_dict["Mandag"].append(item)
                pass
            
            day_counter = 0
            for letter in item:

                if letter == ":":
                    
                    times_dict["Mandag"].append(item)
    row_counter += 1
      
print(main_lst)