from typing import Optional
from scheduler import Scheduler, Event

from threading import Lock

class Subscriber:
    def __init__(self):
        self.event_queue = []
        self.subscription_ids = {}
        self.mutex = Lock()

    def poll_event(self) -> Optional[Event]:
        with self.mutex:
            if self.event_queue:
                return self.event_queue.pop()
        return None

    def add_event_to_queue(self, event: Event) -> None:
        with self.mutex:
            self.event_queue.append(event)

    def subscribe_into(self, group: str, scheduler: Scheduler) -> None:
        id = scheduler.subscribe(group, self.add_event_to_queue)
        self._append_into_subscription_list(id, scheduler)

    def _append_into_subscription_list(self, id: int, scheduler: Scheduler) -> None:
        if self.subscription_ids.get(scheduler) is None:
            self.subscription_ids[scheduler] = []

        self.subscription_ids[scheduler].append(id)

    def _unsubscribe_all(self):
        for scheduler, ids in self.subscription_ids:
            for id in ids:
                scheduler.unsubscribe(id)

    def __del__(self):
        print("Destructed.")
        if not self.subscription_ids:
            return

        self._unsubscribe_all()
