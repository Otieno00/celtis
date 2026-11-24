from tkinter import ttk
from ..config import C, FONT


def install_styles():
    s = ttk.Style()
    try:
        s.theme_use("clam")
    except Exception:
        pass
    s.configure("Primary.TButton", background=C.PRIMARY, foreground="white")
    s.configure("Success.TButton", background=C.SUCCESS, foreground="white")
    s.configure("Danger.TButton",  background=C.DANGER,  foreground="white")
    s.configure("TNotebook.Tab", font=(FONT, 12, "bold"), padding=[8, 4])