import sys
sys.path.append('/Users/oliverlewis/Work/StravaCO2')
 
from apis import APIRequest, APIResponse, AnyModel
from functools import cached_property
 
WEATHERAPI_URL = 'http://api.weatherapi.com/v1/'
WEATHERAPI_KEY = 'e7c7127ad1824f3db14210153262903'
 
 
class WeatherAPIRequest(APIRequest):
    def __init__(self, path: str, **query_parameters):
        super().__init__(
            WEATHERAPI_URL,
            path,
            {},                        
            key=WEATHERAPI_KEY,         
            **query_parameters
        )
        self.api_calls: int = 0
 
    @cached_property                    
    def response(self) -> APIResponse:
        self.api_calls += 1
        return super().response
 
 
def fetch_weather():
    request = WeatherAPIRequest(
        'current.json',
        q='51.0,0.0'                   
    )
    print(f"URL: {request.url}")       
    return request.response      
 
 
if __name__ == "__main__":
    print(fetch_weather())
