# HWID Info Checker
**By BigH**

A Windows desktop tool that collects and displays hardware identifiers from your machine — disk serials, MAC address, motherboard info, CPU ID, and volume IDs — in a clean, modern GUI.

---

## Features

- **Disk Serial Numbers** — reads all physical drives via WMI
- **MAC Address** — fetches the first physical adapter address
- **Motherboard** — manufacturer, product name, and serial number
- **CPU ID** — unique processor identifier
- **Volume IDs** — serial numbers for all logical drives
- **Copy buttons** on every field for quick clipboard access
- **Copy All** — exports all info in one clean formatted block
- **Error Log panel** — shows any fetch errors in-app, with Copy and Clear buttons
- **Refresh** — re-fetches all data without restarting
- Background loading — UI stays responsive while data is collected

---

## Requirements

- Windows 10 / 11
- Python 3.11+
- Dependencies listed in `requirements.txt`

---

## Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/BigH018/HWID-Info-Checker.git
   cd HWID-Info-Checker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run**
   ```bash
   python main.py
   ```

---

## Building a Standalone Executable

Use PyInstaller to produce a single `.exe` with no console window:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

The executable will be output to the `dist/` folder.

> **Note:** PyInstaller bundles your Python interpreter and all dependencies, so the `.exe` will work on machines without Python installed.

---

## Project Structure

```
HWID-Info-Checker/
├── main.py          # Entry point — creates the Qt application and launches the window
├── hardware.py      # All hardware data fetching (WMI, subprocess) and error logging
├── ui.py            # All PyQt5 UI — window layout, cards, error log panel
├── requirements.txt # Python dependencies
└── .gitignore
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'wmi'` | Run `pip install WMI pywin32` |
| `ModuleNotFoundError: No module named 'PyQt5'` | Run `pip install PyQt5` |
| Disk / Volume shows blank | Run as Administrator — some WMI queries require elevated privileges |
| Error in log: `CoInitialize` | Make sure you're running the unmodified source; this is fixed in the current version |

---

## Screenshots

![HWID Info Checker](screenshots/preview.png)

> To add your screenshot: create a `screenshots/` folder in the repo, drop your image in as `preview.png`, and push it.

---

## License

MIT License — free to use, modify, and distribute.
