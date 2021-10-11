import logging
from threading import Lock

class Event:
    def __init__(self, name, group, arguments = []):
        self.name = name
        self.group = group
        self.arguments = arguments

class Subscription:
    def __init__(self, group, callback, id):
        self.id = id
        self.group = group
        self.callback = callback

class Scheduler:
    def __init__(self):
        self._event_queue = []
        self._subscribers = []

        self._mutex = Lock()

        self.subscriber_count = 0

    def distribute_events(self):
        with self._mutex:
            for event in self._event_queue:
                for subscriber in self._subscribers:
                    if subscriber.group == event.group:
                        subscriber.callback(event)
            self._event_queue.clear()

    def subscribe(self, group, callback):
        logging.info(f"Scheduler: {self.subscriber_count} subscribed.")

        with self._mutex:
            subscriber = Subscription(group, callback, self.subscriber_count)
            self._subscribers.append(subscriber)
            self.subscriber_count += 1

        return subscriber.id

    def publish(self, group, name, arguments):
        with self._mutex:
            self._event_queue.append(Event(name, group, arguments))

    def unsubscribe(self, id):
        logging.info(f"Scheduler: {id} unsubscribed.")
        with self._mutex:
            if self._subscribers:
                self._subscribers[:] = [x for x in self._subscribers if not x.id == id]
