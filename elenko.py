import os
import re
import time
import schedule
from slackclient import SlackClient
from utils import menu, subscribe, unsubscribe, get_subscribers


RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
SEND_MENU_TIME = '11:45'
BOT_TOKEN = os.environ.get('ELENKO_SLACK_TOKEN', None)
slack_client = SlackClient(BOT_TOKEN)

COMMANDS = {
    'menu': menu,
    'subscribe': subscribe,
    'unsubscribe': unsubscribe,
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


if __name__ == '__main__':
        if slack_client.rtm_connect(with_team_state=False):
            print('Starter Bot connected and running!')
            schedule.every().day.at(SEND_MENU_TIME).do(send_daily_menu)
            while True:
                try:
                    command, channel, user = read_command(
                            slack_client.rtm_read()
                    )
                    if command:
                        handle_command(command, channel, user)
                    # send daily menu to subscribed users
                    schedule.run_pending()
                except Exception:
                    import traceback
                    traceback.print_exc()
                time.sleep(RTM_READ_DELAY)
        else:
            print('Connection failed. Exception traceback printed above.')
