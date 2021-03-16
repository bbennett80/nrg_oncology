import pandas as pd
import requests
import json
import glob
import os

def main():
    """Download all "open to accrual" clinical trials from NRG Oncology.
    Feed trials to clinicaltrials.gov API to retrieve full study data.
    Combine into a .xlsx file with tabbed disease sites.
    """
    folder_setup()
    nrg_trials = gather_nrg_trials()
    trial_search(nrg_trials)
    extract_brief()
    combine()
    clean_up()

def folder_setup():
    current_directory = os.getcwd()

    studies_directory = os.path.join(current_directory, r'Full_Studies')
    
    not_available_file = 'Full_Studies/not_available.txt'

    if not os.path.exists(studies_directory):
       os.makedirs(studies_directory)
    
    if not os.path.exists(not_available_file):
        pass
    else:
        os.remove(not_available_file)

def gather_nrg_trials():
    nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
    df1 = pd.read_html(nrg_url)
    df = df1[0]
    open_trial = df.Status == 'Open to Accrual'
    open_filtered = df.loc[open_trial]
    open_filtered = open_filtered.drop(columns=['Title', 'Status'])
    return open_filtered


def trial_search(nrg_trials):    
    for nrg_num in nrg_trials.Study:
        nrg_num = nrg_num.replace(' ', '+')
        api_url = f'https://clinicaltrials.gov/api/query/full_studies?expr={nrg_num}&min_rnk=1&max_rnk=&fmt=json'
        r = requests.get(api_url).text
        raw_json = json.loads(r)
        if raw_json['FullStudiesResponse']['NStudiesFound'] == 0:
            print('No study available by this NRG number.', nrg_num)
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
            nrg_id = data['FullStudiesResponse']['Expression']
            nctid = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']
            title = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['OfficialTitle']
            brief = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['BriefSummary']
            criteria = data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['EligibilityModule']['EligibilityCriteria']

            study_data = {'Study': nrg_id,
                          'NCTId': nctid,
                          'Title': title,
                          'Brief Summary': brief,
                          'EligibilityCriteria': criteria} 
            
            df = pd.DataFrame(data = study_data, index=[0])
            df.to_excel(f'Full_Studies/NRGOncology{nctid}.xlsx')


def combine():
    study_briefs = glob.glob('Full_Studies/*.xlsx', recursive=True)
    df = pd.concat((pd.read_excel(f) for f in study_briefs),ignore_index=True)
    df = df.drop(columns=['Unnamed: 0'])
    df.to_excel('NRG Open Study Briefs.xlsx')

    df_briefs = pd.read_excel('NRG Open Study Briefs.xlsx')
    df_nrg = gather_nrg_trials()
    df = pd.merge(df_briefs, df_nrg, how='outer', on='Study')
    df = df.drop(columns=['Unnamed: 0'])
    df['Link'] = 'https://clinicaltrials.gov/ct2/show/' + df['NCTId']
    
    df = df.groupby('Disease Category')

    with pd.ExcelWriter('NRG Open Study Merge.xlsx') as writer:
        for ID, group_df in df:
            ID = ID.replace('[', '').replace(']', '')
            group_df.to_excel(writer, sheet_name=ID, index=False)


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
    main()
