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
        self.sort_image_actions()
        self.loop_fails = 0
        while True:
            self.LoopImages()
            time.sleep(delay)

    def sort_image_actions(self) -> None:
        self.image_paths = sorted(glob.glob(pathname="*.png", root_dir="images"))
        # order the list in actions that are more likely instead of just randomizing everything
        # 1. go button, 2. collect, 3. chance, 4. jail-roll, 5. bank heist, 6. shutdown, 7. X's, 8. 0/
        sorted_image_paths = [path for path in self.image_paths if path.endswith("go.png")]
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("collect.png")])
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("chance.png")])
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("jail-roll.png")])
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("shutdown.png")])
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("bank-heist-door.png")])
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("X.png")])
        sorted_image_paths.extend([path for path in self.image_paths if path.endswith("rolls-done.png")])
        self.sorted_images = sorted_image_paths

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
        current_sorted_images = self.sorted_images
        for path in current_sorted_images:
            if not self.running:
                return
            elif path.endswith(("go.png","collect.png", "chance.png", "X.png")):
                if path.endswith("go.png"):
                    tried_all = {path: self.ProcessImage(path) for path in self.sorted_images if path.endswith("go.png")}
                    if any(tried_all.values()):
                        [self.sorted_images.remove(path) for path in self.sorted_images if path.endswith("go.png") and not tried_all.get(path, False)]
                        self.loop_fails = 0
                        return
                if path.endswith("keepbuildingX.png"):
                    tried_all = [self.ProcessImage(path) for path in self.sorted_images if path.endswith("keepbuildingX.png")]
                    if any(tried_all):
                        [self.ProcessImage(path) for path in self.sorted_images if path.endswith("buildgrayX.png")]
                        self.loop_fails = 0
                        return
                imageProcessed = self.ProcessImage(path)
                if imageProcessed:
                    self.loop_fails = 0
                    return
            elif path.endswith("jail-roll.png"):
                print("trying jails")
                tried_all = {path: self.ProcessImage(path) for path in self.sorted_images if path.endswith("jail-roll.png")}
                if any(tried_all.values()):
                    jail_trues = [path for path, v in tried_all.items() if v]
                    self.ProcessImage(jail_trues[0])
                    self.ProcessImage(jail_trues[0])
                    [self.sorted_images.remove(jail) for jail in current_sorted_images if jail.endswith("jail-roll.png") and not tried_all.get(jail, False)]
                    self.loop_fails = 0
                    return
            elif path.endswith("shutdown.png"):
                print("trying shutdowns")
                [self.ProcessImage(path) for path in self.sorted_images if path.endswith("switch.png")]
                [self.ProcessImage(path) for path in self.sorted_images if path.endswith("gorandom.png")]
                tried_all = {path: self.ProcessImage(path) for path in self.sorted_images if path.endswith("shutdown.png")}
                imageProcessed = any(tried_all.values())
                if imageProcessed:
                    [self.sorted_images.remove(shutdown) for shutdown in current_sorted_images if shutdown.endswith("shutdown.png") and not tried_all.get(shutdown, False)]
                    self.loop_fails = 0
                    return
            elif path.endswith("bank-heist-door.png"):
                print("trying heists")
                tried_all = {path: self.ProcessImage(path) for path in self.sorted_images if path.endswith("bank-heist-door.png")}
                if any(tried_all.values()):
                    heist_trues = [path for path, v in tried_all.items() if v]
                    for _ in repeat(None, 7):
                        [self.ProcessImage(path) for path in heist_trues]
                    [self.sorted_images.remove(heist) for heist in current_sorted_images if heist.endswith("bank-heist-door.png") and not tried_all.get(heist, False)]
                    self.loop_fails = 0
                    return
            elif path.endswith("rolls-done.png"):
                tried_all = {path: self.ProcessImage(path) for path in self.image_paths if path.endswith("rolls-done.png")}
                if any(tried_all.values()):
                    icons = {path: self.ProcessImage(path) for path in self.image_paths if path.endswith("buildicon.png")}
                    if any(icons.values()):
                        builds = [path for path in self.image_paths if path.replace(".png", "").split("build")[0].isdigit() and path.replace(".png", "").split("build")[1].isdigit()]
                        tried_builds = {}
                        while any(tried_all.values()):
                            time.sleep(1)
                            tried_builds = {build: self.ProcessImage(build) for build in builds}
                            for build, build_truth in tried_builds.items():
                                remove_builds = [rm_build for rm_build in self.image_paths if rm_build.endswith(build.split("build")[1]) and not rm_build != build and build_truth]
                                [self.image_paths.remove(rm_build) for rm_build in remove_builds]
                            tried_all = {path: self.ProcessImage(path) for path in self.image_paths if path in builds}
                            builds = [path for path in self.image_paths if path.replace(".png", "").split("build")[0].isdigit() and path.replace(".png", "").split("build")[1].isdigit()]
                        return
            else:
                imageProcessed = any([self.ProcessImage(path) for path in self.sorted_images])
                if imageProcessed:
                    return
                elif self.loop_fails == 3:
                    raise Exception("Loop Failure, add images corresponding to the current Bot's image.")
                elif self.loop_fails == 2:
                    # reset sorted images when loop fails
                    self.loop_fails += 1
                    print(f"No image is matching. loop failures are at {self.loop_fails}, Resetting image selections.")
                    return
                elif self.loop_fails == 1:
                    self.loop_fails += 1
                    print(f"No image is matching. loop failures are at {self.loop_fails}")
                    return



    def LoadImage(self, path: str) -> PIL.Image.Image:
        image = self.cache.get(path)
        if image is None:
            image = self.cache[path] = PIL.Image.open(f"images/{path}")
        return image

    def Find(self, image: PIL.Image.Image, path: str) -> pyscreeze.Point | None:
        try:
            window = gw.getWindowsWithTitle("DashingBee93")[0]
            if not window:
                print(f"{active_window} window not found.")
                return None
            if window.isMinimized:
                window.restore()

            window.activate()

            region = (window.left, window.top, window.width, window.height)

            result = pyautogui.locateOnScreen(image, region=region, grayscale=False, confidence=0.9)
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
    Monopoly(delay=1)
except KeyboardInterrupt:
    sys.exit()
