class Phrases:  
    WHEN = 'Коли плануєте до кінотеатру?'
    WHAT_TIME = 'В який час?'
    WHICH_CINEMA = 'Оберіть кінотеатр  або відправте ваше місцезнаходження щоб отримати інформацію тільки про найближчі кінотеатри'
    BOT_ERROR = 'Помилка роботи боту. Будь-ласка, спробуйте звернутися пізніше.'
    INPUT_ERROR = 'Помилка розпізнавання запиту. Спробуйте ще раз.'

    @classmethod
    def string_cinemas(cls, cinemas):
        reply = ''
        for index, cinema in enumerate(cinemas):
            if cinema.distance:
                reply += '/{} {} {}км'.format(index + 1, cinema.name, "{0:.2f}".format(cinema.distance)) + '\n'
            else:
                reply += '/{} {}'.format(index + 1, cinema.name) + '\n'
        
        return reply
    
    @classmethod
    def string_shows(cls, shows):
        reply = ''
        for show in shows:
            reply += '{} - {}'.format(show.time.strftime("%H:%M"), show.film_title)
            reply += '\n'
        return reply

    @classmethod
    def string_request(cls, request):
        reply = ''
        if request.date:
            reply += 'Дата: {}. '.format(request.date)
        if request.times:
            reply += 'Час початку сеансів: {}. '.format(request.printable_times())
        if request.cinema:
            reply += 'Кінотеатр: {}. '.format(request.cinema.name)
        reply += '\n'
        return reply
