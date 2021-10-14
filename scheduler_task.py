import logging
from scheduler import Scheduler
from subscriber import get_subscriber, use_subscriber

import time

@use_subscriber
def scheduler_task(scheduler: Scheduler, **kwargs):
    task_subscriber = get_subscriber(kwargs)

    task_subscriber.subscribe_into("flow_control", scheduler)

    while True:
        if scheduler._event_queue:
            scheduler.distribute_events()

        task = task_subscriber.poll_event()

        if task is not None and task.name == "terminate_scheduler":
            logging.debug(f"SchedulerTask: Got a terminate scheduler event. Terminating.")
            break;

        time.sleep(0.2)
