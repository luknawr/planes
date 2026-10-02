import requests
import logging
SOURCE = "https://api.adsb.lol/v2/point/"
ROUTE = "https://api.adsbdb.com/v0/callsign/"


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
        

        for item in self.aircrafts_parsed:
            try:
                flight = item['flight'].strip()
                response = requests.get(url = f"{ROUTE}{flight}")
                origin = response.json()
                if response.status_code == 200:
                    item['airline'] = origin['response']['flightroute']['airline']['name']
                    item['from_country'] = origin['response']['flightroute']['origin']['country_name']
                    item['from_airport'] = origin['response']['flightroute']['origin']['name']
                    item['to_country'] = origin['response']['flightroute']['destination']['country_name']
                    item['to_airport'] = origin['response']['flightroute']['destination']['name']
                    logging.info(f'caught info, flight number {flight}')
                else:
                    item['airline']      = "unknown"
                    item['from_country'] = "unknown"
                    item['from_airport'] = "unknown"
                    item['to_country']   = "unknown"
                    item['to_airport']   = "unknown"
                    logging.error(f'Unknown response, content: {response.content}, flight: {flight}') #problem z kodami ICAO i IATA <- jedna strona zwraca icao, druga potrzebuje iata
                
            except Exception as e:
                logging.info('skipped on ground vehicle')
                continue

if __name__ == "__main__":
    ini = AircraftNearMe(50.0461218,19.9765947,60)
    
    deb = 0 