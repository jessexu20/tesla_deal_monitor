from typing import  Dict, Optional
import requests
import asyncio
import json
import os

class PushBulletAPI:
    token = os.getenv('PUSH_BULLET_TOKEN')
    async def fetch_registered_devices(self) -> Dict[str, str]:
        url = "https://api.pushbullet.com/v2/devices"
        headers = {
          'Access-Token': self.token
        }
        response = requests.request("GET", url, headers=headers)
        devices_info = json.loads(response.text)["devices"]
        devices_iden = {}
        for device in devices_info:
            if device["active"]:
                devices_iden[device["nickname"]] = device["iden"]
        
        return devices_iden
        
    async def send_push_notification(self, title: str, content:str, email: Optional[str] = None, device_iden: Optional[str] = None):
        url = "https://api.pushbullet.com/v2/pushes"
        
        data = {        
            "body": content,
            "title": title,
            "type": "note"
        }
        
        if email:
            data["email"] = email
        
        if device_iden:
            data["device_iden"] = device_iden
            
        payload = json.dumps(data)
        headers = {
          'Access-Token': self.token,
          'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response
        


