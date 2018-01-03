import datetime
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
    return 'Абониран сте успешно.'


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
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    return LAVOVI_URL.format(today)
