if __name__ == '__main__':
                
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
        
        output_l = []
        
        bills_recent = bills_df[bills_df.congress > 115]
        
        for i, row in bills_recent.iterrows():
                
                try:
                        metadata = get_congress_data(get_root_url(row['url']))
                        # TODO: get infos from metadata dictionary, like sponsors, originChamber, polyArea, title
                        
                        text_url = get_congress_data(
                                get_root_url(row['url']) + '/text')['textVersions'][0]['formats'][0]['url']
                        
                        text = get_bill_text(text_url)
                        
                        summary = get_congress_data(
                                get_root_url(row['url']) + '/summaries')['summaries'][0]['text']
                        
                        subjects = get_congress_data(
                                get_root_url(row['url']) + '/subjects')['subjects']
                        
                        related_bills = get_congress_data(
                                get_root_url(row['url']) + '/relatedbills')
                        
                        dic_i = {'metadata': metadata,
                         'text' : text,
                         'summary': summary,
                         'subjects': subjects,
                         'related_bills': related_bills
                         }
                        
                        output_l.append(dic_i)
                        #TODO: optional, extract information from this. Otherwise 
                        
                        #TODO: extract: amendments, committees, cosponsors(!), titles                        
                
                except Exception as e:
                        print(e)
                                
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