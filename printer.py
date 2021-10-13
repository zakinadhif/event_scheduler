from subscriber import Subscriber, use_subscriber, get_subscriber
from scheduler import Scheduler
import time

@use_subscriber
def printer_task(scheduler: Scheduler, **kwargs):
    task_subscriber = get_subscriber(kwargs)

    task_subscriber.set_default_scheduler(scheduler)
    task_subscriber.subscribe_into("printer")
    task_subscriber.subscribe_into("flow_control")

    while True:
        task = task_subscriber.poll_event()

        if task is None:
            time.sleep(0.2)
            continue

        if task.name == "print":
            print("Printer:", task.arguments[0])

        if task.name == "terminate":
            break
