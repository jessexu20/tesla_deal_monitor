import requests
from urllib.parse import quote
import json
from bs4 import BeautifulSoup
from car import Car
from typing import  List
import asyncio
from push_bullet_api import PushBulletAPI
from iffft_api import IFFFTAPI

class DealFinder: 
    
    # init method or constructor
    def __init__(self):
        self.push_bullet_api = PushBulletAPI()
        self.iffft_api = IFFFTAPI()
    
    def generate_uri(self, model, condition, arrangeby, order, market, language, super_region, lng, lat, zip_code, range_val, region, offset, count) -> str:
        base_url = "https://www.tesla.com/inventory/api/v1/inventory-results"

        # Format the parameters into the query string
        query_params = {
            "query":{
                "model":model,
                "condition":condition,
                "options":{
                    "TRIM":"MYAWD,LRAWD",
                },
                "arrangeby":arrangeby,
                "order":order,
                "market":market,
                "language":language,
                "super_region":super_region,
                "lng":lng,
                "lat":lat,
                "zip":zip_code,
                "range":range_val,
                "region":region
            },
            "offset":offset,
            "count":count,
            "outsideOffset":0,
            "outsideSearch":False
        }

        # Convert the query_params dictionary to a URL-encoded string
        encoded_params = quote(json.dumps(query_params))

        # Combine the base URL and the encoded query parameters to form the complete URI
        uri = f"{base_url}?query={encoded_params}"
        return uri
    
    async def async_get_cars(self, url) -> List[Car]: 
        try:
            response = requests.get(url)
    
            response.raise_for_status()
            # print(response.text)
            results = json.loads(response.text)['results']
            
    
            available_cars = []
    
            for result in results: 
                model_name = result["TrimName"].replace("All-Wheel Drive", '').replace(" Dual Motor", '').strip(' ')
                price = result["PurchasePrice"]
                color = result["PAINT"]
                odometer = result["Odometer"]
                options = result["OptionCodeSpecs"]["C_OPTS"]["options"]
                discount= result["Discount"]
                vin=result["VIN"]
                # for opt in options:
    #                 if "code":"$PPSW",
                price_before_discount = result["TotalPrice"]
                my_car = Car(model_name, color, price, price_before_discount, odometer, discount, vin)
                available_cars.append(my_car)
            
            return available_cars

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None



    def get_discounted_tesla(self, available_cars: List[Car]):
        max_discount = 0
        min_price = 100000
        available_cars.sort(key=lambda car: car.discount, reverse=True)
        available_cars = filter(Car.has_discount, available_cars)
        return available_cars
        

    async def _async_send_chrome_notif(self, content: str):
        devices_map = await self.push_bullet_api.fetch_registered_devices()
        iden = devices_map["Chrome"]
        await self.push_bullet_api.send_push_notification("Deal alert", content)
        
    
    async def async_monitor(self):
        uri = self.generate_uri(
            model="my",
            condition="new",
            arrangeby="Price",
            order="asc",
            market="US",
            language="en",
            super_region="north america",
            lng=-122.0723816,
            lat=37.31317,
            zip_code="95014",
            range_val=200,
            region="CA",
            offset=0,
            count=3
        )

        available_cars = await self.async_get_cars(uri)
        discounted = self.get_discounted_tesla(available_cars)
    
        try:
            raw_text = ''
            email_content = ''
            count = 0 
            for car in discounted:
                if car.discount >= 2500:
                    count+=1
                    email_content += f"<br>{car.format_in_html()}"
                    raw_text += f"{car.display_info()} \n"
            if count > 0:
                print("ready to send notif")
                await self._async_send_chrome_notif(raw_text)
                await self.iffft_api.trigger(IFFFTAPI.DEAL_FOUND, f"<br>{email_content}<br>")

        except Exception as e:
            print(e)
        
    
    async def async_start_monitor(self):
        while(True):
            await self.async_monitor()
            await asyncio.sleep(10)


deals = DealFinder()
print("****** Start Monitoring, you will be notified!!******")
asyncio.run(deals.async_monitor())
    
    
    
