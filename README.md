# monopoly-go-bot

Automate playing Monopoly Go! using Python and Bluestacks.

https://github.com/lewisgibson/monopoly-go-bot/assets/12851394/d837e9dd-eafd-4872-a1fa-93654c97966c


## **This script requires administrative privileges**

The `start.ps1` script will launch the python script with administrative privileges for you. It needs escalated privileges for these reasons:

1. Bluestacks is a virtual machine where standard mouseclick emulation via `pyautogui` does **not** work. Instead this script uses raw Win32 calls via `pydirectinput`.
2. A global key listener is setup to toggle the script on and off - this is a requirement with a low polling delay because the script takes control of the mouse.

## Instructions

1. Install the Bluestacks Android emulator.
2. Login with Google.
3. Install Monopoly Go! from the app store.
4. Login

    4.1. If coming from iOS, go to settings on the game on your iOS device and connect your account to your Facebook. Use facebook to login on Bluestacks.

5. Ensure normal app functionality works.
6. Clone this repository, or download the zip.
7. Install python and pip.
8. Install the requirements `pip install -r requirements.txt`.
9. Launch `start.ps1` using PowerShell.
10. Use F2 to toggle the script - it starts disabled.
11. Make sure the BlueStacks application is open and visible on a screen at all times.

## Todo

1. Add images to explain installation steps.
2. Keep track of menu navigation state to prevent scanning for close buttons.
3. Use Tesseract to read cash balance and automate build upgrades.
4. Optimise priority list of images to scan.
