import os
import pickle


class Subscriber:
    def __init__(self):
        self.file_name = 'subscribers.bin'
        self.load_subscribers()

    def load_subscribers(self):
        if os.path.isfile(self.file_name):
            with open(self.file_name, 'rb') as file:
                self.subscribers = pickle.load(file)
        else:
            self.subscribers = set()
        print(self.subscribers)

    def subscribe(self, user_id):
        self.subscribers.add(user_id)
        print('Subscribing %s' % user_id)
        print(self.subscribers)
        self._flush()

    def unsubscribe(self, user_id):
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            print('Unsubscribing %s' % user_id)
            self._flush()

    def _flush(self):
        with open(self.file_name, 'wb') as file:
            pickle.dump(self.subscribers, file, pickle.HIGHEST_PROTOCOL)

    def get_subscribers(self):
        return self.subscribers
