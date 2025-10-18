import requests
import os

CLIMATIQ_ID = os.environ['CLIMATIQ_ID']

types_vehicle = {
            "car": "passenger_vehicle-vehicle_type_car-fuel_source_na-engine_size_na-vehicle_age_na-vehicle_weight_na",
            "aircraft": "passenger_flight-route_type_international-aircraft_type_na-distance_short_haul_lt_3700km-class_business-rf_included-distance_uplift_included",
            "train": "passenger_train-route_type_na-fuel_source_na"
        }  

class Emissions:

    def __init__(self):
        self.api_calls = 0
    
    @classmethod
    def emissions(cls, distance, type):
        dist = int(float(distance/1000))  

        req = requests.post("https://api.climatiq.io/data/v1/estimate",
            headers={
                "Authorization": f"Bearer {CLIMATIQ_ID}",
                "Content-Type": "application/json"
            },
            json= {
            "emission_factor": {
            "activity_id": types_vehicle[type],      
            "data_version": "^26"
            },
            "parameters": {
            "distance": dist,
            "distance_unit": "km"
            }}
        )
        res = req.json()
        if req.status_code != 200: return

        return res['co2e']