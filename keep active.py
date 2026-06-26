"""
keep_active.py
Moves the mouse slightly every 10–15 seconds to prevent Teams (and other
apps) from marking you as Away. Movement is small and randomised so it
looks natural. Press Ctrl+C to stop.

Requirements:
    pip install pyautogui
"""

import time
import random
import pyautogui

# Safety: move the mouse to the top-left corner to abort pyautogui
pyautogui.FAILSAFE = True

# How far (in pixels) to nudge the mouse each tick
NUDGE_MIN = 5
NUDGE_MAX = 20

# Interval range in seconds
INTERVAL_MIN = 10
INTERVAL_MAX = 15


def nudge_mouse():
    """Move the mouse a tiny random amount and then move it back."""
    dx = random.randint(NUDGE_MIN, NUDGE_MAX) * random.choice([-1, 1])
    dy = random.randint(NUDGE_MIN, NUDGE_MAX) * random.choice([-1, 1])

    x, y = pyautogui.position()

    # Clamp so we don't fly off screen
    screen_w, screen_h = pyautogui.size()
    new_x = max(0, min(screen_w - 1, x + dx))
    new_y = max(0, min(screen_h - 1, y + dy))

    pyautogui.moveTo(new_x, new_y, duration=0.3)
    time.sleep(0.2)
    pyautogui.moveTo(x, y, duration=0.3)  # move back to original position


def main():
    print("keep_active.py started.")
    print("Mouse will nudge every 10–15 seconds to keep Teams status active.")
    print("Move mouse to TOP-LEFT corner, or press Ctrl+C, to stop.\n")

    try:
        while True:
            interval = random.uniform(INTERVAL_MIN, INTERVAL_MAX)
            print(f"  Next nudge in {interval:.1f}s ...", end="\r")
            time.sleep(interval)
            nudge_mouse()
            print(f"  Nudged at {time.strftime('%H:%M:%S')}          ")
    except KeyboardInterrupt:
        print("\nStopped by user.")


if __name__ == "__main__":
    main()
