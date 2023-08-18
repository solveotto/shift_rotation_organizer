import pdfplumber
import pandas as pd


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



# count = 0
# for x in table[2][1:-2]:
    
#     x = x.splitlines()
#     print(x)

#     if count == 0:
#         if chk_for_fridag(x):
#             new_dict["Mandag"].append(x)
#     elif count == 1:
#         if chk_for_fridag(x):
#             new_dict["Tirsdag"].append(x)
#     elif count == 2:

#         if chk_for_fridag(x):
#             new_dict["Onsdag"].append(x)
        
#         elif chk_for_time(x):
#             string = get_time_in_string(x)  
#             print(string)
            
#             if len(string) > 0:
#                 if len(new_dict["Tirsdag"]) < 2 and "OO" not in new_dict["Tirsdag"]:
#                     for x in string:
#                         new_dict["Tirsdag"].append(x)
#                 else: 
#                     for x in string:
#                         x.replace("\n", "")
#                         new_dict["Onsdag"].append(x)

    
#     count +=1 

content_dict = {"Uke":[], "Mandag":[], "Tirsdag":[], "Onsdag":[]}
main_lst = []
for line in table[2:7]:
    count = 0
    lst = []

    
    
    
    for cell in line[:-2]:
        mod_cell = cell.splitlines()
        result = sum([s.split() for s in mod_cell], [])
        lst.append(result)

    main_lst.append(lst)

time_lst  = {"Mandag":[],}

for l in main_lst:
    for entry in l:
        for post in entry:
            for letter in post:
                if letter == ":":
                    val  = l[0][0]
                    time_lst.append({val : post})

print(time_lst)