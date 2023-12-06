import sys
import time
import pyautogui
import pydirectinput
import glob
import pyscreeze
import PIL.Image
import pynput


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
        for path in sorted(glob.glob(pathname="*.png", root_dir="images")):
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
            result = pyautogui.locateOnScreen(image, grayscale=True, confidence=0.7)
            if result is None:
                return None
            return pyautogui.center(result)
        except pyautogui.ImageNotFoundException:
            print(f"Could not locate {path} with sufficient confidence.")
            return None

    def ProcessImage(self, path: str) -> bool:
        image = self.LoadImage(path)

        point = self.Find(image, path)
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
