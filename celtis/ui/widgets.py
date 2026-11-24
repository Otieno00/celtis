"""Reusable tkinter widgets, value helpers, validators, and scrollable frame."""

import tkinter as tk
from tkinter import ttk, messagebox

from ..config import C, ENTRY_FONT, BOLD_FONT

CALC_BG = C.CALC
HDR_BG  = C.HDR


def entry(parent, w=10, bg="white", **kw):
    """Standard editable Entry."""
    return tk.Entry(parent, width=w, bg=bg, font=ENTRY_FONT,
                    relief=tk.SUNKEN, **kw)


def calc_entry(parent, w=10):
    """Read-only Entry used for computed results."""
    return tk.Entry(parent, width=w, bg=C.CALC, font=ENTRY_FONT,
                    relief=tk.SUNKEN, state="readonly")


def hdr(parent, text, w=None, bg=C.HDR, **grid_kw):
    """Header label (bold, centered) placed with grid()."""
    lbl_ = tk.Label(parent, text=text, bg=bg, font=BOLD_FONT,
                    relief=tk.RIDGE, anchor="center",
                    wraplength=100, justify="center")
    if w:
        lbl_.config(width=w)
    lbl_.grid(**grid_kw)
    return lbl_


def lbl(parent, text, **grid_kw):
    """Row label (regular font, left aligned)."""
    lbl_ = tk.Label(parent, text=text, font=ENTRY_FONT,
                    anchor="w", bg="#f8f8f8")
    lbl_.grid(**grid_kw)
    return lbl_


def section(parent, title, row, col, colspan=1, rowspan=1,
            padx=6, pady=4, bg="#f0f0f0"):
    """LabelFrame placed with grid()."""
    f = tk.LabelFrame(parent, text=title, font=BOLD_FONT,
                      bg=bg, padx=4, pady=4)
    f.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan,
           sticky="nsew", padx=padx, pady=pady)
    return f


def section_pack(parent, title, padx=6, pady=4, fill=tk.X, expand=False,
                 bg="#f0f0f0"):
    """LabelFrame placed with pack()."""
    f = tk.LabelFrame(parent, text=title, font=BOLD_FONT,
                      bg=bg, padx=4, pady=4)
    f.pack(fill=fill, expand=expand, padx=padx, pady=pady)
    return f


# ---------------------------------------------------------------------------
# Value helpers
# ---------------------------------------------------------------------------
def set_val(entry_widget, value, fmt=None):
    """Write `value` into `entry_widget`, preserving its previous state.

    If `fmt` is given, it is applied via an f-string format spec, e.g.
    ``set_val(e, 3.14159, ".2f")`` writes ``"3.14"``.
    """
    if entry_widget is None:
        return
    prior = entry_widget.cget("state")
    try:
        entry_widget.config(state="normal")
    except (tk.TclError, AttributeError):
        return
    entry_widget.delete(0, tk.END)
    if value is not None:
        entry_widget.insert(0, f"{value:{fmt}}" if fmt else str(value))
    try:
        entry_widget.config(state=prior if prior != "normal" else "readonly")
    except tk.TclError:
        pass


def get_float(entry_widget, default=None):
    """Parse the entry's content as float, or return `default` on failure."""
    try:
        return float(entry_widget.get())
    except (ValueError, tk.TclError, AttributeError):
        return default


def is_calc(entry_widget):
    """True if the entry is currently read-only (a computed field)."""
    try:
        return entry_widget.cget("state") == "readonly"
    except (tk.TclError, AttributeError):
        return False


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------
def _parse(entry_widget, name):
    try:
        return float(entry_widget.get())
    except (ValueError, TypeError, AttributeError):
        messagebox.showerror("Validation Error", f"{name} must be a number")
        entry_widget.focus_set()
        return None


def validate_positive(entry_widget, name):
    v = _parse(entry_widget, name)
    if v is None:
        return None
    if v <= 0:
        messagebox.showerror("Validation Error", f"{name} must be positive")
        entry_widget.focus_set()
        return None
    return v


def validate_non_empty(entry_widget, name):
    v = (entry_widget.get() or "").strip()
    if not v:
        messagebox.showerror("Validation Error", f"{name} cannot be empty")
        entry_widget.focus_set()
        return None
    return v


def validate_range(entry_widget, name, lo, hi):
    v = _parse(entry_widget, name)
    if v is None:
        return None
    if not (lo <= v <= hi):
        messagebox.showerror(
            "Validation Error", f"{name} must be between {lo} and {hi}")
        entry_widget.focus_set()
        return None
    return v


# ---------------------------------------------------------------------------
# Scrollable frame
# ---------------------------------------------------------------------------
def scrolled_frame(parent):
    """Create a scrollable container.

    Returns ``(outer, inner, canvas)``. Put content inside ``inner``.
    """
    outer = tk.Frame(parent)
    outer.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(outer, bg="#f0f0f0", highlightthickness=0)
    vsb = ttk.Scrollbar(outer, orient=tk.VERTICAL, command=canvas.yview)
    hsb = ttk.Scrollbar(outer, orient=tk.HORIZONTAL, command=canvas.xview)
    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    inner = tk.Frame(canvas, bg="#f0f0f0")
    win = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _resize(_=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfig(win, width=max(canvas.winfo_width(),
                                         inner.winfo_reqwidth()))
    inner.bind("<Configure>", _resize)
    canvas.bind("<Configure>", _resize)

    # ---- scroll handlers ------------------------------------------------
    def _y_scroll(e):
        delta = getattr(e, "delta", 0)
        num   = getattr(e, "num", None)
        if delta:
            canvas.yview_scroll(int(-1 * (delta / 120)), "units")
        elif num == 4:
            canvas.yview_scroll(-2, "units")
        elif num == 5:
            canvas.yview_scroll(2, "units")

    def _x_scroll(e):
        delta = getattr(e, "delta", 0)
        num   = getattr(e, "num", None)
        if delta:
            canvas.xview_scroll(int(-1 * (delta / 120)), "units")
        elif num == 4:
            canvas.xview_scroll(-2, "units")
        elif num == 5:
            canvas.xview_scroll(2, "units")

    SEQ = ("<MouseWheel>", "<Button-4>", "<Button-5>", "<Shift-MouseWheel>",
           "<Up>", "<Down>", "<Left>", "<Right>", "<Prior>", "<Next>",
           "<Home>", "<End>")

    def _bind(_=None):
        canvas.bind_all("<MouseWheel>", _y_scroll)
        canvas.bind_all("<Button-4>", _y_scroll)
        canvas.bind_all("<Button-5>", _y_scroll)
        canvas.bind_all("<Shift-MouseWheel>", _x_scroll)
        canvas.bind_all("<Up>",    lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Down>",  lambda e: canvas.yview_scroll( 1, "units"))
        canvas.bind_all("<Left>",  lambda e: canvas.xview_scroll(-1, "units"))
        canvas.bind_all("<Right>", lambda e: canvas.xview_scroll( 1, "units"))
        canvas.bind_all("<Prior>", lambda e: canvas.yview_scroll(-5, "units"))
        canvas.bind_all("<Next>",  lambda e: canvas.yview_scroll( 5, "units"))
        canvas.bind_all("<Home>",  lambda e: canvas.yview_moveto(0))
        canvas.bind_all("<End>",   lambda e: canvas.yview_moveto(1))

    def _unbind(_=None):
        for seq in SEQ:
            try:
                canvas.unbind_all(seq)
            except Exception:
                pass

    canvas.bind("<Enter>", _bind)
    canvas.bind("<Leave>", _unbind)
    inner.bind("<Enter>", _bind)
    return outer, inner, canvas