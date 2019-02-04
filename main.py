from collections import defaultdict, namedtuple
from datetime import datetime, timedelta
from telebot import types, TeleBot
from config import TELEBOT_TOKEN
from phrases import Phrases
from request import Request
from parser import ParsingError


WEEK_DAYS = {'Mon': 'Пн',
             'Tue': 'Вт',
             'Wed': 'Ср',
             'Thu': 'Чт',
             'Fri': 'Пт',
             'Sat': 'Сб',
             'Sun': 'Нд'}

# User states to handle the flow of dialogue with bot
SELECT_DATE, SELECT_TIME, SELECT_CINEMA = range(3)

# Current user's request
CURRENT_REQUESTS = defaultdict(lambda:  Request(SELECT_DATE))

# To handle callback_query buttons
Button = namedtuple('Button', ['text', 'callback_data'])

def create_date_buttons(days):
    now = datetime.now()
    dates = [now + timedelta(days=x) for x in range(2, days + 2)]
    return [Button(WEEK_DAYS.get(date.strftime('%a')) + ' ' + date.strftime('%d.%m'),
                   date.strftime('%d.%m')) for date in dates]

BUTTONS = {SELECT_DATE: [Button('Cьогодні', 'c'),
                         Button('Завтра', 'з'),
                         *[button for button in create_date_buttons(6)]],
           SELECT_TIME: [Button('До обіду', '00:00-15:59'),
                         Button('Після обіду', '13:00-23:59'),
                         Button('Цілий день', '00:00-23:59'),
                         Button('Ввечорі', '17:00-23:59')],
           SELECT_CINEMA: [Button('Перелік кінотеатрів', 'get_cinemas')]
           }


bot = TeleBot(TELEBOT_TOKEN)

def create_inline_keyboard(message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [types.InlineKeyboardButton(text=button.text, callback_data=button.callback_data)
            for button in BUTTONS[get_state(message)]]
    keyboard.add(*buttons)
    return keyboard


def get_state(message):
    return CURRENT_REQUESTS[message.chat.id].state


def update_state(message, state):
    CURRENT_REQUESTS[message.chat.id].state = state


# STEP 1 - (no state yet) - Asking for a DATE from user
@bot.message_handler(commands=['start'])
def start_dialogue(message):

    # safety POP from current requests
    CURRENT_REQUESTS.pop(message.chat.id, None)

    # create new request. Request has now SELECT_DATE state
    CURRENT_REQUESTS[message.chat.id].set_chat_id(message.chat.id)
    
    bot.send_message(message.chat.id, Phrases.WHEN, reply_markup=create_inline_keyboard(message))


# STEP 2 - SELECT_DATE state - Checking date and asking for a time from user
@bot.callback_query_handler(func=lambda callback_query: get_state(callback_query.message) == SELECT_DATE)
def date_choosing_inline(callback_query):
    message = callback_query.message
    request = CURRENT_REQUESTS[message.chat.id]

    # checking/assigning date
    try:
        request.set_date_from_cb_data(callback_query.data)
    except ParsingError:
        bot.send_message(message.chat.id, Phrases.INPUT_ERROR)
        return
    except Exception:
        bot.send_message(message.chat.id, Phrases.BOT_ERROR)
        CURRENT_REQUESTS.pop(message.chat.id, None)
        return
    
    # DATE checked, not asking to select time
    update_state(message, SELECT_TIME)

    bot.edit_message_text(Phrases.WHEN, chat_id=message.chat.id,
                              message_id=message.message_id, reply_markup=create_inline_keyboard(message))


# STEP 3 - SELECT_TIME state - Checking time and asking for a cinema from user
@bot.callback_query_handler(func=lambda callback_query: get_state(callback_query.message) == SELECT_TIME)
def time_choosing_inline(callback_query):
    message = callback_query.message
    request = CURRENT_REQUESTS[message.chat.id]

    # CHECKING TIME
    try:
        request.set_times_from_cb_data(callback_query.data)
    except ParsingError:
        bot.send_message(message.chat.id, Phrases.INPUT_ERROR)
        return
    except Exception:
        bot.send_message(message.chat.id, Phrases.BOT_ERROR)
        CURRENT_REQUESTS.pop(message.chat.id, None)
        return
    
    update_state(message, SELECT_CINEMA)

    bot.edit_message_text(chat_id=message.chat.id, text=Phrases.WHICH_CINEMA,
                    message_id=message.message_id, reply_markup=create_inline_keyboard(message))

    

# STEP 4.A - SELECT_CINEMA - Sending the list of all cinemas with available sessions on date at time selected earlier
@bot.callback_query_handler(func=lambda callback_query: callback_query.data == 'get_cinemas' and get_state(callback_query.message) == SELECT_CINEMA)
def send_available_cinemas(callback_query):

    message = callback_query.message
    request = CURRENT_REQUESTS[message.chat.id]

    try:
        cinemas = request.get_cinemas()
    except Exception:
        bot.send_message(message.chat.id, Phrases.BOT_ERROR)
        CURRENT_REQUESTS.pop(message.chat.id, None)
        return

    bot.send_message(message.chat.id, Phrases.string_cinemas(cinemas))

# STEP 4.B - SELECT_CINEMA - if location sent - sending 10 (or less if less) closest cinemas with available sessions on date at time selected earlier
@bot.message_handler(content_types=['location'], func=lambda message: get_state(message) == SELECT_CINEMA)
def calculate_and_send_closest_cinemas(message):

    bot.send_message(message.chat.id, 'Шукаю...')

    request = CURRENT_REQUESTS[message.chat.id]

    cinemas = request.get_closest_cinemas(message.location.latitude, message.location.longitude) 

    bot.send_message(message.chat.id, Phrases.string_cinemas(cinemas))
    

# STEP 5 - sending shows for selected cinema/date/time
@bot.message_handler(func=lambda message: get_state(message) == SELECT_CINEMA)
def sending_sessions(message):
    request = CURRENT_REQUESTS[message.chat.id]

    try:
        request.set_cinema_from_message(message)
    except ParsingError:
        bot.send_message(message.chat.id, Phrases.INPUT_ERROR)
        return
    except Exception:
        bot.send_message(message.chat.id, Phrases.BOT_ERROR)
        CURRENT_REQUESTS.pop(message.chat.id, None)
        return

    try:
        shows = request.get_shows()
    except Exception:
        bot.send_message(message.chat.id, Phrases.BOT_ERROR)
        CURRENT_REQUESTS.pop(message.chat.id, None)
        return
 
    reply = Phrases.string_request(request)
    reply += Phrases.string_shows(shows)
    
    bot.send_message(message.chat.id, reply)


if __name__ == '__main__':
    bot.polling(none_stop=True)
