import requests
import logging
import re
SOURCE = "https://api.adsb.lol/v2/point/"
ROUTE = "https://api.adsbdb.com/v0/callsign/"
CALLSIGN = "https://api.adsbdb.com/v0/airline/"

class AircraftNearMe:
    def __init__(self, lat, long, range):
        self.lat = lat
        self.long = long
        self.range = range
        self.aircrafts_raw = self.get_aircrafts_raw()
        self.aircrafts_parsed = self.aircrafts_as_list()
        self.complete_info = self.append_route()
        

    def get_aircrafts_raw(self):
        response = requests.get(url = f"{SOURCE}/{self.lat}/{self.long}/{self.range}")
        return response.json()


    def aircrafts_as_list(self):
        
        return [item for item in self.aircrafts_raw['ac']]
    

        
    def append_route(self):
        result = []
        for item in self.aircrafts_parsed:
            flight = item['flight'].strip()
            callsign_airline = re.match(r"^\D*", flight).group()
            callsign_num =  flight.removeprefix(callsign_airline)
            
            callsign_response = requests.get(f"{CALLSIGN}{callsign_airline}")
            if callsign_response.status_code == 200 and callsign_response.json()['response'][0]['iata'] is not None:
                callsign_mapped = callsign_response.json()['response'][0]['iata']
                iata_callsign = callsign_mapped + callsign_num
                response = requests.get(url = f"{ROUTE}{iata_callsign}")
            else:
                response = requests.get(url = f"{ROUTE}{flight}")
            route_info = response.json()
            if response.status_code == 200:
                item['airline'] = route_info['response']['flightroute']['airline']['name']
                item['origin'] = {
                    "country" : route_info['response']['flightroute']['origin']['country_name'],
                    "airport" : route_info['response']['flightroute']['origin']['name'],
                    "lat"     : route_info['response']['flightroute']['origin']['latitude'],
                    "long"    : route_info['response']['flightroute']['origin']['longitude'],
                    }
                item['destination'] = {
                    "country" : route_info['response']['flightroute']['destination']['country_name'],
                    "airport" : route_info['response']['flightroute']['destination']['name'],
                    "lat"     : route_info['response']['flightroute']['destination']['latitude'],
                    "long"    : route_info['response']['flightroute']['destination']['longitude'],
                    }

                logging.info(f'caught info, flight number {flight}')
            else:
                item['airline']     = None
                item['destination'] = None
                item['origin']      = None
            result.append(item)
        return result 
            

if __name__ == "__main__":
    ini = AircraftNearMe(50.0461218,19.9765947,70)
    
    deb = 0 