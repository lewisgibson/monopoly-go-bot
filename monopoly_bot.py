import ctypes
import sys
import time
import pyautogui
import pydirectinput
import glob
import pyscreeze
import PIL.Image
import pynput
import random
import pygetwindow as gw
from threading import Event
import queue


# For elevated permissions, negating the PowerShell script
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

# Variable to establish the window name. It could be different depending on software and systems.
active_window = "BlueStacks App Player"

class Monopoly:
    def __init__(self, delay: float, stop_event: Event, queue: queue.Queue, active_window: str) -> None:
        self.active_window = active_window
        self.delay = delay
        self.stop_event = stop_event
        self.queue = queue
        self.cache: dict[str, PIL.Image.Image] = {}
        self.running = False
        self.PrintBanner()
        self.SetupKeyHandler()
        self.RunBot()

    def PrintBanner(self) -> None:
        banner = "Monopoly Go! Bot\n\nPress F2 to toggle running.\n"
        self.queue.put(banner)

    def SetupKeyHandler(self) -> None:
        def onKeyPress(key) -> None:
            if key == pynput.keyboard.Key.f2:
                self.running = not self.running
                if self.running:
                    self.queue.put("Started\n")
                else:
                    self.queue.put("Stopped. Press F2 to start again.\n")

        pynput.keyboard.Listener(onKeyPress).start()

    def RunBot(self) -> None:
        while not self.stop_event.is_set():
            if self.running:
                self.LoopImages()
            time.sleep(self.delay)

    def LoopImages(self) -> None:
        image_paths = sorted(glob.glob(pathname="*.png", root_dir="images"))
        random.shuffle(image_paths)

        for path in image_paths:
            if not self.running or self.stop_event.is_set():
                return
            
            imageProcessed = self.ProcessImage(path)
        
            if path.endswith("1keepbuildingX.png"):
                self.ProcessImage(path.replace("1keepbuildingX.png", "1buildgrayX.png"))
                time.sleep(0.5)
                continue
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
                self.queue.put(f"{active_window} window not found.\n")
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

        self.queue.put(f"Located matching image for {path} -> ({point.x}, {point.y})\n")
        pyautogui.moveTo(x=point.x, y=point.y, duration=0.2)
        pydirectinput.click()
        return True

if __name__ == "__main__":
    try:
        stop_event = Event()
        message_queue = queue.Queue()
        Monopoly(delay=0.1, stop_event=stop_event, queue=message_queue)
    except KeyboardInterrupt:
        sys.exit()
