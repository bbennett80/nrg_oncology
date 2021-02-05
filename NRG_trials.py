import pandas as pd
import requests
from bs4 import BeautifulSoup
#get current open trials from NRG Oncology and save file
nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
df1 = pd.read_html(nrg_url)
df = df1[0]

#use BeautifulSoup to grab the trial link
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

        
#adds empty columns (Enrolled and Planned) to add CTSU data
df['Enrolled'] = ''
df['Planned'] = ''
df['Trial link'] = links
open_trial = df.Status == 'Open to Accrual'
open_filtered = df.loc[open_trial]

disease_cat = open_filtered.groupby('Disease Category')

with pd.ExcelWriter(f'NRG Oncology open trials.xlsx') as writer:
        for ID, group_df in disease_cat:
            ID = ID.replace('[', '').replace(']', '')
            group_df.to_excel(writer, sheet_name=ID, index=False)
