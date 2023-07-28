from dataclasses import dataclass, asdict
import json

@dataclass
class Car:
    model: str
    color: str
    price: int
    price_before_discount: int
    odometer: int
    discount: int
    vin:str
    
    def get_link(self):
        return f"https://www.tesla.com/my/order/{self.vin}"
    
    def has_discount(self):
        return self.discount > 0
    
    def is_new(self):
        return "NEW"  if self.odometer <= 100  else "USED"
    
    def as_record(self, time:str)-> str:
        car_data = asdict(self)
        car_data["status"] = self.is_new()
        car_data["link"] = self.get_link()
        car_data["parse_time"] = time
        return json.dumps(car_data)


    def display_info(self):
        return f"{self.is_new()} | Price: now: {self.price} | discount: {self.discount} | before: {self.price_before_discount}  | {self.model} | Odometer: {self.odometer}| Vin: {self.vin} |color: {self.color} | link: {self.get_link()} "

    def format_in_html(self):
        html_template = """
<h1>Model: {model}</h1>
<ul>
    <li>Status: {status}</li>
    <li>Price: Now {price} (Discounted from {price_before_discount}, Save {discount})</li>
    <li>Model: {model}</li>
    <li>Odometer: {odometer} miles</li>
    <li>VIN: {vin}</li>
    <li>Color: {color}</li>
    <li><Link: {link}</li>
</ul>
        """
        car_data = asdict(self)
        car_data["status"] = self.is_new()
        car_data["link"] = self.get_link()
        
        formatted_html = html_template.format(**car_data)
        return formatted_html.replace("\n", '')