import geopy.distance
from math import cos, asin, sqrt

class Locator:
    """
    Class that finds nearest cinemas based on provided lat and long
    """
    @classmethod
    def get_verified_closest(cls, latitude, longitude, cinemas, result_amount=10):
        """
        :param lat: float latitude
        :param lon: float longitude
        :param cinemas: list of cinemas to review for the closest
        :param result_amount: number of closest cinemas returned
        :return: list of closest cinemas (Cinema objects)
        """
        # calculate distance for all cinemas
        for cinema in cinemas:
            cinema.distance = cls._get_accurate_distance((latitude, longitude), cinema.get_coordinates())
            
        
        # create list sorted by distance
        sorted_cinemas = sorted(cinemas, key=lambda c: c.distance)

        # check length of result and re-assign if needed
        if len(sorted_cinemas) < result_amount:
            result_amount = len(sorted_cinemas)

        return sorted_cinemas[:result_amount]


    @classmethod
    def _get_accurate_distance(cls, coords_1, coords_2):
        return geopy.distance.vincenty(coords_1, coords_2).km
