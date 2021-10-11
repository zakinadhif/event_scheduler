from scheduler import Scheduler
from subscriber import Subscriber

import time

def scheduler_task(scheduler: Scheduler):
    task_subscriber = Subscriber()

    task_subscriber.subscribe_into("flow_control", scheduler)

    while True:
        scheduler.distribute_events()

        task = task_subscriber.poll_event()

        if task is not None and task.name == "terminate_scheduler":
            break;

        time.sleep(0.2)
