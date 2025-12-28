import json
import requests
from requests.exceptions import HTTPError
import os
from dotenv import load_dotenv

load_dotenv()

hrj = '1370614665649979472'
fj = '1379787390155096105'
channelID = fj

def retrieve_messages(channelID):
    
    discordAuth  = os.getenv('DISCORD_KYLE')
    print(discordAuth)
    headers = {
        'authorization': f'{discordAuth}'
    }

    try:
        r = requests.get(f'https://discord.com/api/v9/channels/{channelID}/messages?limit=100', headers=headers)
        # If the response was successful, no Exception will be raised
        r.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6+
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6+
    else:
        jsonn = r.json()

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(jsonn, f, ensure_ascii=False, indent=4)
        
        #print(jsonn[0]['content'])
        print(jsonn)
        return jsonn
    
retrieve_messages(channelID)