import re
import logging
from datetime import datetime, timedelta


class ParsingError(Exception):
    pass


class Parser:
    @classmethod
    def parse_date(cls, message):
        """
        Method recognizes: latin/cyrillic 'C', 'c', 'cьогодні' == Today
        cyrillic 'З', 'з', 'завтра' == Tomorrow
        Any date in format 'DD.MM'
        Raises UserInputError if other message received
        :param message: message received in Telegram
        :return: date in str('YYYY-MM-DD')
        """
        if 'сьогодні' in message.lower() or 'с' == message.lower() or 'c' == message.lower():
            date = str(datetime.today().date())
        elif 'завтра' in message.lower() or 'з' == message.lower():
            date = str(datetime.today().date() + timedelta(days=1))
        else:
            regex_result = re.findall(r'([0-9]+?)\.([0-9]+)', message)
            if not len(regex_result) == 1:
                logging.warning('parse date len(regex_result) != 1')
                raise ParsingError
            month = int(regex_result[0][1])
            day = int(regex_result[0][0])
            try:
                datetime(year=2019, month=month, day=day)
            except ValueError:
                logging.warning('parse date cannot create datetime object')
                raise ParsingError
            date = str(datetime.today().year) + '-' + regex_result[0][1] + '-' + regex_result[0][0]
        return date


    @classmethod
    def parse_time(cls, message):
        """
        Method recognizes: numbers from 0 to 24
        Raises UserInputError if other message received
        :param message: message received in Telegram
        :return: time in str('HH')
        """
        # expecting 2 numbers - time_min and time_max
        times = message.split("-")

        if len(times) != 2:
            logging.warning('parse_time error: not 2 items received after times parsing')
            raise ParsingError


        try:
            time_min =  datetime.strptime(times[0], '%H:%M')
            time_max = datetime.strptime(times[1], '%H:%M')
        except Exception:
            logging.warning('parse_time error converting string to datetime')
            raise ParsingError

        return time_min, time_max


    @classmethod
    def parse_cinema(cls, message, cinemas, cinemas_ids_mapping):
        """
        Method parses User message and returns cinema objects if cinema with such name/ID is found among {cinemas}
        Raises UserInputError if not found
        :param message: message received in Telegram
        :param cinemas: list of Cinema objects to search among
        :return: Cinema object if found
        """
        cinema_id = re.findall(r'^/?([0-9]+)', message.text)
        if cinema_id:
            try:
                return Parser._parse_cinema_id(int(cinema_id[0]), cinemas_ids_mapping)
            except ParsingError:
                logging.warning('parse_cinema found cinema_id in message but no proper mapping')
                pass

        for cinema in cinemas:
            if message.text.lower() in cinema.name.lower():
                return cinema

        logging.warning('parse_cinema no proper cinema_name in message')
        raise ParsingError


    @classmethod
    def _parse_cinema_id(cls, cinema_id, cinemas_ids_mapping):
        if cinema_id in cinemas_ids_mapping:
            cinema = cinemas_ids_mapping[cinema_id]
            return cinema
        else:
            raise ParsingError






