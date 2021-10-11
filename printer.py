from subscriber import Subscriber
from scheduler import Scheduler
import time

def printer_task(scheduler: Scheduler):
    task_subscriber = Subscriber()

    task_subscriber.subscribe_into("printer", scheduler)
    task_subscriber.subscribe_into("flow_control", scheduler)

    while True:
        task = task_subscriber.poll_event()

        if task is None:
            time.sleep(0.2)
            continue

        if task.name == "print":
            print("Printer:", task.arguments[0])

        if task.name == "terminate":
            break

    del task_subscriber
