from datetime import datetime
from api import ShowsInCity, APIError
from parser import Parser
from locator import Locator
import logging

class RequestError(Exception):
    pass


class Request:
    """
    High-level object created for each communication with user. To be used for data extraction for user.
    """
    def __init__(self, state):
        # added during init
        self.state = state

        # provided by user
        self.date = str(datetime.now().date())
        self.times = tuple([datetime.now().strftime('%H'), 23])
        
        # will be initialized after date and time are provided by user
        self.shows_in_city = None
        
        # chosen by user after options are provided to him
        self.cinema = None

        # will be calculated
        self.cinemas = []
        self.mapped_cinemas = {}

    def get_cinemas(self):
        if not self.shows_in_city:
            self._init_sic()

        self.cinemas = self.shows_in_city.get_cinemas_with_shows(self.times)
        self._map_cinemas()

        if not self.cinemas:
            raise RequestError

        return self.cinemas


    def get_closest_cinemas(self, latitude, longitude):
        """
        Returns 10 closest cinemas with available sessions
        """
        if not self.shows_in_city:
            self._init_sic()
        
        if not self.cinemas:
            self.cinemas = self.shows_in_city.get_cinemas_with_shows(self.times)

        # overwriting all cinemas to only closest to proper map them
        self.cinemas = Locator.get_verified_closest(latitude, longitude, self.cinemas)
        self._map_cinemas()

        return self.cinemas

           
    def get_shows(self):
        if not self.shows_in_city:
            self._init_sic()
        
        shows = self.shows_in_city.get_shows(self.cinema, self.times)

        if not shows:
            raise RequestError

        shows.sort(key=lambda x: x.time)

        return shows

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def set_cinema_from_message(self, message):
        try:
            self.cinema = Parser.parse_cinema(message, self.cinemas, self.mapped_cinemas)
        except Exception:
            raise
    
    def set_times_from_cb_data(self, cbdata):
        try:
            self.times = Parser.parse_time(cbdata)
        except Exception:
            raise

    def set_date_from_cb_data(self, cbdata):
        try:
            self.date = Parser.parse_date(cbdata)
        except Exception:
            raise

    def printable_times(self):
        
        time_min = self.times[0].strftime('%H:%M')
        time_max = self.times[1].strftime('%H:%M')

        return ('з {} до {}'.format(time_min, time_max))

    def _map_cinemas(self):
        self.mapped_cinemas = dict()
        for index, cinema in enumerate(self.cinemas):
            self.mapped_cinemas[index + 1] = cinema

    def _init_sic(self):
        if not self.date:
            logging.warning('trying to init request.shows_in_city without request.date set')
            raise RequestError
        try:
            self.shows_in_city = ShowsInCity(1, self.date)
        except Exception:
            raise