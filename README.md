# League of Legends Minimap Capture Overlay

This project is a **Python overlay tool** for League of Legends that allows capturing the minimap with mouse clicks and displaying a live overlay on a second monitor. It is optimized for performance and supports dual-monitor setups.

---

## Features

- Automatically detects minimap scale from `PersistedSettings.json`
- Dual monitor support
- Capture and display the main screen by holding the left mouse button on the minimap
- Press `Space` programmatically for quick actions
- Toggle capture on/off with the `Delete` key
- Safely exit the program with the `End` key
- Optimized screen capture using `mss` and OpenCV

---

## Requirements

Python 3.10+ is recommended.

### Required Packages:

```bash
pip install opencv-python numpy mss pynput screeninfo
Note: Windows OS is recommended. A dual-monitor setup is required.
