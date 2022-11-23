if __name__ == '__main__':
                
        import urllib.request
        import json
        import os
        import pandas as pd
        import xml.etree.ElementTree as ET
        import random
        import time

        def congress_deco(output_format='json') -> object:
                
                def get_congress(func):
                        
                        print(f'Decorating: {func.__name__}')
                        
                        def wrapper(*args, **kwargs):
                                
                                try:
                                        
                                        url, hdr = func(*args, **kwargs)
                                        
                                        req = urllib.request.Request(url, headers=hdr)
                                        req.get_method = lambda: 'GET'
                                        response = urllib.request.urlopen(req, timeout=5)
                                        
                                        if output_format == 'json':
                                                
                                                output = response.read()
                                                
                                                output = json.loads(output)
                                                
                                        if output_format == 'html':
                                                
                                                output = response.read()
                                        
                                        return output
                                
                                except Exception as e:
                                        
                                        print(e)
                                
                        return wrapper
                
                return get_congress
        
        
        @congress_deco(output_format='json')
        def get_congress_data(query:str, *args, api_key=os.getenv('US.GOV_API')) -> dict:
                
                hdr = {
                        # specifying requested encoding
                        'Cache-Control': 'no-cache',
                        'charset': 'UTF-8',
                        'X-Api-Key': api_key,
                        'User-Agent': random.choice(['Mozilla/5.0', 'Chrome 104.0.0.0', 
                                                     'Chrome 52.0.2762.73', 'Chrome 55.0.2919.83'])
                        }
                
                BASE_URL = 'https://api.congress.gov/v3/'
                
                query_url = BASE_URL + query
                
                if args: # concatenate variable arguments to url
                        query_url += '&' + '&'.join(args)
                                
                return (query_url, hdr)
        
        @congress_deco(output_format='html')
        def get_bill_text(query:str) -> str:
                
                hdr = {
                        # specifying requested encoding
                        'Cache-Control': 'no-cache',
                        'charset': 'UTF-8',
                        'User-Agent': random.choice(['Mozilla/5.0', 'Chrome 104.0.0.0', 
                                                     'Chrome 52.0.2762.73', 'Chrome 55.0.2919.83'])
                        }
                
                return (query, hdr)
        
        # def get_congress_data(query, *args, api_key=os.getenv('US.GOV_API')):
                
        #         try:
                        
        #                 BASE_URL = 'https://api.congress.gov/v3/'
                        
        #                 hdr = {
        #                 #specifying requested encoding
        #                 'Cache-Control': 'no-cache',
        #                 'charset': 'UTF-8',
        #                 'X-Api-Key': api_key
        #                 }
                        
        #                 query_url = BASE_URL + query
                        
        #                 if args: # concatenate variable arguments to url
        #                         query_url += '&' + '&'.join(args)
                        
        #                 req = urllib.request.Request(query_url, headers=hdr)
        #                 req.get_method = lambda: 'GET'
        #                 response = urllib.request.urlopen(req)

        #                 string_resp = response.read()
                        
        #                 return json.loads(string_resp)
                        
        #         except Exception as e:
                        
        #                 print(e)

        bills = []
        
        for c in range(116, 117):
                
                next_link = f"bill/{c}?format=json&limit=250"
                
                while next_link:
                        
                        try:
                                
                                print(f"Now retrieving: {next_link}")
                                output = get_congress_data(next_link)
                                bills.append(output['bills'])
                                next_link = output['pagination']['next'].replace('https://api.congress.gov/v3/', '')
                                
                        except Exception:
                                                                
                                print(f'Finished congress {c}')
                                next_link = False
        
        bills_df = pd.concat([pd.DataFrame.from_records(recs) for recs in bills], axis=0)
        bills_df.to_csv('data/bills.csv')
        
        def get_root_url(url):
                return url.replace('https://api.congress.gov/v3/', '').replace('?format=json', '')
        
        
        bills_df = pd.read_csv('data/bills2.csv')
        
        output_l = []
        list_cosponsors = []
        text_list = []
        summary_list = []
        
        bills_recent = bills_df[bills_df['congress'].isin([116, 117])].reset_index()
        
        counter = 0
        start_t = time.time()
        
        api_keys = list(map(os.getenv, ['US.GOV_API', 'US.GOV_API2', 'US.GOV_API3', 'US.GOV_API4']))
        api_key = api_keys.pop()
        
        bills_recent = bills_recent.iloc[116:130,:]
              
        for i, row in bills_recent.iterrows():
                
                print(f'Querying bill {i} of {len(bills_recent)}')
                
                counter += 6
                
                if (counter%4000 <= 6) & (counter > 10):
                        
                        end_t = time.time()
                        elapsed = end_t - start_t
                        time.sleep(60*60 - elapsed + 10)
                        
                        start_t = time.time()
                        
                        counter = 6
                        
                elif (counter%1000 <= 6) & (counter > 10):
                        
                        if api_keys:
                                api_key = api_keys.pop()
                        else:
                                api_keys = list(map(os.getenv, ['US.GOV_API', 'US.GOV_API2', 'US.GOV_API3', 'US.GOV_API4']))
                
                try:
                        metadata = get_congress_data(get_root_url(row['url']), api_key=api_key)
                        # TODO: get infos from metadata dictionary, like sponsors, originChamber, polyArea, title
                        
                        bill_number = metadata['bill']['number']
                        policy_area = metadata['bill']['policyArea']['name']
                        if 'cosponsors' in metadata['bill'].keys():
                                cosponsors = get_congress_data(get_root_url(metadata['bill']['cosponsors']['url']) + "?limit=250", api_key=api_key)
                                cosponsor_D = 0
                                cosponsor_R = 0
                                cosponsor_l = []
                                for cosponsor in cosponsors['cosponsors']:
                                        cosponsor_party = cosponsor['party']
                                        cosponsor_D += 1 if cosponsor_party == 'D' else 0
                                        cosponsor_R += 1 if cosponsor_party == 'R' else 0
                                        cosponsor_name = cosponsor['firstName'] + ' ' + cosponsor['lastName']
                                        cosponsor_party = cosponsor['party']
                                        cosponsor_l.append({'cosponsor_name': cosponsor_name, 'cosponsor_party': cosponsor_party, 'number': bill_number})
                                #number = int(output_l[0]['metadata']['bill']['number'])
                                cosponsor_D = cosponsor_D/(cosponsor_D + cosponsor_R)
                                cosponsor_R = cosponsor_R/(cosponsor_D + cosponsor_R)
                        else:
                                cosponsor_D = 0
                                cosponsor_R = 0
                                cosponsor_l = []
                                
                        latest_action = metadata['bill']['latestAction']['actionDate']
                        
                        try:
                                
                                text_l = get_congress_data(get_root_url(row['url']) + '/text', api_key=api_key)['textVersions']
                                
                                if len(text_l) > 2:
                                        
                                        text_dict = {i['type']: get_bill_text(i['formats'][0]['url']) for i in text_l if (i['formats'] and i['type'])}
                                else:
                                        text_dict = {text_l[0]['type']: get_bill_text(text_l[0]['formats'][0]['url'])}
                                
                                text_dict['bill'] = row['number']
                                text_dict['title'] = row['title']
                        
                        except Exception as er:
                                
                                print(er)
                                text_dict = None
                        
                        summary_l = get_congress_data(get_root_url(row['url']) + '/summaries', api_key=api_key)['summaries']
                        
                        summary_dict = {i['actionDesc']: i['text'] for i in summary_l}
                        
                        summary_dict['bill'] = row['number']
                        summary_dict['title'] = row['title']
                        
                        subjects = get_congress_data(get_root_url(row['url']) + '/subjects', api_key=api_key)['subjects']
                        
                        related_bills = get_congress_data(get_root_url(row['url']) + '/relatedbills', api_key=api_key)
                        
                        # dic_i = {'metadata': metadata,
                        # 'text' : text,
                        # 'summary': summary,
                        # 'subjects': subjects,
                        # 'related_bills': related_bills
                        # }
                        summary_list.append(summary_dict)
                        text_list.append(text_dict)
                        list_cosponsors.extend(cosponsor_l)
                        output_l.append({'bill number': bill_number,
                                        'policy_area': policy_area, 'latest_action': latest_action,
                                        'cosponsor_D_perc': cosponsor_D, 'cosponsor_R_perc': cosponsor_R})
                        #TODO: optional, extract information from this. Otherwise 
                        
                        #TODO: extract: amendments, committees, cosponsors(!), titles                        
                        
                except Exception as e:
                        print(e)
                        
        df_ouput_cosponsors = pd.concat(list_cosponsors)
        
        output_df = pd.DataFrame.from_records(output_l)
        text_df = pd.DataFrame.from_records(text_list)
                        
