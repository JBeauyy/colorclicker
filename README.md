# Color Clicker Bot

![Clicker Bot Interface](https://github.com/HelloByeLetsNot/colorclicker/blob/main/clicker.png?raw=true)

This bot is designed to automatically click on a specified color within a defined area on the screen, streamlining repetitive actions where color-based targeting is essential. With a simple GUI for selecting colors, setting search areas, and adjusting click delay, users can easily configure the bot to suit various tasks.

### Features
- **Color Selection**: Choose a color from the built-in RGB/HSV wheel and sliders, or sample any pixel by hovering and pressing the "Set Color" button.
- **Area Selection**: Drag to create a search area, focusing the bot’s actions on a specific screen region.
- **Auto-Clicking**: Automatically clicks on the first instance of the selected color detected within the area.
- **Loop Delay Adjustment**: Customize the interval between clicks for optimal performance.
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

Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python Linux-main.py
```

On Linux, grant the terminal accessibility/input permissions requested by your desktop environment. On macOS, use the Linux entry point with Accessibility and Screen Recording permissions.

## Use it with a browser game

1. Open the game and keep the game window visible; do not minimize it.
2. Select the target color from the RGB wheel, adjust the Red/Green/Blue sliders if needed, and click **Use Selected Color**. You can alternatively move the pointer over the target and click **Set Color** to sample it.
3. Click **Set Search Area**, then drag a rectangle around the part of the game where that color can appear.
4. Press **Ctrl+Space** or click **Toggle Clicking** until clicking is **ON**.
5. Press **Ctrl+S** to start or stop scanning. Adjust **Loop Delay** if the game needs slower input.

The bot clicks the first matching pixel in the selected area. Use it only with games and services where automation is allowed.
