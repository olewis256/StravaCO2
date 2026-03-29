import requests
import os

CLIMATIQ_ID = os.environ['CLIMATIQ_ID']
CLIMATIQ_URL = "https://api.climatiq.io/data/v1/estimate"

types_vehicle = {
            "car": "passenger_vehicle-vehicle_type_car-fuel_source_na-engine_size_na-vehicle_age_na-vehicle_weight_na",
            "aircraft": "passenger_flight-route_type_international-aircraft_type_na-distance_short_haul_lt_3700km-class_business-rf_included-distance_uplift_included",
            "train": "passenger_train-route_type_na-fuel_source_na"
        }  

class EmissionsError(Exception):
    
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Emissions API error {status_code}: {message}")

class Emissions:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {CLIMATIQ_ID}",
            "Content-Type": "application/json"
        })
    
    def estimate(self, distance: float, type: str) -> float:

        if type not in types_vehicle:
            raise ValueError(
                f"Unsupported vehicle type: {type}"
            )


        dist = int(float(distance/1000))  

        req = self.session.post(CLIMATIQ_URL,
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
        
        if req.status_code != 200: return

        res = req.json()

        return res["co2e"]