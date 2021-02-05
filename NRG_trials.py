import pandas as pd

nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
df1 = pd.read_html(nrg_url)
df = df1[0]

#adds empty columns (Enrolled and Planned) to add CTSU data
df['Enrolled'] = ''
df['Planned'] = ''


open_trial = df.Status == 'Open to Accrual'
open_filtered = df.loc[open_trial]
disease_cat = open_filtered.groupby('Disease Category')

#saves as .xlsx file. 
with pd.ExcelWriter(f'NRG Oncology open_trials.xlsx') as writer:
        for ID, group_df in disease_cat:
            ID = ID.replace('[', '').replace(']', '')
            group_df.to_excel(writer, sheet_name=ID, index=False)