else:
        import urllib.request
        import json
        import os
        import pandas as pd


        # def get_congress_data(query, *args, api_key=os.getenv('US.GOV_API')):
                
        #         try:
                        
        #                 BASE_URL = 'https://api.congress.gov/v3/'
                        
        #                 hdr = {
        #                 # specifying requested encoding
        #                 'Cache-Control': 'no-cache',
        #                 'charset': 'UTF-8',
        #                 'X-Api-Key': api_key
        #                 }
                        
        #                 query_url = BASE_URL + query
                        
        #                 if args: # concatenate variable arguments to url
        #                         query_url += '&' + '&'.join(args)
                        
        #                 req = urllib.request.Request(query_url, headers=hdr)
        #                 req.get_method = lambda: 'GET'
        #                 response = urllib.request.urlopen(req)

        #                 string_resp = response.read()
                        
        #                 return json.loads(string_resp)
                
        #         except Exception as e:
                        
        #                 print(e)
        import urllib.request
        import json
        import os
        import pandas as pd
        import xml.etree.ElementTree as ET

        def congress_deco(output_format='json') -> object:
                
                def get_congress(func):
                        
                        print(f'Decorating: {func.__name__}')
                        
                        def wrapper(*args, **kwargs):
                                
                                try:
                                        
                                        url, hdr = func(*args, **kwargs)
                                        
                                        req = urllib.request.Request(url, headers=hdr)
                                        req.get_method = lambda: 'GET'
                                        response = urllib.request.urlopen(req, timeout=5)
                                        
                                        output = response.read()
                                        
                                        if output_format == 'json':
                                                
                                                output = json.loads(output)
                                                
                                        if output_format == 'html':
                                                
                                                root = ET.ElementTree(ET.fromstring(output)).getroot()
                                                
                                                output = [node.text for node in root.findall('.//pre')]
                                        
                                        return output
                                
                                except Exception as e:
                                        
                                        print(e)
                                
                        return wrapper
                
                return get_congress
        
        
        @congress_deco(output_format='json')
        def get_congress_data(query:str, *args, api_key=os.getenv('US.GOV_API')) -> dict:
                
                hdr = {
                        # specifying requested encoding
                        'Cache-Control': 'no-cache',
                        'charset': 'UTF-8',
                        'X-Api-Key': api_key,
                        'User-Agent': 'Mozilla/5.0'
                        }
                
                BASE_URL = 'https://api.congress.gov/v3/'
                
                query_url = BASE_URL + query
                
                if args: # concatenate variable arguments to url
                                query_url += '&' + '&'.join(args)
                                
                return (query_url, hdr)
        
        @congress_deco(output_format='html')
        def get_bill_text(query:str, api_key=os.getenv('US.GOV_API')) -> str:
                
                hdr = {
                        # specifying requested encoding
                        'Cache-Control': 'no-cache',
                        'charset': 'UTF-8',
                        'User-Agent': 'Mozilla/5.0'
                        }
                
                return (query, hdr)