import os
import sys
from threading import Thread
from time import sleep
import json
import logging

LOG_FORMAT = "%(filename)s - %(lineno)d - %(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(filename="log.log", level=logging.DEBUG, format=LOG_FORMAT, filemode="a+")


from pynput.keyboard import (
    Key,
    KeyCode,
)

from zyXKey import xyZkey

from seleniumOverlay import SeleniumOverlay

from tasktray import taskbarIconThread


from pynput.mouse import Controller as mouseController, Button as mouseButtons

############################################################################


def WINDOWS_TURN_OFF_SCREEN():
    import win32gui

    win32gui.SendMessageTimeout(65535, 274, 0xF170, 2, 8, 1000)


OVERLAY_ENABLED = True


def main():

    XyZkey = xyZkey()

    XyZkey.consolelog = lambda *x: ping_selenium(*x)

    XyZkey.xKeyAdd("f13", Key.f13)
    XyZkey.xKeyAdd("pause", Key.pause)

    Mouse = mouseController()

    VOL_UP = KeyCode.from_vk(0xAF)
    VOL_DOWN = KeyCode.from_vk(0xAE)
    PREV_MEDIA = KeyCode.from_vk(0xB1)
    NEXT_MEDIA = KeyCode.from_vk(0xB0)
    PAUSE_MEDIA = KeyCode.from_vk(0xB3)
    SCREENSHOT = KeyCode.from_vk(0x2C)

    # Back
    @XyZkey.bind("gesture", modifier_key=Key.f13, cooldown=0.2, direction="left")
    def _():
        Mouse.click(mouseButtons.x1)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "back"})

    # Forward
    @XyZkey.bind("gesture", modifier_key=Key.f13, cooldown=0.2, direction="right")
    def _():
        Mouse.click(mouseButtons.x2)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "forward"})

    # Volume up
    @XyZkey.bind("gesture", modifier_key=Key.f13, direction="up")
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=Key.page_up)
    def _():
        for i in range(3):
            XyZkey.keyboardPress(VOL_UP)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "volume up"})

    # Volume down
    @XyZkey.bind("gesture", modifier_key=Key.f13, direction="down")
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=Key.page_down)
    def _():
        for i in range(3):
            XyZkey.keyboardPress(VOL_DOWN)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "volume down"})

    # Previous media
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=KeyCode.from_char(","))
    def _():
        XyZkey.keyboardPress(PREV_MEDIA)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "previous"})

    # Play/f13 media
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=KeyCode.from_char("/"))
    def _():
        XyZkey.keyboardPress(PAUSE_MEDIA)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "f13/play"})

    # Next media
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=KeyCode.from_char("."))
    def _():
        XyZkey.keyboardPress(NEXT_MEDIA)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "previous"})

    # Sleep
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=KeyCode.from_char("\\"))
    def _():
        WINDOWS_TURN_OFF_SCREEN()
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "sleep"})

    # Screenshot
    @XyZkey.bind("modifier", modifier_key=Key.pause, key=Key.ctrl_r)
    def _():
        XyZkey.keyboardPress(SCREENSHOT)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onExec", {"bind": "screenshot"})

    ################################## DEBUG ##################################

    def ping_selenium(*x):
        print(*x)
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute(
            "ping", json.dumps({*x}, default=lambda x: list(x) if isinstance(x, set) else x)
        )

    @XyZkey.bind("modifier", modifier_key=Key.f13, key=KeyCode.from_char("r"))
    def _():
        OVERLAY_ENABLED and OVERLAY.refresh()
        pass

    @XyZkey.bind("modifier", modifier_key=Key.f13, key=KeyCode.from_char("="))
    def _():
        OVERLAY_ENABLED and OVERLAY.JsExecute("window.electron.send('openDevTools')")
        pass

    ############################################################################

    ############################################################################

    @XyZkey.bind("onTick")
    def _(data):
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onTick", data)
        pass

    @XyZkey.bind("onModifierRelease")
    def _():
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onModifierRelease")
        pass

    @XyZkey.bind("onModifierPress")
    def _():
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onModifierPress")
        pass

    @XyZkey.bind("doubleTap", key=KeyCode.from_char("v"))
    def _():
        OVERLAY_ENABLED and OVERLAY.seleniumJsExecute("onModifierPress")
        pass

    ############################################################################

    @XyZkey.bind("modifier", modifier_key=Key.pause, key=Key.esc)
    def KILL_APP():
        nonlocal RUNNING
        print("KILLING")
        RUNNING = False

    ############################################################################

    XyZkey.start()

    if OVERLAY_ENABLED:
        OVERLAY = SeleniumOverlay()
        OVERLAY.go("https://xyzKey.wumbl3.xyz/xyzKey/v3/body.html")

    TASKBAR_ICO = taskbarIconThread(exit_func=KILL_APP)

    print("APP READY...")
    RUNNING = True

    while RUNNING:
        sleep(1)

    XyZkey.__kill__()
    XyZkey.join()
    OVERLAY_ENABLED and OVERLAY.__kill__()
    TASKBAR_ICO.__kill__()
    TASKBAR_ICO.join()
    sys.exit(0)

    ############################################################################


try:
    main()
except Exception as e:
    print("Exception", e)
    logging.exception(e)
