from typing import  Dict, Optional, Any
import requests
import asyncio
import json
from car import Car
from dataclasses import asdict
import os


class IFFFTAPI:
    DEAL_FOUND = "tesla_deal_found"
    DIGEST = "tesla_digest"

    token = os.getenv('IFFFT_TOKEN')

    async def trigger(self, event:str, data: str) -> Dict[str, str]:
        url = f"https://maker.ifttt.com/trigger/{event}/json/with/key/{self.token}"
        payload = json.dumps({
          "cars": data
        })
       
        headers = {
          'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if not response.ok:
          raise Exception(f"Request Failed!, exception is {response.status_code}, content is {response.content}" )
        
    
  
# api = IFFFTAPI()
# asyncio.run(api.trigger(IFFFTAPI.DEAL_FOUND, {"Cars": ['my 1231', 'm2 12312']}))