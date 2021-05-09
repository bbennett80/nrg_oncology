from datetime import datetime
import pandas as pd
import requests

from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.styles import Font


def main():
    """Download all "open to accrual" clinical trials from NRG Oncology.
    Feed trials to clinicaltrials.gov API to retrieve full study data.
    Combine into a .xlsx file with tabbed disease sites.
    
    Note:
    The final output of this programs is a .xlsx file. As such, the
    following limits should be noted.
    
    - Row height: 409 points
    - Total number of characters that a cell can contain: 32,767 characters
    
    https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3
    
    ***ALL CRITERIA MIGHT NOT BE CONTAINED IN CORRESPONDING CELL***
    
    """
    global today 
    today = datetime.now().strftime('%m_%d_%Y')
    nrg_trials = scrape_nrg_trials()
    trial_urls, disease_categories = trial_search(nrg_trials)
    table = download_open_trials(trial_urls, disease_categories)
    write_table(table)
    prettify()
    
    
def scrape_nrg_trials():
    """Searches NRG Oncology for clinical trial listed as 'open to accrual',
    returns a dataframe.
    """
    nrg_url = 'https://www.nrgoncology.org/Clinical-Trials/Protocol-Search'
    df1 = pd.read_html(nrg_url)
    df = df1[0]
    df.Study = df.Study.str.replace('NRG-GI004/SWOG-S1610', 'S1610')
    df.Study = df.Study.str.replace('SWOG-S1207 NSABP B-53', 'S1207')

    open_trial = (df.Status == 'Open to Accrual')
    open_filtered = df.loc[open_trial]
    open_filtered = open_filtered.drop(columns=['Title', 'Status'])
    return open_filtered

def trial_search(nrg_trials): 
    """Builds urls and disease categories for open clinical trials"""
    
    trial_urls = []
    disease_categories = []
    
    for nrg_num, disease_category in zip(nrg_trials['Study'], nrg_trials['Disease Category']) :
        nrg_num = nrg_num.replace(' ', '+').replace('/', ' ')
        api_url = f'https://clinicaltrials.gov/api/query/full_studies?expr={nrg_num}&min_rnk=1&max_rnk=&fmt=json'
        
        disease_category = disease_category.replace('[', '').replace(']', '')
        
        trial_urls.append(api_url)
        disease_categories.append(disease_category)
              
    return trial_urls, disease_categories


def download_open_trials(trial_urls, disease_categories):
    """Downloads clinical trials and places information into csv style table."""
    
    print('Downloading...')
    
    table = []
    for url, disease_category in zip(trial_urls, disease_categories):
        r = requests.get(url)
        
        if r.status_code != 200:
            print(f'URL is not available:\n{url}\n')
            with open('not_available.txt', 'a+') as log:
                log.write(f'URL is not available:\n{url}\n')
        
        else:
            trial_data = r.json()            
            
            if trial_data['FullStudiesResponse']['NStudiesFound'] == 0:
                print(f'No study available by this NRG url\n {url}')
                with open('not_available.txt', 'a+') as log:
                    log.write(f'{url}\n')

            else:
                row = []
                
                nrg_id = trial_data['FullStudiesResponse']['Expression']
                nctid = trial_data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['NCTId']
                disease_category = disease_category
                phase = trial_data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DesignModule']['PhaseList']['Phase']
                planned = ''
                actual = ''
                title = trial_data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['IdentificationModule']['OfficialTitle']
                brief = trial_data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['DescriptionModule']['BriefSummary']
                criteria = trial_data['FullStudiesResponse']['FullStudies'][0]['Study']['ProtocolSection']['EligibilityModule']['EligibilityCriteria']
                link = f'https://clinicaltrials.gov/ct2/show/{nctid}'
                
                
                print(f'\t{nrg_id}')                
                
                row.append(nrg_id)
                row.append(nctid)
                row.append(disease_category)
                row.append(phase)
                row.append(planned)
                row.append(actual)
                row.append(title)
                row.append(brief)
                row.append(criteria)
                row.append(link)
                
                table.append(row)
                
    
    print('\n-----Downloads complete-----\n')
    return table


def write_table(table):
    """Takes in table and combines info into a .xlsx file with tabbed disease sites.
    Stamped with today's date.
    """
        
    df = pd.DataFrame(data=table, 
                      columns=['NRG ID','NCT ID', 'Disease Category', 'Phase',
                               'Planned', 'Actual', 'Title', 'Brief', 
                               'Eligibility Criteria', 'Link']
                     )
    
    df = df.groupby('Disease Category')

    
    with pd.ExcelWriter(f'NRG Open Study {today}.xlsx') as writer:
        for ID, group_df in df:
            group_df.to_excel(writer, sheet_name=ID, index=False)


def prettify():
    """.xlsx formatting fixes."""
    
    print("""Note:
    The final output of this programs is a .xlsx file. As such, the
    following limits should be noted.
    
    - Row height: 409 points
    - Total number of characters that a cell can contain: 32,767 characters
    
    https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3
    
    ***ALL CRITERIA MIGHT NOT BE CONTAINED IN CORRESPONDING CELL***
    """)
    
    wb = load_workbook(f'NRG Open Study {today}.xlsx')
    
    for ws in wb.worksheets:
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 14
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 24
        ws.column_dimensions['E'].width = 14
        ws.column_dimensions['F'].width = 14
        ws.column_dimensions['G'].width = 55
        ws.column_dimensions['H'].width = 100
        ws.column_dimensions['I'].width = 100
        ws.column_dimensions['J'].width = 42
        for cell in ws:
            for row in cell:
                row.alignment = Alignment(horizontal='justify', vertical='center', wrap_text=True)
                row.font = Font(name='Calibri',size=12)

    wb.save(f'NRG Open Study {today}.xlsx')  
    

if __name__=='__main__':
    main()
