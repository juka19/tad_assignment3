import urllib.request
import json
import os
import pandas as pd
import xml.etree.ElementTree as ET
import random
import time
from multiprocessing.pool import ThreadPool as Pool


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
                                        
                                        return output
                                        
                                if output_format == 'html':
                                        
                                        output = response.read()
                                        
                                        return output
                        
                        except urllib.request.HTTPError:
                                
                                time.sleep(60*60)
                        
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


def get_root_url(url):
        return url.replace('https://api.congress.gov/v3/', '').replace('?format=json', '')



def loop_function(api_key, url):
    try:

            metadata = get_congress_data(get_root_url(url), api_key=api_key)
            # TODO: get infos from metadata dictionary, like sponsors, originChamber, polyArea, title
            
            bill_number = metadata['bill']['number']
            policy_area = metadata['bill']['policyArea']['name']
        #     if 'cosponsors' in metadata['bill'].keys():
        #             cosponsors = get_congress_data(get_root_url(metadata['bill']['cosponsors']['url']) + "?limit=250", api_key=api_key)
        #             cosponsor_D = 0
        #             cosponsor_R = 0
        #             cosponsor_l = []
        #             for cosponsor in cosponsors['cosponsors']:
        #                     cosponsor_party = cosponsor['party']
        #                     if cosponsor_party == "D":
        #                             cosponsor_D += 1 
        #                     if cosponsor_party == "R":
        #                             cosponsor_R += 1
        #                     cosponsor_name = cosponsor['firstName'] + ' ' + cosponsor['lastName']
        #                     cosponsor_party = cosponsor['party']
        #                     cosponsor_l.append({'cosponsor_name': cosponsor_name, 'cosponsor_party': cosponsor_party, 'number': bill_number})
        #             #number = int(output_l[0]['metadata']['bill']['number'])
        #             if (cosponsor_D + cosponsor_R)!= 0:
        #                     cosponsor_D_perc = cosponsor_D/(cosponsor_D + cosponsor_R)
        #                     cosponsor_R_perc = cosponsor_R/(cosponsor_D + cosponsor_R)
        #     else:
        #             cosponsor_D_perc = 0
        #             cosponsor_R_perc = 0
        #             cosponsor_l = []
                    
            latest_action = metadata['bill']['latestAction']['actionDate']
            
        #     subjects = get_congress_data(get_root_url(url) + '/subjects', api_key=api_key)['subjects']
            actions = get_congress_data(get_root_url(url) + '/actions', api_key=api_key)['actions']
            
            # related_bills = get_congress_data(get_root_url(url) + '/relatedbills', api_key=api_key)
            
            # try:
                    
            #         text_l = get_congress_data(get_root_url(url) + '/text', api_key=api_key)['textVersions']
                    
            #         if len(text_l) > 2:
                            
            #                 text_dict = {i['type']: get_bill_text(i['formats'][0]['url']) for i in text_l if (i['formats'] and i['type'])}
            #         else:
            #                 text_dict = {text_l[0]['type']: get_bill_text(text_l[0]['formats'][0]['url'])}
                    
            #         text_dict['bill'] = row['number']
            #         text_dict['title'] = row['title']
            
            # except Exception as er:
            #         print(er)
            #         text_dict = None  
                    
            summaries = get_congress_data(get_root_url(url) + '/summaries', api_key=api_key)
            
            if summaries['summaries']:
                summary = summaries['summaries'][-1]['text']
            else:
                summary = ''
            # summary_dict = {i['actionDesc']: i['text'] for i in summary_l}
        
        
            # summary_dict['bill'] = bill_number
            # summary_dict['title'] = metadata['bill']['title']         
            
            # summary_list.append(summary_dict)
            # text_list.append(text_dict)
            # list_cosponsors.extend(cosponsor_l)
            output_l.append({
                'bill number': bill_number, 
                #'subjects': subjects, 
                'metadata': metadata,
                            # 'related_bills' : related_bills,
                #'summary': summary,
                'policy_area': policy_area, 
                'latest_action': latest_action,
                'actions': actions, 
                #'cosponsor_D_perc': cosponsor_D_perc, 
                #'cosponsor_R_perc': cosponsor_R_perc
                })
            
            #TODO: optional, extract information from this. Otherwise 
            
            #TODO: extract: amendments, committees, cosponsors(!), titles
            
    except Exception as e:
            print(e)
            exceptions.append[i]


