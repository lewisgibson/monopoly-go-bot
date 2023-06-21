import sys
import time
import pyautogui
import pydirectinput
import glob
import pyscreeze
import PIL.Image
import pynput

running = False


def on_press(key):
    global running
    if key == pynput.keyboard.Key.f2:
        running = not running
        if running:
            print("Started")
        else:
            print("Stopped")


listener = pynput.keyboard.Listener(on_press=on_press)
listener.start()


class Monopoly:
    cache: dict[str, PIL.Image.Image] = {}

    def __init__(self, delay: float) -> None:
        while True:
            self.LoopImages()
            time.sleep(delay)

    def LoopImages(self) -> None:
        global running
        if not running:
            return

        for path in sorted(glob.glob(pathname="*.png", root_dir="images")):
            if not running:
                return

            if self.ProcessImage(path):
                break

    def LoadImage(self, path: str) -> PIL.Image.Image:
        image = self.cache.get(path)
        if image is None:
            image = self.cache[path] = PIL.Image.open(f"images/{path}")
        return image

    def Find(self, image: PIL.Image.Image) -> pyscreeze.Point | None:
        result = pyautogui.locateOnScreen(image, grayscale=True, confidence=0.75)
        if result is None:
            return None
        return pyautogui.center(result)

    def ProcessImage(self, path: str) -> bool:
        image = self.LoadImage(path)

        point = self.Find(image)
        if point is None:
            print(f"Scanning for {path}")
            return False

        print(f"Scanning for {path} -> ({point.x}, {point.y})")
        pyautogui.moveTo(x=point.x, y=point.y, duration=0.2)
        pydirectinput.click()
        return True


try:
    Monopoly(delay=0.1)
except KeyboardInterrupt:
    sys.exit()
