def manual_trial_search(trial_number: str):    
    api_url = f'https://clinicaltrials.gov/api/query/full_studies?expr={trial_number}&min_rnk=1&max_rnk=&fmt=json'
    r = requests.get(api_url).text
    raw_json = json.loads(r)
    if raw_json['FullStudiesResponse']['NStudiesFound'] == 0:
        print('No study available by this NRG number.', trial_number)
        with open('manual_not_available.txt', 'a+') as log:
            log.write(f'{trial_number}\n')
    else:
        print('Downloading:', trial_number)

        r = requests.get(api_url)
        r = requests.get(api_url).text
        raw_json = json.loads(r)
        with open(f'{trial_number}.json', 'w+') as f:
            json.dump(raw_json, f, indent=2)

# S1207 = NCT01674140
# NRG-GI004/SWOG-S1610 = NCT02997228
# SWOG-S1418+NRG-BR006 = closed
# manual_trial_search('NCT02997228')
