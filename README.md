# Color Clicker Bot

![Clicker Bot Interface](https://github.com/HelloByeLetsNot/colorclicker/blob/main/clicker.png?raw=true)

This bot is designed to automatically click on a specified color within a defined area on the screen, streamlining repetitive actions where color-based targeting is essential. With a simple GUI for selecting colors, setting search areas, and adjusting click delay, users can easily configure the bot to suit various tasks.

### Features
- **Color Selection**: Choose a color from the built-in RGB/HSV wheel and sliders, enter an exact color code, or use the screen dropper to sample a browser pixel.
- **Area Selection**: Drag to create a search area, focusing the bot’s actions on a specific screen region.
- **Auto-Clicking**: Automatically clicks on the first instance of the selected color detected within the area.
- **Loop Delay and Color Tolerance**: Customize the interval between clicks and how closely screen pixels must match the selected color.
- **Hotkey Controls**: Start/stop the bot with `Ctrl+S`, toggle clicking with `Ctrl+Space`, and select color with `F`.

Built with PyAutoGUI, OpenCV, and Tkinter, this program is ideal for automating interactions in environments where specific color elements require consistent attention.

## Run it

Install Python 3.10 or newer, then install the dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python Win-main.py
```

To install it as a desktop application on Windows, right-click `setup-windows.ps1`, choose **Run with PowerShell**, and approve the execution if prompted. The script creates the virtual environment, installs dependencies, and adds a **Color Clicker** shortcut to your Desktop. Double-click that shortcut to launch the GUI without a console window. If PowerShell blocks the script, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup-windows.ps1
```

Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python Linux-main.py
```

On Linux, grant the terminal accessibility/input permissions requested by your desktop environment. On macOS, use the Linux entry point with Accessibility and Screen Recording permissions.

## Use it with a browser game

1. Open the game and keep the game window visible; do not minimize it.
2. Choose a color from the RGB wheel or enter an exact `#RRGGBB` / `R, G, B` code and click **Apply Code**. To sample the browser directly, click **Pick Color From Screen** (or press `F`), switch to the browser with `Alt+Tab`, then click the exact pixel. The sampling click is intercepted so it won't activate the game element.
3. Click **Set Search Area**, then drag a rectangle around the part of the game where that color can appear.
4. Draw the search area tightly around the button or buttons, sampling their solid background rather than the text. Click **Start Scanning** in the app; the cursor moves to and clicks the nearest matching color region. The app reports whether it found a match. Press **Ctrl+Space** to pause or resume clicking, and **Ctrl+S** (or **Stop Scanning**) to stop. Adjust **Color Tolerance** if button shading or anti-aliasing prevents a match, and adjust **Loop Delay** to control click speed.

The bot clicks the first matching pixel in the selected area. Use it only with games and services where automation is allowed.
