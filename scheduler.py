import logging
from threading import Lock, Condition

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
        self._publish_condition = Condition(Lock())

        self.subscriber_count = 0

    def distribute_events(self):
        with self._mutex:
            for event in self._event_queue:
                for subscriber in self._subscribers:
                    if subscriber.group == event.group:
                        subscriber.callback(event)
            self._event_queue.clear()

    def wait_and_distribute_events(self, timeout: float = None):
        logging.debug(f"Scheduler: {id(self)} is about to wait for incoming events")

        if self._event_queue:
            logging.debug(f"Scheduler: {id(self)} is going to distribute events without waiting")
            return self.distribute_events()
        else:
            logging.debug(f"Scheduler: {id(self)} is waiting for incoming events")
            with self._publish_condition:
                if self._publish_condition.wait(timeout):
                    assert self._event_queue, "_event_queue is empty, yet publish_condition indicates otherwise"
                    logging.debug(f"Scheduler: {id(self)} recieved some events after waiting, distributing")
                    return self.distribute_events()
                else:
                    logging.debug(f"Scheduler: {id(self)} stopped waiting because of time out, returning none")
                    return None

    def subscribe(self, group, callback):
        with self._mutex:
            logging.info(f"Scheduler: {self.subscriber_count} subscribed.")
            subscriber = Subscription(group, callback, self.subscriber_count)
            self._subscribers.append(subscriber)
            self.subscriber_count += 1

        return subscriber.id

    def publish(self, group, name, arguments):
        with self._mutex:
            self._event_queue.append(Event(name, group, arguments))

        with self._publish_condition:
            self._publish_condition.notify_all()

    def unsubscribe(self, id):
        # TODO(zndf): Check if id points to a valid subscription.
        logging.info(f"Scheduler: {id} unsubscribed.")
        with self._mutex:
            if self._subscribers:
                self._subscribers[:] = [x for x in self._subscribers if not x.id == id]
