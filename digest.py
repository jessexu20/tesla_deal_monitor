import asyncio
import json
from typing import Dict, Any
from datetime import datetime


class Digest:

    RAW_LOG_FILE_PATH = "tesla_price_raw.log"
    LIMIT_NUMBER = 7

    async def async_generate_hourly_digest_email_content(self):
        cur_digest = await self._async_generate_hourly_digest_info()
        if not cur_digest:
            return None
        cur_time = datetime.now().ctime()
        html = f"<h1> Time {cur_time}</h1>\n"
        count = 0
        for k, v in cur_digest.items():
            car_info = self._format_in_html(cur_digest[k])
            html+=(car_info)
            count+=1
            if count == self.LIMIT_NUMBER:
                break
        return html


    def _format_in_html(self, data: Dict[str, Any]):
        html_template = """
<ul>
    <li>Model: {color}, {model}</li>
    <li>Status: {status}</li>
    <li>Discount {discount})</li>
</ul>
        """
                
        formatted_html = html_template.format(**data)
        return formatted_html.replace("\n", '')


    async def _async_generate_hourly_digest_info(self) -> Dict[str, Any]:
        try:
            with open(self.RAW_LOG_FILE_PATH, "r") as file: 
                cur_time = datetime.now()
                cur_digest= {}

                for line in file.readlines():
                    record = json.loads(line)
                    for k, v in record.items():
                        car = json.loads(v)
                        parse_time = car["parse_time"]
                        parse_dt = datetime.fromtimestamp(parse_time)
                        if parse_dt.date() == cur_time.date() and parse_dt.hour == cur_time.hour: 
                            cur_digest[k] = {
                                "model" : car["model"],
                                "discount": car["discount"],
                                "color": car["color"],
                                "status": car["status"]
                            }
                return cur_digest
        except Exception as e:
            print(e) 

# d =  Digest()
# asyncio.run(d.async_generate_hourly_digest_email_content())
