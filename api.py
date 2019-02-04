import requests
import logging
import json
from entities import *
from datetime import datetime
from config import KINOTEATR_API_TOKEN

KINOTEATR_API_URL = 'http://api.kino-teatr.ua'
SHOWS_IN_CITY_ENDPOINT = ['/rest/city/', '/shows']


class ShowsInCity:
    """
    Class that wraps API calls. To be used by higher-level Request object
    """
    def __init__(self, city, date):
        self.content = list()
        self.cinemas = dict()
        self.halls = dict()
        self.films = dict()
        self.shows = list()

        # field are imported directly from JSON API response
        try:
            self.__dict__= API.get_shows_in_city_on_date(city, date)
        except APIError:
            raise

        # setting fields after JSON import
        try:
            self._objectify()
            self._set_shows()
        except Exception:
            logging.warning('error during API response parsing')
            raise
    
    def get_cinemas_with_shows(self, times):
        """
        Returns cinemas (objects) received from API that 1) have shows at given date (self.date) and between given times
        """
        # filter sessions based on time_min and time_max
        filtered_shows = [show for show in self.shows if times[0] <= show.time <= times[1]]

        # get hall_id from sessions and then cinema name from hall_id
        cinemas = {self.cinemas[self.halls[show.hall_id].cinema_id] for show in filtered_shows}

        return list(cinemas)

    def get_shows(self, cinema, times):    
        """
        Returns shows (objects) received from API that 1) occur in a given cinema 2) occur between given times
        """ 
        shows = [show for show in self.shows if times[0] <= show.time <= times[1] and show.cinema_name == cinema.name]
        return shows
    
    def _objectify(self):
        """
        Transforms raw dict fields into dicts of objects
        """
        # {id: cinema}
        self.cinemas = {item["id"]: Cinema(item["id"], item["name"], item["latitude"], item["longitude"]) for item in self.cinemas}

        # {id: hall}
        self.halls = {item["id"]: Hall(item["id"], item["cinema_id"]) for item in self.halls}

        # {id: film}
        self.films = {item["id"]: Film(item["id"], item["title"]) for item in self.films}

        # [shows]
        self.shows = [Show(item["id"], item["film_id"], item["hall_id"], datetime.strptime(times["time"], '%H:%M:%S')) for item in self.content for times in item["times"]]
    

    def _set_shows(self):
        """
        Assigning film titles and cinema names to shows for convenience
        """
        for show in self.shows:
            # assign film_title
            show.film_title = self.films[show.film_id].title

            # assing cinema_name
            show.cinema_name = self.cinemas[self.halls[show.hall_id].cinema_id].name


class APIError(Exception):
    pass

class API:
    """
    Low-level class that communicates with API. To be used by generic classes that wrap different endpoints responses.
    Has only class method. Variables are taken from config.py (TOKEN, URL)/
    """
    @classmethod
    def get_shows_in_city_on_date(self, city=1, date=str(datetime.now().date()), size=500):
        """
        Params for get request are hard-coded. Should be re-checked
        :return: API response
        """
        params = {'size': size,
                  'page': 0,
                  'detalization': 'FULL',
                  'apiKey': KINOTEATR_API_TOKEN,
                  'date': date}
        
        # URL is dynamic based on CITY
        url = KINOTEATR_API_URL + str(city).join(SHOWS_IN_CITY_ENDPOINT)

        r = requests.get(url, params=params)
        if not r.status_code == 200:
            logging.warning("API response status code '{}' endpoint '{}'".format(str(r.status_code), url))
            raise APIError

        return r.json()




