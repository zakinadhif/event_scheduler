import logging
from scheduler import Scheduler, Event

from typing import Optional
from threading import Lock, Condition
import functools


class Subscriber:
    def __enter__(self):
        self.event_queue = []
        self.subscription_ids = {}
        self.mutex = Lock()
        self.read_condition = Condition(Lock())
        return self

    def __exit__(self, *exc):
        if not self.subscription_ids:
            return

        self._unsubscribe_all()

    def poll_event(self) -> Optional[Event]:
        with self.mutex:
            if self.event_queue:
                return self.event_queue.pop()
        return None

    def wait_event(self, timeout = None) -> Optional[Event]:
        logging.debug(f"Subscriber: {id(self)} is about to wait for an event")

        event = self.poll_event()

        if event:
            logging.debug(f"Subscriber: {id(self)} is going to return an event without waiting")
            return event
        else:
            logging.debug(f"Subscriber: {id(self)} is waiting for an event")
            with self.read_condition:
                if self.read_condition.wait(timeout):
                    assert self.event_queue, "event_queue is empty, yet read_condition indicates otherwise"
                    logging.debug(f"Subscriber: {id(self)} retrieved an event after waiting, returning event")
                    return self.poll_event()
                else:
                    logging.debug(f"Subscriber: {id(self)} stopped waiting because of time out, returning none")
                    return None

    def set_default_scheduler(self, scheduler: Scheduler) -> None:
        self.default_scheduler = scheduler

    def subscribe_into(self, group: str, scheduler: Scheduler = None) -> None:
        if scheduler is None:
            assert self.default_scheduler, """
            Default scheduler is not set, yet subscribe_into is called
            without destination scheduler passed in.
            """

            scheduler = self.default_scheduler

        id = scheduler.subscribe(group, self._add_event_to_queue)
        self._append_into_subscription_list(id, scheduler)

    def _add_event_to_queue(self, event: Event) -> None:
        with self.mutex:
            self.event_queue.append(event)

        with self.read_condition:
            self.read_condition.notify_all()

    def _append_into_subscription_list(self, id: int, scheduler: Scheduler) -> None:
        if self.subscription_ids.get(scheduler) is None:
            self.subscription_ids[scheduler] = []

        self.subscription_ids[scheduler].append(id)

    def _unsubscribe_all(self):
        for scheduler, ids in self.subscription_ids.items():
            for id in ids:
                scheduler.unsubscribe(id)

        self.subscription_ids.clear()


_USE_SUBSCRIBER_KEY = "_subscriber"


def use_subscriber(func):
    @functools.wraps(func)
    def wrapper_use_subscriber(*args, **kwargs):
        with Subscriber() as subscriber:
            kwargs[_USE_SUBSCRIBER_KEY] = subscriber
            return func(*args, **kwargs)

    return wrapper_use_subscriber


def get_subscriber(kwargs: dict) -> Subscriber:
    return kwargs[_USE_SUBSCRIBER_KEY]
