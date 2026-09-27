import pyautogui
import cv2
import numpy as np
import time
import threading
import colorsys
import re
from pynput import keyboard, mouse
import tkinter as tk
from PIL import Image, ImageTk

# Global variables
selected_color = None
running = False
clicking = False
pressed_keys = set()
lock = threading.Lock()
loop_delay = 0.1  # Default loop delay
area = None
start_x, start_y = None, None
wheel_image = None
dropper_listener = None


def create_color_wheel(size=220):
    """Create a hue/saturation wheel image for the color picker."""
    image = Image.new("RGB", (size, size), "white")
    center = size / 2
    radius = center - 2
    for y in range(size):
        for x in range(size):
            dx, dy = x - center, y - center
            distance = (dx * dx + dy * dy) ** 0.5
            if distance <= radius:
                saturation = distance / radius
                hue = (np.arctan2(-dy, dx) / (2 * np.pi)) % 1
                image.putpixel((x, y), tuple(round(value * 255) for value in colorsys.hsv_to_rgb(hue, saturation, 1)))
    return image


def update_color_from_rgb(_=None):
    rgb = (red_scale.get(), green_scale.get(), blue_scale.get())
    rgb_label.config(text=f"RGB: {rgb}")
    color_preview.config(bg="#%02x%02x%02x" % rgb)
    color_code_var.set("#%02X%02X%02X" % rgb)


def parse_color_code(value):
    value = value.strip()
    if re.fullmatch(r"#?[0-9a-fA-F]{6}", value):
        value = value.removeprefix("#")
        return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))

    channels = value.split(",")
    if len(channels) == 3:
        try:
            rgb = tuple(int(channel.strip()) for channel in channels)
        except ValueError:
            pass
        else:
            if all(0 <= channel <= 255 for channel in rgb):
                return rgb

    raise ValueError("Enter #RRGGBB or three RGB values from 0 to 255.")


def apply_color_code():
    try:
        rgb = parse_color_code(color_code_var.get())
    except ValueError as error:
        status_label.config(text=str(error))
        return

    red_scale.set(rgb[0])
    green_scale.set(rgb[1])
    blue_scale.set(rgb[2])
    use_picker_color()


def use_picker_color():
    global selected_color
    selected_color = (red_scale.get(), green_scale.get(), blue_scale.get())
    color_label.config(text=f"Selected Color: {selected_color}")
    status_label.config(text="Color selected from picker. Set Search Area.")


def choose_wheel_color(event):
    center = 110
    dx, dy = event.x - center, event.y - center
    radius = (dx * dx + dy * dy) ** 0.5
    if radius > center:
        return
    saturation = min(radius / center, 1)
    hue = (np.arctan2(-dy, dx) / (2 * np.pi)) % 1
    rgb = tuple(round(value * 255) for value in colorsys.hsv_to_rgb(hue, saturation, 1))
    red_scale.set(rgb[0])
    green_scale.set(rgb[1])
    blue_scale.set(rgb[2])
    update_color_from_rgb()

def get_color_from_keypress():
    """Arm a one-shot global click to sample a screen pixel."""
    global dropper_listener
    if dropper_listener is not None and dropper_listener.is_alive():
        root.after(0, lambda: status_label.config(text="Screen color picker is already armed."))
        return

    root.after(0, lambda: status_label.config(text="Switch to the browser and click the exact pixel to sample."))

    def on_click(x, y, button, pressed):
        global selected_color
        if not pressed or button != mouse.Button.left:
            return

        try:
            sampled_color = pyautogui.screenshot().getpixel((x, y))
        except (IndexError, OSError, pyautogui.PyAutoGUIException) as error:
            root.after(0, lambda message=str(error): status_label.config(text=f"Color sampling failed: {message}"))
            return False

        def apply_sample():
            global selected_color
            selected_color = sampled_color
            red_scale.set(sampled_color[0])
            green_scale.set(sampled_color[1])
            blue_scale.set(sampled_color[2])
            color_label.config(text=f"Selected Color: {selected_color}")
            status_label.config(text="Screen color selected. Set Search Area.")

        root.after(0, apply_sample)
        return False

    dropper_listener = mouse.Listener(on_click=on_click, suppress=True)
    dropper_listener.start()
    
