import ctypes
import sys
import time
import pyautogui
import pydirectinput
import glob
import pyscreeze
import PIL.Image
import pynput
import pygetwindow as gw
from itertools import repeat
import json
from typing import Dict

#For elevated permssions, negating the powershell script
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

#Variable to establish the window name. It could be different depending on software and systems.
active_window = "BlueStacks App Player"


class Monopoly:
    running = False
    cache: dict[str, PIL.Image.Image] = {}

    def __init__(self, delay: float, bot_name: str) -> None:
        self.PrintBanner()
        self.SetupKeyHandler()
        self.loop_fails = 0
        self.bot_name = bot_name
        self.StartBot()
        self.exit = False
        while True:
            self.LoopImages()
            time.sleep(delay)


    def StartBot(self) -> None:
        try:
            image = self.LoadImage(f'{self.bot_name}.png')
            window = gw.getWindowsWithTitle("BlueStacks Multi Instance Manager")[0]
            if not window:
                print(f"{active_window} window not found.")
                raise Exception("Can't find multi-instance manager window")
            if window.isMinimized:
                window.restore()

            window.resizeTo(920, 920)
            window.activate()

            region = (window.left, window.top, window.width, window.height)

            result = pyautogui.locateOnScreen(image, region=region, grayscale=False, confidence=0.9)
            if result is None:
                raise Exception("Bot doesn't exist!")

            result = pyautogui.center(result)
            # move to 75 instead of in the middle of matching bot to click start
            pyautogui.moveTo(x=(int((result.x*2)/4)*2.5), y=result.y, duration=0.2)
            pydirectinput.click()
            time.sleep(10)
            while not self.ProcessImage("monopoly-app.png"):
                self.ProcessImage("monopoly-app.png")
            time.sleep(10)
        except pyautogui.ImageNotFoundException:
            raise


    def PrintBanner(self) -> None:
        print("Monopoly Go! Bot")
        print()
        print("Press F2 to toggle running.")
        print()

    def SetupKeyHandler(self) -> None:
        def onKeyPress(key) -> None:
            if key == pynput.keyboard.Key.f2:
                self.running = not self.running
                if self.running:
                    print("Started")
                    print()
                else:
                    print("Stopped. Press F2 to start again.")
                    print()

        pynput.keyboard.Listener(onKeyPress).start()

    def LoopImages(self) -> None:
        loop_actions = ["go", "collect", "shutdown", "bank-heist", "jail-roll", "start-upX", "otherX"]
        if not self.running:
            return
        for loop_action in loop_actions:
            image_processed = self.ProcessImage(f"{loop_action}.png")
            if image_processed:
                return
        if self.ProcessImage("keep-rolling.png"):
            self.ProcessImage("buildX.png")
            while self.ProcessImage("otherX.png"):
                self.ProcessImage("otherX.png")
            self.ProcessImage("build.png")
            continue_building = True
            while continue_building:
                continue_building = any([self.ProcessImage(f'build{num}.png') for num in range(1,6)])
            return
        if self.ProcessImage("keep-building.png"):
            self.ProcessImage("buildX.png")
            self.ProcessImage("close-phone.png")
            self.ProcessImage("really-close-phone.png")
            self.exit = True
            return
        return

    def LoadImage(self, path: str) -> PIL.Image.Image:
        image = self.cache.get(path)
        if image is None:
            image = self.cache[path] = PIL.Image.open(f"images/{path}")
        return image

    def Find(self, image: PIL.Image.Image, path: str) -> pyscreeze.Point | None:
        try:
            window = gw.getWindowsWithTitle(self.bot_name)[0]
            if not window:
                print(f"{active_window} window not found.")
                return None
            if window.isMinimized:
                window.restore()

            window.resizeTo(540, 960)
            window.activate()

            region = (window.left, window.top, window.width, window.height)

            result = pyautogui.locateOnScreen(image, region=region, grayscale=False, confidence=0.8)
            if result is None:
                return None

            return pyautogui.center(result)
        except pyautogui.ImageNotFoundException:
            return None

    def ProcessImage(self, path: str) -> bool:
        image = self.LoadImage(path)

        point = self.Find(image, path)
        if point is None:
            return False

        print(f"Located matching image for {path} -> ({point.x}, {point.y})")
        
        pyautogui.moveTo(x=point.x, y=point.y, duration=0.2)
        pydirectinput.click()
        return True

try:
    with open("bots.json") as bots:
        bots = json.loads(bots.read())
    for bot in bots:
        monops_bot = Monopoly(delay=1, bot_name=bot)
        while not monops_bot.exit:
            pass
        del monops_bot
except KeyboardInterrupt:
    sys.exit()
