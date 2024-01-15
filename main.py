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

            window.resizeTo(1280, 720)
            window.activate()

            region = (window.left, window.top, window.width, window.height)

            try:
                result = pyautogui.locateOnScreen(image, region=region, grayscale=False, confidence=0.9)
            except pyautogui.ImageNotFoundException:
                check_for_start = self.LoadImage(f'{self.bot_name}_started.png')
                try:
                    result = pyautogui.locateOnScreen(check_for_start, region=region, grayscale=False, confidence=0.9)
                except:
                    raise

            result = pyautogui.center(result)
            # move to 75 instead of in the middle of matching bot to click start
            pyautogui.moveTo(x=(int((result.x*2)/4)*2.5), y=result.y, duration=0.2)
            pydirectinput.click()
            time.sleep(10)
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
        loop_actions = ["go", "collect", "switch-opponent", "click-random", "bank-heist", 
                        "jail-roll", "spin", "cash-grab" ,"start-upX", "otherX", "keep-rolling", 
                        "other-otherX", "transparentX", "graydot", "monopoly-app", "monopoly-app2"]
        if not self.running:
            return
        for loop_action in loop_actions:
            image_processed = self.ProcessImage(f"{loop_action}.png")
            if image_processed and loop_action == "click-random":
                for _ in repeat(None, 5):
                    time.sleep(0.3)
                    image_processed = self.ProcessImage("shutdown.png")
            if image_processed and loop_action == "bank-heist":
                for _ in repeat(None, 10):
                    time.sleep(0.3)
                    self.ProcessImage("bank-heist.png")
                return
            if image_processed and loop_action == "graydot.png":
                while not self.ProcessImage("keep-building"):
                    self.ProcessImage("graydot.png")
            if self.ProcessImage("keep-rolling.png"):
                self.ProcessImage("keep-rollingX.png")
                self.ProcessImage("otherX.png")
                self.ProcessImage("other-otherX.png")
                self.ProcessImage("transparentX.png")
                self.ProcessImage("inviteX.png")
                self.ProcessImage("build.png")
                return
            if self.ProcessImage("keep-building.png"):
                self.ProcessImage("buildX.png")
                self.ProcessImage("close-phone.png")
                self.ProcessImage("really-close-phone.png")
                self.exit = True
                return
            if image_processed:
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

            result = pyautogui.locateOnScreen(image, region=region, grayscale=False, confidence=0.75)
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

if __name__ == "__main__":
    try:
        bots = []
        with open("bots.json") as bots_file:
            bots = json.loads(bots_file.read())
        for bot in bots:
            monops_bot = Monopoly(delay=0.8, bot_name=bot)
            while not monops_bot.exit:
                pass
            del monops_bot
    except KeyboardInterrupt:
        sys.exit()
