import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml
import json


def nrg_trials():
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
    #df['Description'] = description

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


def study_brief():
    df = pd.concat(pd.read_excel('./NRG Oncology open trials.xlsx', 
        sheet_name=None), 
        ignore_index=True)
    
    briefs = []

    for title in df.Title:
        title = title.replace(' ', '+').replace(',', '%2C').replace('+/-', '%2B%2F').replace('/', '%2F').replace(':', '%3A').replace('(', '%28').replace(')', '%29'). replace('=', '%3D')
        api_url = f'https://clinicaltrials.gov/api/query/full_studies?expr={title}&min_rnk=1&max_rnk=&fmt=json'
        r = requests.get(api_url)
        
        if r.status_code != 200:
            briefs.append('Bad URL')
        elif r.status_code == 200:
            try:
                r = requests.get(api_url).text
                raw_json = json.loads(r)
                brief = raw_json['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['BriefSummary']
                briefs.append(brief)
            except KeyError:
                briefs.append('No description in URL')
    
    df['Description'] = briefs
    
    disease_cat = df.groupby('Disease Category')

    with pd.ExcelWriter(f'NRG Oncology open trials.xlsx') as writer:
            for ID, group_df in disease_cat:
                ID = ID.replace('[', '').replace(']', '')
                group_df.to_excel(writer, sheet_name=ID, index=False)

def add_brief():
    pass

if __name__=='__main__':
    nrg_trials()
    study_brief()
    add_brief()
