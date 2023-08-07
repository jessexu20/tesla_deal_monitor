from datetime import datetime 
import requests
from urllib.parse import quote
import json
from car import Car
from typing import Dict, List
import asyncio
from digest import Digest
from logger import Logger
from push_bullet_api import PushBulletAPI
from iffft_api import IFFFTAPI

class DealFinder:
    RAW_LOG_FILE_PATH = "tesla_price_raw.log"
    DISCOUNT_TO_ALERT = 3500
    COOL_DOWN = 900
    TIME_TO_CLEAR_CACHE = 1
    cache = {}
    
    def __init__(self):
        self.push_bullet_api = PushBulletAPI()
        self.iffft_api = IFFFTAPI()
        self.already_alerted = {}
        self.logger = Logger(self.RAW_LOG_FILE_PATH)
        self.digest_service = Digest()
    
    def generate_uri(self, model, condition, arrangeby, order, market, language, super_region, lng, lat, zip_code, range_val, region, offset, count) -> str:
        base_url = "https://www.tesla.com/inventory/api/v1/inventory-results"
        query_params = {
            "query": {
                "model": model,
                "condition": condition,
                "options": {
                    "TRIM": "MYAWD,LRAWD",
                },
                "arrangeby": arrangeby,
                "order": order,
                "market": market,
                "language": language,
                "super_region": super_region,
                "lng": lng,
                "lat": lat,
                "zip": zip_code,
                "range": range_val,
                "region": region
            },
            "offset": offset,
            "count": count,
            "outsideOffset": 0,
            "outsideSearch": False
        }
        encoded_params = quote(json.dumps(query_params))
        uri = f"{base_url}?query={encoded_params}"
        return uri
    
    async def async_get_cars(self, url) -> List[Car]: 
        try:
            response = requests.get(url)
            response.raise_for_status()
            results = json.loads(response.text)['results']
            available_cars = []
    
            for result in results: 
                model_name = result["TrimName"].replace("All-Wheel Drive", '').replace(" Dual Motor", '').strip(' ')
                price = result["PurchasePrice"]
                color = result["PAINT"]
                odometer = result["Odometer"]
                options = result["OptionCodeSpecs"]["C_OPTS"]["options"]
                discount = result["Discount"]
                vin = result["VIN"]
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
    
    async def async_monitor(self, model: str):
        """
        This function monitors the Tesla inventory for deals and sends notifications if any are found.
        """
        uri = self.generate_uri(
            model=model,
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
            count=50
        )
        available_cars = await self.async_get_cars(uri)
        discounted = self.get_discounted_tesla(available_cars)
    
        try:
            await self.log(discounted_cars=discounted)
            await self.notify(discounted)

        except Exception as e:
            print(e)

    async def notify(self, discounted_cars: List[Car]):
        try:
            raw_text = ''
            email_content = ''
            count = 0 
            for car in discounted_cars:
                if car.discount > self.DISCOUNT_TO_ALERT and count < 10 and car.vin not in self.already_alerted: 
                    count += 1
                    self.already_alerted[car.vin] = car.as_record(datetime.now())
                    email_content += f"<br>{car.format_in_html()}"
                    raw_text += f"{car.display_info()} \n"
            if count > 0:
                print(f"Ready to notify: {count} cars")
                await self._async_send_chrome_notif(raw_text)
                await self.iffft_api.trigger(IFFFTAPI.DEAL_FOUND, f"<br>{email_content}<br>")

        except Exception as e:
            print(e)

    
    async def log(self,  discounted_cars: List[Car]):
        """
            "vin: car "
        """
        raw_log = {}
        ts = datetime.now() 
        try:
            for car in discounted_cars:
                raw_log[car.vin] = car.as_record(ts)
            await self.logger.async_write_log_file(raw_log)
        
        except Exception as e:
            print(e)


    async def async_start_monitor(self):
        """
        This function starts the monitoring process, continuously checking for deals at regular intervals.
        """
        while True:
            await self.async_monitor("my")
            print(f"we will wait for {self.COOL_DOWN} seconds and try again!")
            cur_time = datetime.now()
            if cur_time.minute < 20:
                print(f"Sending digest for{cur_time.hour}")
                digest_content = await self.digest_service.async_generate_hourly_digest_email_content()
                await self.iffft_api.trigger(IFFFTAPI.DIGEST, f"<br>{digest_content}<br>")
            if cur_time.hour == self.TIME_TO_CLEAR_CACHE:
                self.cache = {}
            await asyncio.sleep(self.COOL_DOWN)

deals = DealFinder()
print("****** Start Monitoring, you will be notified!!******")
asyncio.run(deals.async_start_monitor())
