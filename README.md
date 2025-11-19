Password Checker GUI
====================

This folder is prepared for upload. It contains the GUI application and a small helper script used to generate a background image.

Files included
- `password_checker_gui.py` - main Tkinter GUI application
- `scripts/generate_hud.py` - Pillow-based script to generate `assets/background.png`
- `assets/` - contains a placeholder; please copy your `background.png` here if you want the GUI to show a background image

Quick start
1. (Optional) Create and activate a virtual environment.

PowerShell example:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Generate the background image (optional). If you already have `assets/background.png`, skip this step.

```powershell
python scripts\\generate_hud.py
```

4. Run the GUI:

```powershell
python password_checker_gui.py
```

Notes
- If you want the GUI to use a background image, ensure `assets/background.png` exists. If Pillow is installed the script will resize the image to the screen size.
- The GUI requires Tkinter (usually included with the standard Python installer). If you get errors about Tk, ensure your Python distribution includes Tk support.

Security / privacy
- The GUI intentionally asks for `Name` and `DOB` during the check flow to detect personal info being used in a password. Do not enter sensitive personal data unless you trust the local machine.

Installation (Windows and Linux)
--------------------------------

Follow the platform-specific instructions below. The steps are the same conceptually: create a virtual environment (recommended), install dependencies, optionally generate the background image, then run the GUI.

Windows (PowerShell)
- Create and activate a virtual environment, then install dependencies:

```powershell
# create and activate venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt
```

- If you don't want a virtual environment, run `pip install -r requirements.txt` in your normal environment.

- If you don't have Tkinter installed (rare on Windows default Python), install the official Python from python.org and ensure the "tcl/tk and IDLE" option is selected during installation.

- Generate the background image (optional):

```powershell
python scripts\generate_hud.py
```

- Run the GUI:

```powershell
python password_checker_gui.py
```

Linux (bash)
- Create and activate a virtual environment and install dependencies:

```bash
# create and activate the venv
python3 -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt
```

- Tkinter availability: many Linux distributions package Tk separately. If you see errors about missing `tk` or `tkinter`, install the system package:

Debian/Ubuntu:
```bash
sudo apt update
sudo apt install python3-tk
```

Fedora / RHEL (dnf):
```bash
sudo dnf install python3-tkinter
```

Arch Linux:
```bash
sudo pacman -S tk
```

- Generate the background image (optional):

```bash
python3 scripts/generate_hud.py
```

- Run the GUI:

```bash
python3 password_checker_gui.py
```

Troubleshooting
---------------
- If the app fails to start with errors referencing `PIL` or `Pillow`, ensure `Pillow` is installed (`pip install Pillow`) or re-run `pip install -r requirements.txt`.
- If the GUI displays but the background image does not appear, ensure `assets/background.png` exists. The app will fall back to a simple canvas if no image is present.
- On some Linux desktops you may need an X11 or Wayland session with GUI support; running the app over plain SSH without X forwarding will not display the window.

Licensing / Attribution
------------------------
This package is a small educational toolkit for learning Python/Tkinter and is provided without warranty. Feel free to adapt or relicense before uploading to a public repository.
