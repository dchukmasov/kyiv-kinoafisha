class Cinema:
    def __init__(self, id, name, latitude, longitude):
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.distance = None

    def get_coordinates(self):
        return float(self.latitude), float(self.longitude)

class Hall:
    def __init__(self, id, cinema_id):
        self.id = id
        self.cinema_id = cinema_id

class Film:
    def __init__(self, id, title):
        self.id = id
        self.title = title

class Show:
    def __init__(self, id, film_id, hall_id, time):
        self.id = id
        self.time = time
        self.film_id = film_id
        self.hall_id = hall_id
        self.cinema_name = None
        self.film_title = None



    