def drag_area_selection():
    """Display a visual selection square and capture the selected area."""
    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.3)  # Transparent window
    overlay.attributes("-topmost", True)
    overlay.configure(bg='gray')
    
    selection_rect = tk.Label(overlay, bg="blue", highlightthickness=1)
    selection_rect.place(x=0, y=0, width=0, height=0)
    
    def on_click(x, y, button, pressed):
        global start_x, start_y, area
        
        if pressed:
            start_x, start_y = x, y
        else:
            end_x, end_y = x, y
            # Define area as a rectangle between start and end points
            area = (min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x), abs(end_y - start_y))
            area_label.config(text=f"Search Area: {area}")
            overlay.destroy()
            status_label.config(text="Area Selected! Press 'Ctrl+S' to start or stop.")
            return False  # Stop listener

    def on_move(x, y):
        """Update the rectangle dimensions during mouse drag."""
        if start_x is not None and start_y is not None:
            width, height = abs(x - start_x), abs(y - start_y)
            x0, y0 = min(start_x, x), min(start_y, y)
            selection_rect.place(x=x0, y=y0, width=width, height=height)
    
    listener = mouse.Listener(on_click=on_click, on_move=on_move)
    listener.start()

    threading.Thread(target=listener.join).start()

def click_color_in_area(area):
    global selected_color, running, clicking, loop_delay
    status_label.config(text="Clicking Started!")
    while running:
        if area is None:
            status_label.config(text="Set a search area before starting.")
            break

        if clicking and selected_color:
            screenshot = pyautogui.screenshot(region=area)
            screenshot_np = np.array(screenshot)

            target_color = np.array(selected_color, dtype=np.int16)
            lower_bound = np.clip(target_color - 20, 0, 255).astype(np.uint8)
            upper_bound = np.clip(target_color + 20, 0, 255).astype(np.uint8)
            mask = cv2.inRange(screenshot_np, lower_bound, upper_bound)
            coords = np.column_stack(np.where(mask > 0))

            if len(coords) > 0:
                y, x = coords[0]
                click_x = area[0] + x
                click_y = area[1] + y
                pyautogui.click(click_x, click_y)
                print(f"Clicked on color at: ({click_x}, {click_y})")

        time.sleep(loop_delay)

    running = False
    status_label.config(text="Script Stopped. Press 'Ctrl+S' to start.")


def toggle_running():
    global running

    if not running and (selected_color is None or area is None or area[2] <= 0 or area[3] <= 0):
        status_label.config(text="Set a color and a non-empty search area first.")
        return

    if not selected_color:
        status_label.config(text="Select a color before starting the bot.")
        return

    if area is None:
        status_label.config(text="Select a search area before starting the bot.")
        return

    if running:
        running = False
        status_label.config(text="Script Stopped. Press 'Ctrl+S' to start.")
        return

    running = True
    status_label.config(text="Script Running. Press 'Ctrl+S' to stop.")
    threading.Thread(target=click_color_in_area, args=(area,), daemon=True).start()
    
def toggle_clicking():
    global clicking
    clicking = not clicking
    toggle_label.config(text=f"Clicking: {'ON' if clicking else 'OFF'}")

def update_loop_delay(val):
    global loop_delay
    loop_delay = float(val)
    delay_label.config(text=f"Loop Delay: {loop_delay:.2f}s")

def select_color():
    threading.Thread(target=get_color_from_keypress).start()

def set_search_area():
    drag_area_selection()

# Set up GUI
root = tk.Tk()
root.title("Color Clicker")

