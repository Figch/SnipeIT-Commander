#!/usr/bin/env python3

import sys
import requests
import urllib3
import configparser
import argparse
import time
from datetime import datetime


import win32com.client as win32  #pip install pywin32


# stupid youre not secure error supression nothing to see here
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Argparser
parser = argparse.ArgumentParser(description='Check Snipe for overdue audit assets')
parser.add_argument('-e', '--email', action='store_true', help='Open Email templates for user audit requests')
args = parser.parse_args()


def get_user_id(api_base_url, api_token):
    api_url = f"{api_base_url}/users/me"
    try:
        response = requests.get(api_url, headers={"Authorization": f"Bearer {api_token}"}, verify=False)
        if response.status_code == 200:
            return response.json().get("id")
        else:
            print(f"Error: Unable to retrieve user ID. Status Code: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"Error: Unable to connect to {api_base_url}. Please check the URL and your network connection.")
        sys.exit(1)
    except Exception as e:
        print(f"Error in request: {e}")
        sys.exit(1)

def read_config():
    config = configparser.ConfigParser()
    config.read('.config')
    api_base_url = config.get('api', 'url', fallback='https://default.api.url')
    api_token = config.get('api', 'access_token', fallback='')
    # remove the endpoint part from the base url
    api_base_url = api_base_url.rsplit('/', 1)[0]
    user_id = get_user_id(api_base_url, api_token)


    return user_id, api_base_url, api_token


def auditOverdue(api_base_url, api_token):
    allOverdueText=[] #array of strings
    overdueAssets=[]
    askConfirmationAssets={}



    api_url = f"{api_base_url}/hardware/audit/overdue"

    config = configparser.ConfigParser()
    config.read('.config',encoding="utf8")
    company_name = config.get('overdue', 'company_name', fallback='')
    ignore_checkout_names = config.get('overdue', 'ignore_checkout_names', fallback='').split(',')
    ignore_checkout_names = [x for x in ignore_checkout_names if len(x)>0]
    ignore_tags = config.get('overdue', 'ignore_tags', fallback='').split(',')
    ignore_tags = [x for x in ignore_tags if len(x)>0]
    ignore_model_names = config.get('overdue', 'ignore_model_names', fallback='').split(',')
    ignore_model_names = [x for x in ignore_model_names if len(x)>0]
    ignore_model_names_contains = config.get('overdue', 'ignore_model_names_contains', fallback='').split(',')
    ignore_model_names_contains = [x for x in ignore_model_names_contains if len(x)>0]
    request_size = int(config.get('overdue', 'request_size', fallback=500)) #how many assets to request at once
    show_assets = int(config.get('overdue', 'show_assets', fallback=1000)) #how many overdue assets to list
    email_checkout_names = config.get('overdue', 'email_checkout_names', fallback='').split(',')
    email_checkout_names = [x for x in email_checkout_names if len(x)>0]
    email_subject = config.get('overdue', 'email_subject', fallback='Inventur')
    email_domain = config.get('overdue', 'email_domain', fallback='example.com')

    
    

    last_data_length=request_size
    page=0
    while len(overdueAssets)<show_assets and last_data_length==request_size:
        params = {"limit": request_size, "offset": request_size*page}
        page+=1
        try:
            response = requests.get(api_url, headers={"Authorization": f"Bearer {api_token}"}, params=params, verify=False, timeout=2)
        except requests.exceptions.ConnectionError:
            print(f"Error: Unable to connect to {api_base_url}. Please check the URL and your network connection.")
            sys.exit(1)
        except Exception as e:
            print(f"Error in request: {e}")
            sys.exit(1)
        if response.status_code == 200:
            data = response.json()
            last_data_length=len(data['rows'])
            print("datalen="+str(last_data_length))
            
            for asset in data['rows']:
                if asset.get('company').get('name')==company_name:
                    if asset.get('byod'):
                        continue
                    if asset.get('assigned_to','') is not None: #checked out to someone
                        if asset.get('assigned_to').get('name','') in ignore_checkout_names: #checked out to something to be ignored
                            continue
                    if asset.get('asset_tag', 'Unknown Tag') in ignore_tags:
                        continue
                    if asset.get('model') is not None:
                        if asset.get('model').get('name') in ignore_model_names: #is a model to be ignored
                            continue
                        if any(m in asset.get('model').get('name') for m in ignore_model_names_contains): #is a model to be ignored *
                            continue
                    if asset.get('status_label').get('status_meta') == 'archived':
                        continue
                    overdueAssets.append(asset)
                    '''
                    asset_id = asset.get('id', 'Unknown ID')
                    asset_tag = asset.get('asset_tag', 'Unknown Tag')
                    print(f"Tag: {asset_tag}")
                    assigned_to = asset.get('assigned_to')
                    print(f"assigned to: {assigned_to}")
                    checkout_username = assigned_to.get('username', '') if assigned_to else ''
                    checkout_person = assigned_to.get('name', '').split()[0] if assigned_to else ''
                    last_audit = asset.get('last_audit_date')
                    #print(f"{asset}")
                    print("")
                    '''
                    asset_tag = asset.get('asset_tag', 'Unknown Tag')
                    asset_name = asset.get('name', '')
                    assigned_to = ''
                    if asset.get('assigned_to','') is not None: #checked out to someone
                        assigned_to = asset.get('assigned_to').get('name')
                    
                    model_name = asset.get('model').get('name')
                    model_number = asset.get('model_number')
                    if model_number is None:
                        model_number = ''
                    manufacturer_name = asset.get('manufacturer').get('name','')


                    last_checkout = asset.get('last_checkout')
                    if last_checkout is not None:
                        last_checkout=last_checkout.get('datetime')
                    last_checkin = asset.get('last_checkin')
                    if last_checkin is not None:
                        last_checkin=last_checkin.get('datetime')
                    last_audit = asset.get('last_audit_date')
                    if last_audit is not None:
                        last_audit=last_audit.get('datetime')

                    last_checkout_obj = datetime.strptime("1970-01-01 12:00:00", '%Y-%m-%d %H:%M:%S')
                    if last_checkout is not None:
                        last_checkout_obj = datetime.strptime(last_checkout, '%Y-%m-%d %H:%M:%S')
                        
                    last_checkin_obj = datetime.strptime("1970-01-01 12:00:00", '%Y-%m-%d %H:%M:%S')
                    if last_checkin is not None:
                        last_checkin_obj = datetime.strptime(last_checkin, '%Y-%m-%d %H:%M:%S')

                    last_audit_obj = datetime.strptime("1970-01-01 12:00:00", '%Y-%m-%d %H:%M:%S')
                    if last_audit is not None:
                        last_audit_obj = datetime.strptime(last_audit, '%Y-%m-%d %H:%M:%S')

                    lastchange=max(last_audit_obj,last_checkin_obj,last_checkout_obj)
                    notTouchedDays=(datetime.now()-lastchange).days

                    asset_status=asset.get('status_label').get('status_meta') 


                    text="Tag: "+asset_tag+" \""+asset_name+"\" "+manufacturer_name+" "+model_number
                    if assigned_to!='':
                        text+=" checked out to: "+assigned_to
                        #print(f"Tag: {asset_tag} \"{asset_name}\" {manufacturer_name} {model_number} assigned to: {assigned_to}")
                    text+=". Not touched since "+str(notTouchedDays)+" days"

                    if asset_status=='archived' or asset_status=='pending':
                        text+=". Status="+str(asset_status)

                    print(text)
                    allOverdueText.append(text)

                    if assigned_to != '' and assigned_to in email_checkout_names: #checked out to something/someone to be emailed
                        if assigned_to not in askConfirmationAssets:
                            askConfirmationAssets[assigned_to]=[] #create list if this is first element
                        askConfirmationAssets[assigned_to].append("\""+manufacturer_name+" "+asset_name+"\" ("+asset_tag+")")
                    
                    
        else:
            print(f"Error: Unable to retrieve assets. Status Code: {response.status_code}")

    return allOverdueText,askConfirmationAssets,email_subject,email_domain

def main():
    user_id, api_base_url, api_token = read_config()
    allOverdue,askConfirmationAssets,email_subject,email_domain=auditOverdue(api_base_url, api_token)
    with open("overdue.txt", "w") as f:
        for l in allOverdue:
            f.write(l+"\n")
    print(str(len(allOverdue))+" Assets overdue for audit")

    if args.email:
        for name in askConfirmationAssets:
            textassets=askConfirmationAssets[name]
            
            text="Hallo "+str(name.split(' ')[0])+",<br><br>Für die Inventur bräuchte ich einmal von dir die Bestätigung, dass folgende Geräte noch bei dir sind.<br>"
            text+="Wenn etwas nicht da ist, bitte Bescheid geben.<br><br>"
            text+="<ul>"
            for l in textassets:
                text+="<li>"+str(l)+"</li>"
            text+="</ul>"
            text+="<br>Besten Dank"


            
            outlook = win32.Dispatch('outlook.application')
            mail = outlook.CreateItem(0)

            splitname=name.split(' ')
            splitname=[x.replace('ä','ae').replace('Ä','Ae').replace('ü','ue').replace('Ü','Ue').replace('ö','oe').replace('Ö','Oe').replace('ß','ss') for x in splitname]
            assert len(splitname)==2 or len(splitname)==1,"Cannot create email from name!"
            if len(splitname)==2:
                mail.To = splitname[0].lower()+"."+splitname[1].lower()+"@"+email_domain
            elif len(splitname)==1:
                mail.To = splitname[0].lower()+"@"+email_domain


            
            mail.Subject = email_subject
            mail.HtmlBody = text
            mail.Display(False)

            print("Created Email for "+name+" Email:"+mail.To)



if __name__ == "__main__":
    main()

