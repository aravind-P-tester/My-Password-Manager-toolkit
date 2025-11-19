#!/usr/bin/env python3
"""password_checker_gui.py

Simple Tkinter GUI wrapper for the password strength checker.

Features:
- Password entry with show/hide toggle
- Check button that evaluates the password (Weak/Medium/Strong)
- Shows which categories are present and which are missing
- Detects common passwords if `common_passwords_top1000.txt` is present in the same folder

No external dependencies; works with standard Python (Tkinter included).
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple, Set


COMMON_PASSWORDS_FILENAME = "common_passwords_top1000.txt"


def check_personal_info(pw: str, name: str = "", dob: str = "") -> tuple:
    """Detect use of personal information in a password.

    Returns (is_personal: bool, found_items: list).

    - Checks name tokens (first/last/parts, length>=2) and initials.
    - Extracts digits from DOB and looks for contiguous digit substrings
      of lengths 2, 4, 6, 8 appearing in the password (e.g., 85, 1985, 03121985).

    Uses simple string operations (no regex) and is intentionally conservative.
    """
    found = []
    low_pw = (pw or "").lower()

    # Name tokens
    if name:
        for tok in name.split():
            t = tok.strip()
            if len(t) >= 2 and t.lower() in low_pw:
                found.append(f"name: {t}")

        # initials (e.g., JSmith -> js)
        parts = [p for p in name.split() if p]
        if len(parts) >= 2:
            initials = "".join(p[0].lower() for p in parts if p)
            if initials and initials in low_pw:
                found.append(f"initials: {initials}")

    # DOB digit substrings
    digits = "".join(ch for ch in dob if ch.isdigit()) if dob else ""
    if digits:
        L = len(digits)
        seen = set()
        for length in (2, 4, 6, 8):
            if L >= length:
                for i in range(0, L - length + 1):
                    sub = digits[i:i+length]
                    if sub in low_pw and sub not in seen:
                        found.append(f"dob digits: {sub}")
                        seen.add(sub)

    return (len(found) > 0, found)


def load_common_passwords() -> Set[str]:
    base = os.path.dirname(__file__)
    path = os.path.join(base, COMMON_PASSWORDS_FILENAME)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return {line.rstrip("\n\r") for line in fh if line.strip()}
    except FileNotFoundError:
        return set()


COMMON_PASSWORDS = load_common_passwords()


def evaluate_password(pw: str) -> Tuple[str, dict]:
    """Return (label, details) using same rules as the CLI checker.

    Strong requires: lowercase + UPPERCASE + digit + special and length >= 8.
    Medium: length >= 6 and at least 2 character categories.
    Weak: otherwise or if found in common-passwords list.
    """
    has_lower = False
    has_upper = False
    has_digit = False
    has_special = False

    for ch in pw:
        if ch.islower():
            has_lower = True
        elif ch.isupper():
            has_upper = True
        elif ch.isdigit():
            has_digit = True
        else:
            has_special = True

    length = len(pw)
    categories = sum((has_lower, has_upper, has_digit, has_special))

    # common-password check
    is_common = False
    if COMMON_PASSWORDS:
        if pw in COMMON_PASSWORDS or pw.lower() in {p.lower() for p in COMMON_PASSWORDS}:
            is_common = True

    if length == 0:
        label = "Weak"
    elif is_common:
        label = "Weak"
    elif length < 6 or categories <= 1:
        label = "Weak"
    elif length >= 8 and has_lower and has_upper and has_digit and has_special:
        label = "Strong"
    elif length >= 6 and categories >= 2:
        label = "Medium"
    else:
        label = "Weak"

    details = {
        "length": length,
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_special": has_special,
        "categories": categories,
        "is_common": is_common,
    }

    return label, details


def generate_suggestions(seed: str, number: str = "", max_suggestions: int = 6) -> list:
    """Generate password suggestions from a user-provided seed and optional number.

    The function applies deterministic, human-friendly transformations:
    - title/upper/lower variants
    - leetspeak substitutions
    - append/prepend number and symbols
    - ensure suggestions aim to meet the strict "Strong" criteria by
      adding missing categories when necessary.
    It avoids suggestions that match the common-password blacklist.
    """
    def leet(s: str) -> str:
        mapping = str.maketrans({
            'a': '@', 'A': '@',
            'e': '3', 'E': '3',
            'i': '1', 'I': '1',
            'o': '0', 'O': '0',
            's': '$', 'S': '$',
            't': '7', 'T': '7',
        })
        return s.translate(mapping)

    base = (seed or "").strip()
    num = (number or "").strip()
    if not base and not num:
        return []

    candidates = []
    # basic forms
    if base:
        candidates += [base, base.title(), base.upper(), base.lower(), base[::-1]]
        candidates += [leet(base), leet(base.title())]
    else:
        candidates += [num]

    symbols = ['!', '@', '#', '$', '%', '?']
    combos = []
    for c in candidates:
        # append and prepend number if present
        if num:
            combos.append(c + num)
            combos.append(num + c)
            combos.append(c + num + '!')
        # variants with symbols
        for s in symbols[:3]:
            combos.append(c + s)
            combos.append(s + c)

    # mix casing inside the word (capitalize middle)
    for c in candidates:
        if len(c) >= 3:
            mid = len(c) // 2
            mixed = c[:mid].lower() + c[mid].upper() + c[mid+1:].lower()
            combos.append(mixed)

    # ensure length and category coverage by appending a small fixed suffix when needed
    final = []
    seen = set()
    for c in combos:
        suggestion = c
        # if too short, append a predictable suffix
        if len(suggestion) < 8:
            suggestion = suggestion + 'A1!a'
        # ensure at least one symbol and digit and mixed case
        # if missing, add them deterministically
        if not any(ch.isdigit() for ch in suggestion):
            suggestion = suggestion + '1'
        if not any(ch.islower() for ch in suggestion):
            suggestion = suggestion + 'a'
        if not any(ch.isupper() for ch in suggestion):
            suggestion = 'A' + suggestion
        if not any(not ch.isalnum() for ch in suggestion):
            suggestion = suggestion + '!'

        # avoid duplicates and common passwords
        if suggestion in seen:
            continue
        if COMMON_PASSWORDS:
            lowset = {p.lower() for p in COMMON_PASSWORDS}
            if suggestion.lower() in lowset:
                continue

        seen.add(suggestion)
        final.append(suggestion)
        if len(final) >= max_suggestions:
            break

    return final


class PasswordCheckerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Strength Checker")
        # Make window resizable and attempt to maximize so it fills the display
        self.resizable(True, True)
        try:
            # Windows: this typically maximizes the window
            self.state('zoomed')
        except Exception:
            try:
                # Some platforms support the -zoomed attribute
                self.attributes('-zoomed', True)
            except Exception:
                # Fall back to geometry stretch (no-op)
                pass

        # Visual theme colors (grayscale)
        accent = "#2b2b2b"
        accent_dark = "#131313"
        bg = "#0b0b0b"          # dark window background
        card = "#1a1a1a"        # inner card/frame background (slightly lighter)
        text_color = "#e8e8e8"  # pale white for text
        entry_bg = "#121212"

        # Use a ttk theme that allows style tweaks
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Configure style elements for dark appearance
        style.configure('Card.TFrame', background=card)
        style.configure('Header.TLabel', background=accent, foreground='white', font=('Segoe UI', 36, 'bold'))
        style.configure('TLabel', background=card, foreground=text_color, font=('Segoe UI', 13))
        style.configure('TEntry', fieldbackground=entry_bg, background=entry_bg, foreground=text_color, font=('Segoe UI', 12))
        style.configure('Accent.TButton', background=accent, foreground='white', font=('Segoe UI', 12, 'bold'))
        style.map('Accent.TButton', background=[('active', accent_dark)])

        self.configure(bg=bg)
        padding = 12

        # Decorative multicolor/digital background: a Canvas with a simple gradient
        # This will sit behind the main UI. If a background image exists at
        # assets/background.png (or background.png), it will be used instead.
        self._images = getattr(self, '_images', {})
        def try_load_photo(name):
            # Prefer Pillow for resizing if available, otherwise use tkinter.PhotoImage
            base = os.path.dirname(__file__)
            candidates = [os.path.join(base, 'assets', name), os.path.join(base, name)]
            pil = None
            try:
                from PIL import Image, ImageTk
                pil = (Image, ImageTk)
            except Exception:
                pil = None

            for p in candidates:
                if os.path.exists(p):
                    try:
                        if pil:
                            Image, ImageTk = pil
                            img = Image.open(p)
                            # Resize to screen size for a full-window background
                            try:
                                sw = self.winfo_screenwidth()
                                sh = self.winfo_screenheight()
                                img = img.resize((sw, sh), Image.LANCZOS)
                            except Exception:
                                pass
                            tkimg = ImageTk.PhotoImage(img)
                            self._images[name] = tkimg
                            return tkimg
                        else:
                            tkimg = tk.PhotoImage(file=p)
                            self._images[name] = tkimg
                            return tkimg
                    except Exception:
                        # try next candidate
                        pass
            return None

        bg_img = try_load_photo('background.png')
        if bg_img:
            bg_label = ttk.Label(self, image=bg_img)
            bg_label.image = bg_img
            bg_label.grid(row=0, column=0, rowspan=3, sticky='nsew')
            bg_label.lower()
        else:
            # Draw a simple vertical gradient with overlapping translucent shapes
            bg_canvas = tk.Canvas(self, highlightthickness=0)
            bg_canvas.grid(row=0, column=0, rowspan=3, sticky='nsew')
            # Add rectangles/ovals for a colorful digital feel
            w = 1600
            h = 900
            for i, color in enumerate(['#111111', '#222222', '#333333', '#444444']):
                x0 = int((i / 4.0) * w)
                x1 = int(((i + 1) / 4.0) * w)
                bg_canvas.create_rectangle(x0, 0, x1, h, fill=color, outline=color)
            # translucent grid dots
            for x in range(0, 1600, 80):
                for y in range(0, 900, 80):
                    r = 2
                    # Tkinter doesn't support alpha in hex colors; use a pale gray instead
                    bg_canvas.create_oval(x - r, y - r, x + r, y + r, fill='#f3f4f6', outline='')
            # Note: do not call bg_canvas.lower() to avoid Tcl argument errors;
            # widgets created after this Canvas will appear above it.

        # Ensure the main grid expands so the UI fills the window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Header above the main card
        header = ttk.Label(self, text='Password Health', style='Header.TLabel')
        header.grid(row=0, column=0, padx=12, pady=(12,6), sticky='ew')

        # Description under header
        desc_text = (
            "This toolkit helps you evaluate password strength and generate secure, memorable passwords.\n\n"
            "- 'Check' evaluates a password for length, character variety, common-password matches, and whether it contains personal information.\n"
            "- 'Create' generates strong password suggestions you can copy to your clipboard.\n\n"
            "Select a card below to get started."
        )
        desc = ttk.Label(self, text=desc_text, style='TLabel', font=('Segoe UI', 11), wraplength=1000, justify='left')
        desc.grid(row=1, column=0, padx=24, pady=(6,12), sticky='ew')

        # Create three page frames: landing, check (existing), create (new)
        # Landing frame (initial) with two big option cards (multicolor)
        landing_frame = ttk.Frame(self, padding=24, style='Card.TFrame')
        landing_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,12))
        landing_frame.columnconfigure(0, weight=1)
        landing_frame.columnconfigure(1, weight=1)

        # Left card (Check) - colored card
        style.configure('LeftCard.TFrame', background='#2b2b2b')
        style.configure('LeftCard.TLabel', background='#2b2b2b', foreground='white')
        left_card = ttk.Frame(landing_frame, padding=12, style='LeftCard.TFrame')
        left_card.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        left_card.columnconfigure(0, weight=1)
        ttk.Label(left_card, text='Check', style='LeftCard.TLabel', font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, sticky='n', pady=(6,6))
        ttk.Button(left_card, text='Open Checker', style='Accent.TButton', command=lambda: self.show_frame('check')).grid(row=1, column=0, pady=(12,0))

        # Right card (Create)
        right_card = ttk.Frame(landing_frame, padding=12, style='Card.TFrame')
        right_card.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        right_card.columnconfigure(0, weight=1)
        # Right card (Create) - colored card
        style.configure('RightCard.TFrame', background='#3a3a3a')
        style.configure('RightCard.TLabel', background='#3a3a3a', foreground='white')
        right_card.configure(style='RightCard.TFrame')
        ttk.Label(right_card, text='Create', style='RightCard.TLabel', font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, sticky='n', pady=(6,6))
        ttk.Button(right_card, text='Open Creator', style='Accent.TButton', command=lambda: self.show_frame('create')).grid(row=1, column=0, pady=(12,0))

        # Check frame: re-create previous password-checking widgets here
        check_frame = ttk.Frame(self, padding=padding, style='Card.TFrame')
        check_frame.columnconfigure(0, weight=2)
        check_frame.columnconfigure(1, weight=1)
        check_frame.columnconfigure(2, weight=1)
        check_frame.rowconfigure(5, weight=1)  # details area expands

        # Personal-info inputs (REQUIRED before checking a password)
        ttk.Label(check_frame, text="Your name (required):").grid(row=0, column=0, sticky="w")
        self.user_name_var = tk.StringVar()
        ttk.Entry(check_frame, textvariable=self.user_name_var, width=24, style='TEntry').grid(row=1, column=0, sticky="w")

        ttk.Label(check_frame, text="DOB (required, e.g. 1985-03-12 or 03121985):").grid(row=0, column=1, sticky="w")
        self.user_dob_var = tk.StringVar()
        ttk.Entry(check_frame, textvariable=self.user_dob_var, width=14, style='TEntry').grid(row=1, column=1, sticky="w")

        # Password label + entry (entered after name/DOB)
        ttk.Label(check_frame, text="Enter password:").grid(row=2, column=0, sticky="w", pady=(8,0))
        self.pw_var = tk.StringVar()
        self.entry = ttk.Entry(check_frame, textvariable=self.pw_var, width=30, show="*", style='TEntry')
        self.entry.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.entry.focus()

        # Show/hide checkbox (aligned with entry)
        self.show_var = tk.BooleanVar(value=False)
        show_cb = ttk.Checkbutton(check_frame, text="Show", variable=self.show_var, command=self.toggle_show)
        show_cb.grid(row=3, column=2, padx=(6,0))

        # Check button
        check_btn = ttk.Button(check_frame, text="Check", command=self.on_check, style='Accent.TButton')
        check_btn.grid(row=4, column=0, pady=(8,0), sticky="w")

        # Strength label (larger font) - use tk.Label so we can change fg color easily
        self.strength_var = tk.StringVar(value="Strength: -")
        self.strength_label = tk.Label(check_frame, textvariable=self.strength_var, bg=card, fg=accent_dark, font=('Segoe UI', 14, 'bold'))
        self.strength_label.grid(row=4, column=1, columnspan=2, sticky="w")

        # Details text — make it expand and fill available space
        self.details = tk.Text(check_frame, wrap="word", state="disabled", bg=entry_bg, fg=text_color, bd=0, insertbackground=text_color, font=('Segoe UI', 12))
        self.details.grid(row=5, column=0, columnspan=3, sticky='nsew', pady=(8,0))

        # (Suggestions removed from checker — generation lives in Create page)

        # Back button to landing
        back_check = ttk.Button(check_frame, text='Back', command=lambda: self.show_frame('landing'))
        back_check.grid(row=8, column=2, sticky='e', pady=(8,0))

        # Create frame: password creation/generation UI
        create_frame = ttk.Frame(self, padding=padding, style='Card.TFrame')
        create_frame.columnconfigure(0, weight=2)
        create_frame.columnconfigure(1, weight=1)
        create_frame.rowconfigure(3, weight=1)

        ttk.Label(create_frame, text="Create Password", font=('Segoe UI', 14, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(create_frame, text="Seed words (optional):").grid(row=1, column=0, sticky='w')
        self.create_seed_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.create_seed_var, width=30, style='TEntry').grid(row=1, column=1, sticky='w')

        ttk.Label(create_frame, text="Number (optional):").grid(row=2, column=0, sticky='w')
        self.create_num_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.create_num_var, width=12, style='TEntry').grid(row=2, column=1, sticky='w')

        ttk.Label(create_frame, text="How many suggestions:").grid(row=1, column=2, sticky='w')
        self.create_count_var = tk.IntVar(value=6)
        ttk.Spinbox(create_frame, from_=1, to=20, textvariable=self.create_count_var, width=5).grid(row=1, column=3, sticky='w')

        gen_btn = ttk.Button(create_frame, text="Generate", style='Accent.TButton', command=self.on_generate)
        gen_btn.grid(row=2, column=2, padx=(6,0))

        # Results area for generated passwords (large and filling)
        self.create_results = tk.Text(create_frame, wrap='word', state='disabled', bg=entry_bg, fg=text_color, bd=0, insertbackground=text_color)
        self.create_results.grid(row=3, column=0, columnspan=4, sticky='nsew', pady=(8,0))

        copy_btn = ttk.Button(create_frame, text='Copy Selected', command=lambda: self.copy_to_clipboard(self.create_results))
        copy_btn.grid(row=4, column=0, pady=(8,0), sticky='w')

        back_btn = ttk.Button(create_frame, text='Back', command=lambda: self.show_frame('landing'))
        back_btn.grid(row=4, column=3, sticky='e')

        # Store frames for easy switching; show landing initially
        self._pages = {'landing': landing_frame, 'check': check_frame, 'create': create_frame}
        self.show_frame('landing')

    def on_suggest(self):
        # Prefer explicit suggestion seed/num if provided; otherwise use
        # the user's name and DOB entered at the top of the form.
        seed = self.seed_var.get() or getattr(self, 'user_name_var', tk.StringVar()).get()
        num = self.num_var.get() or getattr(self, 'user_dob_var', tk.StringVar()).get()
        suggestions = generate_suggestions(seed, num)
        # filter out suggestions that contain provided personal info (if any)
        name = self.seed_var.get()  # note: seed field may be used; also check explicit name/dob fields below
        extra_name = getattr(self, 'user_name_var', tk.StringVar()).get()
        dob = getattr(self, 'user_dob_var', tk.StringVar()).get()

        # build personal tokens to avoid
        personal_tokens = set()
        if extra_name:
            for tok in extra_name.split():
                if len(tok) >= 2:
                    personal_tokens.add(tok.lower())
            # initials
            parts = [p for p in extra_name.split() if p]
            if len(parts) >= 2:
                initials = "".join(p[0].lower() for p in parts if p)
                personal_tokens.add(initials)
        if dob:
            digits = ''.join(ch for ch in dob if ch.isdigit())
            for length in (2,4,6,8):
                if len(digits) >= length:
                    for i in range(0, len(digits)-length+1):
                        personal_tokens.add(digits[i:i+length])

        filtered = []
        for s in suggestions:
            low = s.lower()
            bad = False
            for t in personal_tokens:
                if t and t in low:
                    bad = True
                    break
            if not bad:
                filtered.append(s)
        if filtered:
            suggestions = filtered
        if not suggestions:
            messagebox.showinfo("Suggestions", "No suggestions could be generated from the provided inputs.")
            return

        # Evaluate each suggestion and present them
        lines = ["Password suggestions (examples):\n"]
        for s in suggestions:
            label, details = evaluate_password(s)
            lines.append(f"{s}  -> {label}")
        # Show in the details panel
        self.details.config(state="normal")
        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END, "\n".join(lines))
        self.details.config(state="disabled")


    def show_frame(self, name: str):
        """Show one of the pre-created frames by name (landing/check/create)."""
        for n, f in getattr(self, '_pages', {}).items():
            try:
                f.grid_remove()
            except Exception:
                pass
        frame = getattr(self, '_pages', {}).get(name)
        if frame:
            frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0,12))


    def on_generate(self):
        # Use create_seed_var and create_num_var to produce suggestions
        seed = getattr(self, 'create_seed_var', tk.StringVar()).get()
        num = getattr(self, 'create_num_var', tk.StringVar()).get()
        count = max(1, int(getattr(self, 'create_count_var', tk.IntVar(value=6)).get()))
        suggestions = generate_suggestions(seed, num, max_suggestions=count)
        if not suggestions:
            messagebox.showinfo("Generate", "No suggestions could be created from the provided inputs.")
            return

        self.create_results.config(state='normal')
        self.create_results.delete('1.0', tk.END)
        for s in suggestions:
            label, _ = evaluate_password(s)
            self.create_results.insert(tk.END, f"{s}  -> {label}\n")
        self.create_results.config(state="disabled")




    def copy_to_clipboard(self, text_widget: tk.Text):
        try:
            sel = text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
        except Exception:
            # fallback: copy all
            sel = text_widget.get('1.0', tk.END).strip()
        if not sel:
            return
        self.clipboard_clear()
        self.clipboard_append(sel)
        messagebox.showinfo('Copied', 'Selected text copied to clipboard.')


    def toggle_show(self):
        if self.show_var.get():
            self.entry.config(show="")
        else:
            self.entry.config(show="*")

    def on_check(self):
        # Ensure name and DOB are provided first (required by the flow)
        name = getattr(self, 'user_name_var', tk.StringVar()).get().strip()
        dob = getattr(self, 'user_dob_var', tk.StringVar()).get().strip()
        if not name:
            messagebox.showwarning("Missing name", "Please enter your name before checking a password.")
            return
        if not dob:
            messagebox.showwarning("Missing DOB", "Please enter your date of birth before checking a password.")
            return

        pw = self.pw_var.get()
        label, details = evaluate_password(pw)
        # check personal info fields (optional)
        name = getattr(self, 'user_name_var', tk.StringVar()).get()
        dob = getattr(self, 'user_dob_var', tk.StringVar()).get()
        try:
            is_personal, found = check_personal_info(pw, name, dob)
        except Exception:
            is_personal, found = False, []
        details['is_personal'] = is_personal
        details['personal_matches'] = found
        # If personal info is found: warn and mark as MEDIUM per request.
        if is_personal:
            matches_text = ", ".join(found) if found else "personal data"
            # Show warning inline in details; do not pop up a modal per user's request
            label = "Medium"
        else:
            # If no personal info, treat as Strong per user's instruction
            label = "Strong"

        # color mapping: Weak->orange, Medium->yellow, Strong->green
        color_map = {
            'Weak': '#f97316',   # orange
            'Medium': '#facc15', # yellow
            'Strong': '#10b981', # green
        }
        color = color_map.get(label, '#ffffff')
        try:
            self.strength_label.config(fg=color)
        except Exception:
            pass
        self.strength_var.set(f"Strength: {label}")
        self._update_details(pw, label, details)

    def _update_details(self, pw: str, label: str, details: dict):
        lines = []
        if details.get("is_common"):
            lines.append("This password is in the common-passwords list -> treat as WEAK.")
        lines.append(f"Length: {details.get('length')}")
        present = []
        missing = []
        if details.get("has_lower"):
            present.append("lowercase")
        else:
            missing.append("lowercase")
        if details.get("has_upper"):
            present.append("UPPERCASE")
        else:
            missing.append("UPPERCASE")
        if details.get("has_digit"):
            present.append("digits")
        else:
            missing.append("digits")
        if details.get("has_special"):
            present.append("symbols")
        else:
            missing.append("symbols")

        lines.append("Categories present: " + (", ".join(present) if present else "none"))
        lines.append("Categories missing: " + (", ".join(missing) if missing else "none"))

        # Suggestions
        if label == "Weak":
            lines.append("")
            lines.append("Suggestions:")
            lines.append(" - Make it at least 8 characters and include lowercase, UPPERCASE, digits, and symbols.")
            lines.append(" - Avoid common passwords and simple patterns.")
        elif label == "Medium":
            lines.append("")
            lines.append("To reach STRONG: include the missing categories and ensure length >= 8.")
        else:
            lines.append("")
            lines.append("This meets the strict criteria for Strong. Consider using a memorable passphrase for better security.")

        # Personal-info warning
        if details.get("is_personal"):
            lines.append("")
            lines.append("WARNING: This password appears to contain personal information (name or birthdate). Avoid using those in passwords.")

        # (safe_suggestions removed — generation lives in Create page)

        # Display
        self.details.config(state="normal")
        self.details.delete("1.0", tk.END)
        text = "\n".join(lines)
        self.details.insert(tk.END, text)
        # If a WARNING line exists, tag it red
        try:
            start = self.details.search('WARNING:', '1.0', tk.END)
            if start:
                end = self.details.index(f"{start} lineend")
                self.details.tag_configure('warning', foreground='#ff4d4f', font=('Segoe UI', 12, 'bold'))
                self.details.tag_add('warning', start, end)
        except Exception:
            pass
        self.details.config(state="disabled")


def main():
    app = PasswordCheckerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
