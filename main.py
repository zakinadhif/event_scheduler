from threading import Thread

import logging
import time

import scheduler
import printer
import systray

from scheduler_task import scheduler_task

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    main_scheduler = scheduler.Scheduler()

    scheduler_thread = Thread(
        target=scheduler_task,
        name="SchedulerThread",
        args=[main_scheduler]
    )

    printer_thread = Thread(
        target=printer.printer_task,
        name="PrinterThread",
        args=[main_scheduler]
    )

    logging.info("Main: starting threads")

    scheduler_thread.start()
    printer_thread.start()

    systray.start(main_scheduler)
    main_scheduler.publish("printer", "print", ["Bwaa"])
    main_scheduler.publish("printer", "print", ["Waa"])
    time.sleep(2)
    main_scheduler.publish("flow_control", "terminate", [])

    logging.info("Main: wait for the thread to finish")

    printer_thread.join()

    main_scheduler.publish("flow_control", "terminate_scheduler", [])
    scheduler_thread.join()
