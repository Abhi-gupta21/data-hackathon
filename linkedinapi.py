import requests
import json 
from dotenv import load_dotenv
import os 

load_dotenv()

class linkapi:
    def __init__(self, text):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKENN')
        self.urn = os.getenv('URNN')
        self.client_id = os.getenv('CLIENT_ID')
        self.client_secret = os.getenv('CLIENT_SECRET')
        self.feed=text


    def postfeed(self):
        url_access = 'https://api.linkedin.com/v2/ugcPosts'



        headers = {
            'X-Restli-Protocol-Version': '2.0.0',
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }


        data = {
            "author": f"urn:li:person:{self.urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": self.feed
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }


        response = requests.post(url_access, headers=headers, data=json.dumps(data))
        return response.status_code





        