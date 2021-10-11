from PIL import Image
from pystray import Icon, Menu, MenuItem

from scheduler import Scheduler

def start(scheduler: Scheduler):
    def terminate():
        scheduler.publish("flow_control", "terminate", [])
        icon.stop()

    icon_image = Image.open("assets/favicon.ico")

    icon = Icon("Rierogi", icon_image, menu=Menu(
        MenuItem("Waa", lambda _: scheduler.publish("printer", "print", ["Waa"])),
        MenuItem("Bwaa", lambda _: scheduler.publish("printer", "print", ["Bwaa"])),
        MenuItem("Baa", terminate)
    ))

    icon.run()
