import pandas as pd
import xlsxwriter

# Create some example dataframes
dfs = {'df1' : pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
        'df2' : pd.DataFrame({'C': [7, 8, 9], 'D': [10, 11, 12]})
}
with pd.ExcelWriter('multiple_sheets.xlsx', engine='xlsxwriter') as writer:
    for sheet_name, df in dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

