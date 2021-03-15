import pandas as pd
import requests
import json
import glob
import os

def gather_nrg_trials():
    nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
    df1 = pd.read_html(nrg_url)
    df = df1[0]
    open_trial = df.Status == 'Open to Accrual'
    open_filtered = df.loc[open_trial]
    return open_filtered.Study

def trial_search():
    nrg_trials = gather_nrg_trials()
    
    for nrg_num in nrg_trials:
        nrg_num = nrg_num.replace(' ', '+')
        api_url = f'https://clinicaltrials.gov/api/query/full_studies?expr={nrg_num}&min_rnk=1&max_rnk=&fmt=json'
        r = requests.get(api_url).text
        raw_json = json.loads(r)
        if raw_json['FullStudiesResponse']['NStudiesFound'] == 0:
            print('No study available', nrg_num)
            with open('Full_Studies/not_available.txt', 'a+') as log:
                log.write(f'{nrg_num}\n')
        else:
            print('Downloading:', nrg_num)

            r = requests.get(api_url)
            r = requests.get(api_url).text
            raw_json = json.loads(r)
            with open(f'Full_Studies/{nrg_num}.json', 'w+') as f:
                json.dump(raw_json, f, indent=2)

    with open('Full_Studies/not_available.txt', 'r') as log:
        print('The following clinical trials were not available for download. Please check online.')
        na = log.readlines()
        for i in na:
            print(i)

def extract_brief():
    all_studies = glob.glob('Full_Studies/*.json', recursive=True)

    for study in all_studies:
        with open(study, 'r') as study_doc:
            data = json.load(study_doc)

            nctid = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']
            title = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['OfficialTitle']
            brief = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['BriefSummary']
            criteria = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['EligibilityModule']['EligibilityCriteria']

            study_data = {'NCTId': nctid, 'Title': title, 'Brief Summary': brief, 'EligibilityCriteria': criteria} 
            df = pd.DataFrame(data = study_data, index=[0])
            df.to_excel(f'Full_Studies/NRGOncology{nctid}.xlsx')

def combine_brief():
    study_briefs = glob.glob('Full_Studies/*.xlsx', recursive=True)
    df = pd.concat((pd.read_excel(f) for f in study_briefs),ignore_index=True)
    df = df.drop(columns=['Unnamed: 0'])
    df.to_excel('NRG Open Study Briefs.xlsx',  index=False)
    
def clean_up():
    all_studies = glob.glob('Full_Studies/*.json', recursive=True) + glob.glob('Full_Studies/NRGOncologyNCT*.xlsx', recursive=True)
    
    if not all_studies:
        print('Files cleaned up. Trials downloaded.')
    else:
        try:
            print('Files cleaned up. Trials downloaded.')
            for files in all_studies:
                os.remove(files)
        except OSError as e:
            print(f'Error: {file_path} : {e.strerror}')
    

    
if __name__=='__main__':
    trial_search()
    extract_brief()
    combine_brief()
    clean_up()