status_label = tk.Label(root, text="Choose a color code, use the wheel, or pick a pixel from the screen.")
status_label.pack(pady=5)

color_button = tk.Button(root, text="Pick Color From Screen (F)", command=select_color)
color_button.pack(pady=5)

color_label = tk.Label(root, text="Selected Color: None")
color_label.pack(pady=5)

picker_frame = tk.LabelFrame(root, text="Choose RGB Color", padx=8, pady=8)
picker_frame.pack(pady=5)

wheel_image = ImageTk.PhotoImage(create_color_wheel())
wheel_canvas = tk.Canvas(picker_frame, width=220, height=220, highlightthickness=0)
wheel_canvas.create_image(0, 0, image=wheel_image, anchor="nw")
wheel_canvas.bind("<Button-1>", choose_wheel_color)
wheel_canvas.grid(row=0, column=0, rowspan=4, padx=(0, 10))

red_scale = tk.Scale(picker_frame, from_=255, to=0, orient="horizontal", label="Red", command=update_color_from_rgb)
green_scale = tk.Scale(picker_frame, from_=255, to=0, orient="horizontal", label="Green", command=update_color_from_rgb)
blue_scale = tk.Scale(picker_frame, from_=255, to=0, orient="horizontal", label="Blue", command=update_color_from_rgb)
for row, scale in enumerate((red_scale, green_scale, blue_scale)):
    scale.grid(row=row, column=1, sticky="ew")
rgb_label = tk.Label(picker_frame, text="RGB: (255, 0, 0)")
rgb_label.grid(row=3, column=1)
color_preview = tk.Label(picker_frame, text="      ", bg="#ff0000", relief="sunken")
color_preview.grid(row=4, column=1, pady=4)
color_code_var = tk.StringVar(value="#FF0000")
red_scale.set(255)
tk.Label(picker_frame, text="Color code (#RRGGBB or R, G, B)").grid(row=6, column=0, sticky="w")
color_code_entry = tk.Entry(picker_frame, textvariable=color_code_var, width=18)
color_code_entry.grid(row=6, column=1, sticky="ew")
apply_code_button = tk.Button(picker_frame, text="Apply Code", command=apply_color_code)
apply_code_button.grid(row=7, column=0, columnspan=2, pady=(4, 0))
picker_button = tk.Button(picker_frame, text="Use Selected Color", command=use_picker_color)
picker_button.grid(row=8, column=0, columnspan=2, pady=(4, 0))

area_button = tk.Button(root, text="Set Search Area", command=set_search_area)
area_button.pack(pady=5)

area_label = tk.Label(root, text="Search Area: Not set")
area_label.pack(pady=5)

toggle_button = tk.Button(root, text="Toggle Clicking (Ctrl + Space)", command=toggle_clicking)
toggle_button.pack(pady=5)

toggle_label = tk.Label(root, text="Clicking: OFF")
toggle_label.pack(pady=5)

delay_scale = tk.Scale(root, from_=0.05, to=1.0, resolution=0.05, orient="horizontal", label="Loop Delay (seconds)", command=update_loop_delay)
delay_scale.set(loop_delay)
delay_scale.pack(pady=5)

delay_label = tk.Label(root, text=f"Loop Delay: {loop_delay:.2f}s")
delay_label.pack(pady=5)

# Keyboard listener setup
def on_press(key):
    with lock:
        if key in pressed_keys:
            return

        pressed_keys.add(key)
        try:
            char = key.char.lower()
        except AttributeError:
            char = None

        ctrl_pressed = keyboard.Key.ctrl_l in pressed_keys or keyboard.Key.ctrl_r in pressed_keys
        if char == 'f':
            select_color()
        elif char == 's' and ctrl_pressed:
            toggle_running()
        elif key == keyboard.Key.space and ctrl_pressed:
            toggle_clicking()

def on_release(key):
    with lock:
        try:
            pressed_keys.remove(key)
        except KeyError:
            pass

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

root.mainloop()
