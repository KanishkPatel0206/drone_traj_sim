"""
teleop_key.py  –  Keyboard teleoperation for PySimverse
=========================================================
Controls the simulated drone in real-time using keyboard input.
OpenCV is already a pysimverse dependency, so no extra installs needed.

Usage
-----
    python teleop_key.py

Keep the OpenCV window focused while flying; press Q or Esc to quit.

Key Bindings
------------
  Takeoff / Land
    T          – Take off
    L          – Land

  Throttle / Altitude  (up_down)
    W  /  S    – Ascend / Descend

  Rotation / Yaw
    A  /  D    – Rotate left (CCW) / Rotate right (CW)

  Lateral  (left_right)
    ←  /  →    – Slide left / Slide right  (arrow keys)

  Forward / Backward  (forward_backward)
    ↑  /  ↓    – Fly forward / Fly backward (arrow keys)

  Emergency
    Q / Esc    – Land and quit
"""

import sys
import cv2
import numpy as np
import time
from pysimverse import Drone

# ── tunables ─────────────────────────────────────────────────────────────────
SPEED   = 50   # RC channel magnitude  (-100 … 100)
LOOP_HZ = 20   # control loop frequency
# ─────────────────────────────────────────────────────────────────────────────

# Arrow-key raw keycodes differ by OS.
# Do NOT apply & 0xFF – that strips the high bytes arrow keys need.
if sys.platform == "win32":
    KEY_UP    = 2490368
    KEY_DOWN  = 2621440
    KEY_LEFT  = 2424832
    KEY_RIGHT = 2555904
elif sys.platform == "darwin":
    KEY_UP    = 63232
    KEY_DOWN  = 63233
    KEY_LEFT  = 63234
    KEY_RIGHT = 63235
else:  # Linux
    KEY_UP    = 65362
    KEY_DOWN  = 65364
    KEY_LEFT  = 65361
    KEY_RIGHT = 65363

KEY_MAP = {
    ord('w'): "up",
    ord('s'): "down",
    ord('a'): "rot_left",
    ord('d'): "rot_right",
    KEY_UP:    "forward",
    KEY_DOWN:  "backward",
    KEY_LEFT:  "left",
    KEY_RIGHT: "right",
    ord('t'):  "takeoff",
    ord('l'):  "land",
    ord('q'):  "quit",
    27:        "quit",      # Esc
}


def make_hud(flying: bool, lr: int, fb: int, ud: int, rot: int) -> None:
    """Draw a simple status overlay in the OpenCV window."""
    img = np.zeros((260, 420, 3), dtype="uint8")
    col = (0, 220, 80) if flying else (80, 80, 200)
    status = "FLYING" if flying else "GROUNDED"

    def txt(s, y, c=(200, 200, 200)):
        cv2.putText(img, s, (14, y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, c, 1, cv2.LINE_AA)

    txt("PySimverse  Teleop", 28, (255, 255, 255))
    txt(f"Status  : {status}", 58, col)
    txt(f"L/R     : {lr:+4d}", 90)
    txt(f"F/B     : {fb:+4d}", 115)
    txt(f"U/D     : {ud:+4d}", 140)
    txt(f"Rotation: {rot:+4d}", 165)
    txt("T=takeoff  L=land  Q/Esc=quit", 200, (130, 130, 130))
    txt("W/S=alt  A/D=rot  arrows=move", 224, (130, 130, 130))
    cv2.imshow("PySimverse Teleop", img)


def main():
    drone = Drone()
    drone.connect()
    print("[teleop_key] Connected. Press T to take off.")

    flying = False
    interval = 1.0 / LOOP_HZ

    # RC channel values – kept as separate variables
    lr  = 0   # left / right
    fb  = 0   # forward / backward
    ud  = 0   # up / down
    rot = 0   # rotation (yaw)

    try:
        while True:
            t_start = time.time()

            # Reset channels each tick (no key held = hover)
            lr  = 0
            fb  = 0
            ud  = 0
            rot = 0

            make_hud(flying, lr, fb, ud, rot)

            # Read raw keycode – no & 0xFF so arrow keys work correctly
            key    = cv2.waitKey(1)
            action = KEY_MAP.get(key)

            # ── one-shot commands ─────────────────────────────────────────
            if action == "takeoff" and not flying:
                print("[teleop_key] Taking off …")
                drone.take_off()
                flying = True
                time.sleep(1.5)
                continue

            if action == "land" and flying:
                print("[teleop_key] Landing …")
                drone.send_rc_control(0, 0, 0, 0)
                drone.land()
                flying = False
                continue

            if action == "quit":
                print("[teleop_key] Quit requested.")
                break

            # ── continuous RC commands (only while airborne) ──────────────
            if flying:
                if   action == "up":        ud  =  SPEED
                elif action == "down":      ud  = -SPEED
                elif action == "rot_left":  rot = -SPEED
                elif action == "rot_right": rot =  SPEED
                elif action == "forward":   fb  =  SPEED
                elif action == "backward":  fb  = -SPEED
                elif action == "left":      lr  = -SPEED
                elif action == "right":     lr  =  SPEED

                drone.send_rc_control(lr, fb, ud, rot)

            # ── keep loop timing steady ───────────────────────────────────
            elapsed    = time.time() - t_start
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[teleop_key] Interrupted.")

    finally:
        if flying:
            print("[teleop_key] Emergency land.")
            drone.send_rc_control(0, 0, 0, 0)
            drone.land()
        cv2.destroyAllWindows()
        print("[teleop_key] Done.")


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()