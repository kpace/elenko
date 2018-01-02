import datetime
import os
import re
import time
from slackclient import SlackClient
import requests
from bs4 import BeautifulSoup


RTM_READ_DELAY = 1  # 1 second delay between reading from RTM

COMMANDS = [
    'menu',
    'меню',
    'обедно меню',
    'какво си сготвил',
]

LAVOVI_URL = ('''http://domashnakuhnqlavovi.info/\
%D0%BE%D0%B1%D0%B5%D0%B4%D0%BD%D0%BE-%D0%BC%D0%B5%D0%BD%D1%8E\
-%D0%B4%D0%BE%D0%BC%D0%B0%D1%88%D0%BD%D0%B0-%D0%BA%D1%83%D1%8\
5%D0%BD%D1%8F-%D0%BB%D0%B0%D0%B2%D0%BE%D0%B2%D0%B8-{0}-%D0%B3/''')

BOT_TOKEN = os.environ.get('ELENKO_SLACK_TOKEN', None)
slack_client = SlackClient(BOT_TOKEN)


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            print(event)
            return event['text'], event['channel']
    return None, None


def handle_command(command, channel):
    default_response = 'Не съм сигурен какво означава *{0}*. '\
            'Опитай с *{1}*.'.format(command, ', '.join(COMMANDS))

    # make lowercase and remove puctuation
    command = command.lower()
    command = re.sub(r'[^\w\s]', '', command)
    # command = command.translate(None, string.punctuation)
    response = None
    for available_command in COMMANDS:
        if available_command.startswith(command):
            response = get_menu()

    return slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def get_today_url():
    today = datetime.datetime.now().strftime('%d-%m-%Y')
    return LAVOVI_URL.format(today)
    # print(LAVOVI_URL)
    # return LAVOVI_URL


def get_menu():
    response = requests.get(get_today_url())
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        menu_content = soup.find('div', attrs={'class': 'blog-post'}).find_all('p')
        return '\n'.join([p.getText() for p in menu_content][:-3])
    else:
        return 'Не мога да ти кажа менюто за днес. Има някакъв проблем. :('


if __name__ == "__main__":
        if slack_client.rtm_connect(with_team_state=False):
            print("Starter Bot connected and running!")
            while True:
                try:
                    command, channel = parse_bot_commands(slack_client.rtm_read())
                    if command:
                        handle_command(command, channel)
                except Exception:
                    import traceback
                    traceback.print_exc()
                time.sleep(RTM_READ_DELAY)
        else:
            print("Connection failed. Exception traceback printed above.")