bills_df = pd.read_csv('data/old_data/bills3.csv')
bills_df = bills_df[bills_df['latestAction'].str.contains('Became Public Law')]

bills_df2 = pd.read_csv('data/old_data/bills2.csv')
bills_df2 = bills_df2[(bills_df2['latestAction'].str.contains('Became Public Law')) & (bills_df2['congress'] == 116)]

FINAL_DF = pd.concat([bills_df, bills_df2]).reset_index()

output_l = []
list_cosponsors = []
text_list = []
summary_list = []
exceptions = []
# bills_recent = bills_df[bills_df['congress'].isin([116, 117])].reset_index()

counter = 0
start_t = time.time()

api_keys = list(map(os.getenv, ['US.GOV_API4', 'US.GOV_API3', 'US.GOV_API2', 'US.GOV_API']))
api_key = api_keys.pop()

# pool_size = 8

# pool = Pool(pool_size)

for i, row in FINAL_DF.iterrows():
        
        print(f'Querying bill {i} of {len(FINAL_DF)}')
        
        counter += 4
        
        if (counter%4000 <= 4) & (counter > 10):
                
                end_t = time.time()
                elapsed = end_t - start_t
                
                if elapsed < 60*60:
                    time.sleep(60*60 - elapsed)
                    time.sleep(10)
                
                api_keys = list(map(os.getenv, ['US.GOV_API4', 'US.GOV_API3', 'US.GOV_API2', 'US.GOV_API']))
                api_key = api_keys.pop()
                
                start_t = time.time()
                
                counter = 4
                
        if (counter%1000 <= 4) & (counter > 10) & (counter != 4000):
                
                if api_keys:
                        api_key = api_keys.pop()
                else:
                        api_keys = list(map(os.getenv, ['US.GOV_API', 'US.GOV_API2', 'US.GOV_API3', 'US.GOV_API4']))
                        
        # pool.apply_async(loop_function, (api_key, row['url']))
        try:
            loop_function(api_key=api_key, url=row['url'])
        except TypeError as e:
            print(e)
            continue
        except urllib.request.HTTPError as httperr:
                print(httperr)
                end_t = time.time()
                elapsed = end_t - start_t
                if elapsed < 60*60:
                        time.sleep(60*60 - elapsed)
                continue

# pool.close()
# pool.join()

485-490
# error
# <urlopen error [Errno 11001] getaddrinfo failed>
# 'NoneType' object is not subscriptable
# 'builtin_function_or_method' object is not subscriptable
889, 938
# <urlopen error _ssl.c:1106: The handshake operation timed out>
# 'NoneType' object is not subscriptable
# 'builtin_function_or_method' object is not subscriptable
942 & 943
# The read operation timed out
# 'NoneType' object is not subscriptable
# 'builtin_function_or_method' object is not subscriptable

df_ouput_cosponsors = pd.DataFrame.from_records(list_cosponsors)

output_df = pd.DataFrame.from_records(output_l)

with open('no.txt', 'w') as txtfile:
    json.dump(output_l, txtfile)

text_df = pd.DataFrame.from_records(text_list)
summary_df = pd.DataFrame.from_records(summary_list)

summary_df.to_csv('data/summary_data.csv')
df_ouput_cosponsors.to_csv('data/cosponsors_final.csv')
output_df.to_csv('data/additional_info_final.csv')


text_df.to_csv('data/text_data.csv')      


FINAL_DF = bills_df[bills_df['latestAction'].str.contains('Became Public Law')]
