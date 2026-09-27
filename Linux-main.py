import pyautogui
import cv2
import numpy as np
import time
import threading
from pynput import keyboard, mouse
import tkinter as tk

# Global variables
selected_color = None
running = False
clicking = False
pressed_keys = set()
lock = threading.Lock()
loop_delay = 0.1  # Default loop delay
area = None
start_x, start_y = None, None

def get_color_from_keypress():
    global selected_color
    status_label.config(text="Waiting for Color Selection... Hover and press 'Set Color' button.")
    
    # Wait for user to hover and press the button
    x, y = pyautogui.position()
    selected_color = pyautogui.screenshot().getpixel((x, y))
    color_label.config(text=f"Selected Color: {selected_color}")
    status_label.config(text="Color Selected! Set Search Area.")
    
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
root.title("Clicking Bot Configuration")

status_label = tk.Label(root, text="Press 'Set Color' and hover over your desired color.")
status_label.pack(pady=5)

color_button = tk.Button(root, text="Set Color", command=select_color)
color_button.pack(pady=5)

color_label = tk.Label(root, text="Selected Color: None")
color_label.pack(pady=5)

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
