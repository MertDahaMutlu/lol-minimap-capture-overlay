import os, time, json
import cv2, numpy as np
from mss import mss
from screeninfo import get_monitors
from pynput import mouse, keyboard
from pynput.mouse import Controller as MouseController, Button as PButton
from pynput.keyboard import Controller as KBController, Key as PKey

CONFIG_PATHS = [
    r"C:\Riot Games\League of Legends\Config\PersistedSettings.json",
    r"D:\Riot Games\League of Legends\Config\PersistedSettings.json"
]

def find_config_file():
    for p in CONFIG_PATHS:
        if os.path.exists(p):
            return p
    return None

def read_minimap_scale():
    p = find_config_file()
    if not p: return 1.0
    try:
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
    except:
        return 1.0
    if isinstance(d, list):
        for it in d:
            if isinstance(it, dict) and it.get("name") == "MinimapScale":
                return float(it.get("value",1.0))
    if isinstance(d, dict):
        settings = d.get("settings", []) if isinstance(d.get("settings"), list) else []
        for it in settings:
            if it.get("name") == "MinimapScale":
                return float(it.get("value",1.0))
        hud = d.get("HUD", {})
        if isinstance(hud, dict) and "MinimapScale" in hud:
            return float(hud["MinimapScale"])
    return 1.0

def pick_monitors():
    mons = get_monitors()
    if len(mons) < 2:
        raise RuntimeError("En az 2 monitör gerekli")
    main = next((m for m in mons if getattr(m,"is_primary", False)), mons[0])
    second = next((m for m in mons if m is not main), mons[1])
    return main, second

def minimap_coords(mon, scale):
    size = int(308 * (mon.height / 1080) * scale * 1.15)
    right = mon.x + mon.width
    bottom = mon.y + mon.height
    left = right - size
    top = bottom - size
    return left, top, right, bottom


def main():
    main_mon, second_mon = pick_monitors()
    minimap_scale = read_minimap_scale()
    x1, y1, x2, y2 = minimap_coords(main_mon, minimap_scale)
    print(f"[INFO] Minimap (global) coords: {x1},{y1} -> {x2},{y2}")

    sct = mss()
    region = {"top": int(main_mon.y), "left": int(main_mon.x),
              "width": int(main_mon.width), "height": int(main_mon.height)}

    win = "MiniMap Overlay"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    try: cv2.moveWindow(win, int(second_mon.x), int(second_mon.y))
    except: pass
    cv2.resizeWindow(win, max(400, second_mon.width//2), max(300, second_mon.height//2))

    mouse_ctrl = MouseController()
    kb_ctrl = KBController()

    flags = {"stop": False, "capture": False, "mouse_pressed": False, "switch": True}

    def on_click(x, y, button, pressed):
        if button == mouse.Button.left:
            flags["mouse_pressed"] = pressed
            inside = (x1 <= x <= x2) and (y1 <= y <= y2)
            flags["capture"] = pressed and flags["switch"] and inside
            if pressed and inside:
                print(f"[DEBUG] Click inside minimap at ({x},{y}) -> capture ON")
            elif pressed and not inside:
                print(f"[DEBUG] Click outside minimap at ({x},{y}) -> capture OFF")

    def on_key(key):
        if key == keyboard.Key.end:
            flags["stop"] = True
            return False
        elif key == keyboard.Key.delete:
            flags["switch"] = not flags["switch"]
            if not flags["switch"]:
                flags["capture"] = False
                try: mouse_ctrl.release(PButton.left)
                except: pass
            print(f"[INFO] Delete pressed -> switch {'ON' if flags['switch'] else 'OFF'}")

    mouse.Listener(on_click=on_click).start()
    keyboard.Listener(on_press=on_key).start()

    first_shot = False
    last_time = 0.0
    shot_interval = 0.12 

    try:
        while not flags["stop"]:
            if flags["capture"] and flags["mouse_pressed"] and flags["switch"]:
                now = time.time()
                if not first_shot or now - last_time > shot_interval:
                    last_time = now
                    first_shot = True
                    img = np.array(sct.grab(region))
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    h = max(200, second_mon.height//2)
                    w = int(img.shape[1] * h / img.shape[0])
                    disp = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
                    cv2.imshow(win, disp)
                    cv2.waitKey(1)
                    try: mouse_ctrl.release(PButton.left)
                    except: pass
                    try:
                        kb_ctrl.press(PKey.space)
                        kb_ctrl.release(PKey.space)
                    except: pass
            else:
                first_shot = False
                cv2.waitKey(1)
            time.sleep(0.005)
    finally:
        try: cv2.destroyAllWindows()
        except: pass
        try: sct.close()
        except: pass
    print("Program sonlandı.")

if __name__ == "__main__":
    main()
   
