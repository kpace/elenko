import os
import re
import time
import schedule
from slackclient import SlackClient
from websocket import WebSocketConnectionClosedException
from utils import menu, subscribe, unsubscribe, get_subscribers, eet_to_utc


RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
SEND_HOUR_EET = 11
SEND_MINUTE_EET = 45
BOT_TOKEN = os.environ.get('ELENKO_SLACK_TOKEN', None)
slack_client = SlackClient(BOT_TOKEN)

COMMANDS = {
    'меню': menu,
    'абонирай ме': subscribe,
    'спри абонамента': unsubscribe,
}


def read_command(slack_events):
    for event in slack_events:
        if event['type'] == 'message' and 'subtype' not in event \
                and 'bot_id' not in event:
            print(event)

            # make lowercase and remove puctuation
            command = event['text'].lower()
            command = re.sub(r'[^\w\s]', '', command)
            return command, event['channel'], event['user']
    return None, None, None


def handle_command(command, channel, user):
    response = 'Не съм сигурен какво означава *{0}*. '\
            'Опитай с *{1}*.'.format(command, ', '.join(COMMANDS.keys()))

    if command in COMMANDS:
        response = COMMANDS[command](user)

    return send_message(channel, response)


def send_message(channel, text):
    return slack_client.api_call(
        'chat.postMessage',
        channel=channel,
        text=text,
        as_user=True
    )


def send_daily_menu():
    for subscriber in get_subscribers():
        print('Sending daily menu to user: %s' % subscriber)
        send_message(subscriber, menu())


def schedule_weekday(at, job):
    """ Schedules task for every weekday at given time """
    schedule.every().monday.at(at).do(job)
    schedule.every().tuesday.at(at).do(job)
    schedule.every().wednesday.at(at).do(job)
    schedule.every().thursday.at(at).do(job)
    schedule.every().friday.at(at).do(job)


if __name__ == '__main__':
        if slack_client.rtm_connect(with_team_state=False):
            print('Starter Bot connected and running!')
            send_time_utc = eet_to_utc(SEND_HOUR_EET, SEND_MINUTE_EET)
            print('Will send menu in %s:%s local time, which is %s UTC.'
                  % (SEND_HOUR_EET, SEND_MINUTE_EET, send_time_utc))
            print('Subscribed users: %s' % str(get_subscribers()))
            schedule_weekday(send_time_utc, send_daily_menu)
            while True:
                try:
                    command, channel, user = read_command(
                            slack_client.rtm_read()
                    )
                    if command:
                        handle_command(command, channel, user)
                    # send daily menu to subscribed users
                    schedule.run_pending()
                except WebSocketConnectionClosedException:
                    print('Caught websocket disconnect, reconnecting...')
                    slack_client.rtm_connect(with_team_state=False)
                except Exception:
                    import traceback
                    traceback.print_exc()
                time.sleep(RTM_READ_DELAY)
        else:
            print('Connection failed. Exception traceback printed above.')
