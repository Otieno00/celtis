"""Entry point — `python -m celtis.main` or `python celtis/main.py`."""
import os
import sys

# --- PATH FIX (Must happen before importing celtis.app) ---
if getattr(sys, 'frozen', False):
    # If running as an EXE, use the folder where CELTIS.exe lives
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If running as source code, use the outer 'CELTIS' folder
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.chdir(BASE_DIR)
# ----------------------------------------------------------

import tkinter as tk
from celtis.app import CeltisApp

def main():
    root = tk.Tk()
    try:
        # Look for the icon in the current folder (BASE_DIR)
        icon = os.path.join(BASE_DIR, "celtis_logo.ico")
        if os.path.exists(icon):
            root.iconbitmap(icon)
    except Exception:
        pass
    
    CeltisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()