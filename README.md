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
python scripts\generate_hud.py
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
