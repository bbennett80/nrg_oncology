import pandas as pd

nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
df1 = pd.read_html(nrg_url)
df = df1[0]
df['Enrolled'] = ''
df['Planned'] = ''
open_trial = df.Status == 'Open to Accrual'
open_filtered = df.loc[open_trial]



open_filtered.to_json('NRG_open_trials.json')
