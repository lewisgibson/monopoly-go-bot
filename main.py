import ctypes
import sys
import os
import time
import pyautogui
import pydirectinput
import glob
import pyscreeze
import PIL.Image
import pynput
import random
import pygetwindow as gw

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

    def __init__(self, delay: float) -> None:
        self.PrintBanner()
        self.SetupKeyHandler()
        while True:
            self.LoopImages()
            time.sleep(delay)

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
        image_paths = sorted(glob.glob(pathname="*.png", root_dir="images"))
        random.shuffle(image_paths)

        for path in image_paths:
            if not self.running:
                return

            imageProcessed = self.ProcessImage(path)
            if imageProcessed:
                time.sleep(0.5)
                continue

    def LoadImage(self, path: str) -> PIL.Image.Image:
        image = self.cache.get(path)
        if image is None:
            image = self.cache[path] = PIL.Image.open(f"images/{path}")
        return image

    def Find(self, image: PIL.Image.Image, path: str) -> pyscreeze.Point | None:
        try:
            window = gw.getWindowsWithTitle(active_window)[0]
            if not window:
                print(f"{active_window} window not found.")
                return None
            if window.isMinimized:
                window.restore()

            window.activate()

            region = (window.left, window.top, window.width, window.height)

            result = pyautogui.locateOnScreen(image, region=region, grayscale=True, confidence=0.8)
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
    Monopoly(delay=0.1)
except KeyboardInterrupt:
    sys.exit()
