from dateutil import tz
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from subscription import Subscriber


LAVOVI_URL = ('''http://domashnakuhnqlavovi.info/\
%D0%BE%D0%B1%D0%B5%D0%B4%D0%BD%D0%BE-%D0%BC%D0%B5%D0%BD%D1%8E\
-%D0%B4%D0%BE%D0%BC%D0%B0%D1%88%D0%BD%D0%B0-%D0%BA%D1%83%D1%8\
5%D0%BD%D1%8F-%D0%BB%D0%B0%D0%B2%D0%BE%D0%B2%D0%B8-{0}-%D0%B3/''')


subscriber = Subscriber()


def menu(user=None):
    return get_menu()


def subscribe(user=None):
    subscriber.subscribe(user)
    # TODO: Think for better returning of response
    return 'Абониран сте успешно млади момко/девойко. ' +\
        'Ще получавате менюто всеки делничен ден в 11:45.'


def unsubscribe(user=None):
    subscriber.unsubscribe(user)
    return 'Абонамента е премахнат успешно.'


def get_menu():
    response = requests.get(get_today_url())
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        menu_content = soup.find_all('p')
        return '\n'.join([p.getText() for p in menu_content][:-8])
    else:
        return 'Не мога да ти кажа менюто за днес. Има някакъв проблем. :('


def get_today_url():
    today = datetime.now().strftime('%d-%m-%Y')
    return LAVOVI_URL.format(today)


def get_subscribers():
    return subscriber.get_subscribers()


def utc_to_local(utc):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    utc_time = datetime.strptime(utc, '%H:%M')
    utc_time = utc_time.replace(tzinfo=from_zone)

    return datetime.strftime(utc_time.astimezone(to_zone), '%H:%M')
