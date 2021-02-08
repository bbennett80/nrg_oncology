import pandas as pd
import requests
from bs4 import BeautifulSoup

#gather trial data from NRG Oncology, place in dataframe
nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
df1 = pd.read_html(nrg_url)
df = df1[0]


#use bs4 to gather trial links
response = requests.get(nrg_url)
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', id='results')

links = []
for tr in table.findAll("tr"):
    trs = tr.findAll("td")
    for each in trs:
        try:
            link = each.find('a')['href']
            href = f'https://www.nrgoncology.org/{link}'
            links.append(href)
        except:
            pass

# 'Enrolled' and 'Planned' data should be gathered from CTSU    
df['Enrolled'] = ''
df['Planned'] = ''
df['Trial link'] = links

open_trial = df.Status == 'Open to Accrual'
open_filtered = df.loc[open_trial]

#JSON document
open_filtered.to_json('NRG_open_trials.json', index=False, orient='split', indent=2)
