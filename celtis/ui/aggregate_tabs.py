"""Aggregate tabs — 11 sub-tabs, BaseTab pattern.

   Each sub-tab is a BaseTab subclass; build() is the equivalent of the
   original _build_*_tab body, adapted to the widget helpers used by
   the soil tabs (grid-based sections, save_to_log, make_stored_panel).
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import webbrowser

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ..config import C, FONT
from ..ui.base_tab import BaseTab
from ..ui.widgets import (entry, calc_entry, hdr, section, scrolled_frame,
                          set_val, get_float)


# ---------------------------------------------------------------------
# Shared header helper (project / location / depth strip)
# ---------------------------------------------------------------------
def cml_header(parent, title, test_method, row=0, colspan=8):
    """Grid-placed CML-style header (uses pack internally)."""
    wrapper = tk.Frame(parent, bg="#f8f8f8")
    wrapper.grid(row=row, column=0, columnspan=colspan, sticky="ew")

    title_f = tk.Frame(wrapper, bg="#1f3864", pady=5)
    title_f.pack(fill=tk.X)
    for line in title.split("\n"):
        tk.Label(title_f, text=line, bg="#1f3864", fg="white",
                 font=("Times New Roman", 12, "bold")).pack()

    pf = tk.Frame(wrapper, bg="#f8f8f8", relief=tk.RIDGE, bd=1)
    pf.pack(fill=tk.X, padx=6, pady=4)
    fields = {}
    rows_def = [
        [("Project:", "project", 28), ("Location:", "location", 18), ("Depth:", "depth", 10)],
        [("Client:", "client", 28), ("Lab.no:", "labno", 18), ("Date:", "date", 10)],
        [("Resp. Technician:", "tech", 28), ("Checked:", "checked", 18),
         ("Approved:", "approved", 10)],
    ]
    for ri, row_defs in enumerate(rows_def):
        for ci, (lt, key, w) in enumerate(row_defs):
            tk.Label(pf, text=lt, bg="#f8f8f8",
                     font=("Times New Roman", 12, "bold"),
                     relief=tk.RIDGE, width=18 if ci == 0 else 10,
                     anchor="w", padx=4).grid(
                row=ri, column=ci * 2, sticky="ew", padx=1, pady=1)
            e = entry(pf, w=w)
            e.grid(row=ri, column=ci * 2 + 1, sticky="ew", padx=1, pady=1)
            fields[key] = e
    fields["date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

    tm_f = tk.Frame(wrapper, bg="#ecf0f1", relief=tk.RIDGE, bd=1)
    tm_f.pack(fill=tk.X, padx=6, pady=2)
    tk.Label(tm_f, text=f"TEST METHOD    {test_method}", bg="#ecf0f1",
             font=("Times New Roman", 12), anchor="w", padx=8).pack(fill=tk.X)
    return fields


# =====================================================================
# 1. MOISTURE CONTENT
# =====================================================================
class MoistureContentTab(BaseTab):
    tab_label = "💧 Moisture Content"
    log_category = "agg_moisture"
    log_columns = (("w", "w (%)", 70), ("sample", "Sample", 120))

    NUM_SPEC = 8

    def build(self):
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Moisture Content of Aggregates",
                   "REF. BS 812 : Part 109 : 1990",
                   row=0, colspan=self.NUM_SPEC + 2)

        tbl_f = section(inner, "Test Data", 1, 0, colspan=self.NUM_SPEC + 2)

        row_defs = [
            ("Specimen reference", "spec_ref", False),
            ("Container no.", "cont_no", False),
            ("Mass wet portion + container (m₂)", "m2", False),
            ("Mass dry portion + container (m₃)", "m3", False),
            ("Mass of container  (m₁)", "m1", False),
            ("Mass of moisture  (m₂ - m₃)", "moisture", True),
            ("Mass of dry test portion  (m₃ - m₁)", "dry_mass", True),
            ("Moisture Content  w = ((m₂−m₃)/(m₃−m₁))×100", "w", True),
        ]
        units = ["", "", "g", "g", "g", "g", "g", "%"]

        tk.Label(tbl_f, text="Parameter", bg=C.HDR,
                 font=("Times New Roman", 12, "bold"),
                 relief=tk.RIDGE, width=32, anchor="w").grid(
            row=0, column=0, padx=1, pady=1, sticky="ew")
        tk.Label(tbl_f, text="Unit", bg=C.HDR,
                 font=("Times New Roman", 12, "bold"),
                 relief=tk.RIDGE, width=5, anchor="center").grid(
            row=0, column=1, padx=1, pady=1)
        for i in range(self.NUM_SPEC):
            tk.Label(tbl_f, text=str(i + 1), bg=C.HDR,
                     font=("Times New Roman", 12, "bold"),
                     relief=tk.RIDGE, width=9, anchor="center").grid(
                row=0, column=i + 2, padx=1, pady=1)

        self.cells = {}
        for ri, (lbl_txt, key, is_c) in enumerate(row_defs):
            tk.Label(tbl_f, text=lbl_txt, bg="#f8f8f8",
                     font=("Times New Roman", 12, "bold"),
                     relief=tk.RIDGE, width=32, anchor="w",
                     wraplength=230, justify="left").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(tbl_f, text=units[ri], bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri + 1, column=1, padx=1, pady=1)
            for ci in range(self.NUM_SPEC):
                e = calc_entry(tbl_f, w=9) if is_c else entry(tbl_f, w=9)
                e.grid(row=ri + 1, column=ci + 2, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=2, column=0, columnspan=self.NUM_SPEC + 2,
                sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=3, column=0, columnspan=self.NUM_SPEC + 2,
                   sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        for ci in range(self.NUM_SPEC):
            try:
                m1 = float(self.cells[("m1", ci)].get())
                m2 = float(self.cells[("m2", ci)].get())
                m3 = float(self.cells[("m3", ci)].get())
                moisture = m2 - m3
                dry_mass = m3 - m1
                w = (moisture / dry_mass * 100) if dry_mass else 0
                set_val(self.cells[("moisture", ci)], f"{moisture:.2f}")
                set_val(self.cells[("dry_mass", ci)], f"{dry_mass:.2f}")
                set_val(self.cells[("w", ci)], f"{w:.2f}")
            except (ValueError, ZeroDivisionError):
                pass

    def _save_log(self):
        w_val = ""
        sample = ""
        for ci in range(self.NUM_SPEC):
            v = self.cells[("w", ci)].get()
            if v:
                w_val = v
                sample = self.cells[("spec_ref", ci)].get() or f"Spec {ci+1}"
                break
        if not w_val:
            return messagebox.showwarning("Warning", "Calculate first.")
        ts = self.save_to_log(sample or "Moisture", {"w": w_val, "sample": sample})
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")


# =====================================================================
# 2. RELATIVE DENSITY & WATER ABSORPTION
# =====================================================================
class RelativeDensityTab(BaseTab):
    tab_label = "⚖️ Rel. Density & WA"
    log_category = "agg_rd"
    log_columns = (("rd", "RD", 70), ("wa", "WA %", 70))

    def build(self):
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Relative Density and Water Absorption",
                   "CML TEST 2.2,  ref. BS 812 : Part 2 : 1975",
                   row=0, colspan=6)

        self.cells = {}

        def build_block(title, prefix, row):
            bf = section(inner, title, row, 0, colspan=6)
            col_hdrs = [("Parameter", 30), ("Symbol", 14), ("Unit", 6),
                        ("A", 10), ("B", 10), ("Mean", 10)]
            for ci, (h_txt, w) in enumerate(col_hdrs):
                tk.Label(bf, text=h_txt, bg=C.HDR,
                         font=("Times New Roman", 12, "bold"),
                         relief=tk.RIDGE, width=w, anchor="center").grid(
                    row=0, column=ci, padx=1, pady=1, sticky="ew")
            rd_rows = [
                ("Mass of saturated surface-dry aggregate in air", "A", "g",
                 "a_a", "a_b", False),
                ("Mass of vessel + sample filled with water", "B", "g",
                 "b_a", "b_b", False),
                ("Mass of vessel filled with water only", "C", "g",
                 "c_a", "c_b", False),
                ("Mass of oven-dry aggregate in air", "D", "g",
                 "d_a", "d_b", False),
                ("Apparent relative density  ρa", "D/(D-(B-C))", "t/m³",
                 "rap_a", "rap_b", True),
                ("Water Absorption  Wabs", "((A-D)/D)×100", "%",
                 "wa_a", "wa_b", True),
            ]
            for ri, (lbl, sym, unit, ka, kb, is_c) in enumerate(rd_rows):
                tk.Label(bf, text=lbl, bg="#f8f8f8",
                         font=("Times New Roman", 12), relief=tk.RIDGE,
                         width=30, anchor="w", wraplength=210,
                         justify="left").grid(
                    row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
                tk.Label(bf, text=sym, bg="#fffacd",
                         font=("Times New Roman", 12), relief=tk.RIDGE,
                         width=14, anchor="center", wraplength=95).grid(
                    row=ri + 1, column=1, padx=1, pady=1, sticky="ew")
                tk.Label(bf, text=unit, bg="#f8f8f8",
                         font=("Times New Roman", 12), relief=tk.RIDGE,
                         width=6, anchor="center").grid(
                    row=ri + 1, column=2, padx=1, pady=1)
                for col_idx, k in enumerate([ka, kb]):
                    e = calc_entry(bf, w=10) if is_c else entry(bf, w=10)
                    e.grid(row=ri + 1, column=col_idx + 3,
                           padx=1, pady=1, sticky="ew")
                    self.cells[f"{prefix}_{k}"] = e
                e_mean = calc_entry(bf, w=10)
                e_mean.grid(row=ri + 1, column=5, padx=1, pady=1, sticky="ew")
                self.cells[f"{prefix}_{ka}_mean"] = e_mean

        build_block("Method 1 – Pycnometer", "pyk", 1)
        build_block("Method 2 – Wire Basket", "bsk", 2)

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=3, column=0, columnspan=6, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=4, column=0, columnspan=6, sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        for pfx in ("pyk", "bsk"):
            for ab in ("a", "b"):
                try:
                    A = float(self.cells[f"{pfx}_a_{ab}"].get())
                    B = float(self.cells[f"{pfx}_b_{ab}"].get())
                    Cv = float(self.cells[f"{pfx}_c_{ab}"].get())
                    D = float(self.cells[f"{pfx}_d_{ab}"].get())
                    d2 = D - (B - Cv)
                    set_val(self.cells[f"{pfx}_rap_{ab}"],
                            f"{D/d2:.3f}" if d2 else "")
                    set_val(self.cells[f"{pfx}_wa_{ab}"],
                            f"{(A-D)/D*100:.2f}" if D else "")
                except (ValueError, ZeroDivisionError, KeyError):
                    pass
            for k in ("rap", "wa"):
                try:
                    va = float(self.cells[f"{pfx}_{k}_a"].get())
                    vb = float(self.cells[f"{pfx}_{k}_b"].get())
                    set_val(self.cells[f"{pfx}_{k}_a_mean"],
                            f"{(va+vb)/2:.3f}")
                except (ValueError, KeyError):
                    pass

    def _save_log(self):
        data = {}
        for pfx in ("pyk", "bsk"):
            rap = self.cells.get(f"{pfx}_rap_a_mean")
            wa = self.cells.get(f"{pfx}_wa_a_mean")
            if rap and rap.get():
                data[f"{pfx}_rd"] = rap.get()
                data["rd"] = rap.get()
            if wa and wa.get():
                data[f"{pfx}_wa"] = wa.get()
                data["wa"] = wa.get()
        if not data:
            return messagebox.showwarning("Warning", "Calculate first.")
        ts = self.save_to_log("Rel Density", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")


# =====================================================================
# 3. FLAKINESS INDEX + ALD
# =====================================================================
class FlakinessTab(BaseTab):
    tab_label = "🪨 FI + ALD"
    log_category = "agg_fi"
    log_columns = (("fi_result", "FI (%)", 80),)

    FI_FRACS = [("63", "50", "33.9"), ("50", "37.5", "26.3"),
                ("37.5", "28", "19.7"), ("28", "20", "14.4"),
                ("20", "14", "10.2"), ("14", "10", "7.2"),
                ("10", "6.3", "4.9")]

    def build(self):
        N = len(self.FI_FRACS)
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Flakiness Index - FI / Average Least Dimension - ALD",
                   "CML TEST 2.4,  ref. BS 812 : Section 105.1 : 1989",
                   row=0, colspan=N + 2)

        FRAC_LABELS = [f"{f[0]}/{f[1]}" for f in self.FI_FRACS]

        spec_f = section(inner, "Fraction Gauged", 1, 0, colspan=N + 2)
        for ci, h_txt in enumerate(["", "mm"] + FRAC_LABELS):
            w = 28 if ci == 0 else (5 if ci == 1 else 8)
            tk.Label(spec_f, text=h_txt, bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=w, anchor="center", wraplength=55).grid(
                row=0, column=ci, padx=1, pady=1, sticky="ew")
        for ri, (lbl, unit, vals_idx) in enumerate([
                ("Passing sieve", "mm", 0),
                ("Retained on sieve", "mm", 1),
                ("Slots width", "mm", 2),
                ("Fraction Gauged", "x", None)]):
            tk.Label(spec_f, text=lbl, bg="#f0f8ff",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=28, anchor="w").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(spec_f, text=unit, bg="#f0f8ff",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri + 1, column=1, padx=1, pady=1)
            for ci, frac in enumerate(self.FI_FRACS):
                if vals_idx is not None:
                    tk.Label(spec_f, text=frac[vals_idx], bg="#f0f8ff",
                             font=("Times New Roman", 12), relief=tk.RIDGE,
                             width=8, anchor="center").grid(
                        row=ri + 1, column=ci + 2, padx=1, pady=1)
                else:
                    entry(spec_f, w=8).grid(row=ri + 1, column=ci + 2,
                                             padx=1, pady=1)

        bg_f = section(inner, "Before Gauging", 2, 0, colspan=N + 2)
        self.cells = {}
        bg_rows = [
            ("Mass of tray + Aggregate fraction", "g", "bg_tray_agg", False),
            ("Mass of tray", "g", "bg_tray", False),
            ("Mass of Aggregate fraction  M₀", "g", "bg_m0", True),
            ("Individual percentage  M₀/M₁ × 100", "%", "bg_pct", True),
            ("Sum of Aggregate mass  M₁", "g", "bg_m1", True),
            ("Remaining sum of Aggregate mass  M₂", "g", "bg_m2", True),
        ]
        for ri, (lbl, unit, key, is_c) in enumerate(bg_rows):
            tk.Label(bg_f, text=lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=28, anchor="w", wraplength=200).grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(bg_f, text=unit, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            for ci in range(N):
                e = calc_entry(bg_f, w=8) if is_c else entry(bg_f, w=8)
                e.grid(row=ri, column=ci + 2, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e

        ag_f = section(inner, "After Gauging", 3, 0, colspan=4)
        ag_rows = [
            ("Mass of tray + Sum passing slots", "g", "ag_tray_pass", False),
            ("Mass of tray", "g", "ag_tray", False),
            ("Sum of Aggregate mass passing slots  M₃", "g", "ag_m3", True),
            ("Flakiness Index  FI = M₃/M₂ × 100", "%", "fi_result", True),
        ]
        for ri, (lbl, unit, key, is_c) in enumerate(ag_rows):
            tk.Label(ag_f, text=lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12,
                           "bold" if "FI" in lbl else "normal"),
                     relief=tk.RIDGE, width=28, anchor="w").grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(ag_f, text=unit, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            e = calc_entry(ag_f, w=12) if is_c else entry(ag_f, w=12)
            e.grid(row=ri, column=2, padx=1, pady=1, sticky="ew")
            self.cells[(key, 0)] = e

        ald_f = section(inner, "Average Least Dimension (ALD)", 4, 0, colspan=4)
        for ri, (lbl, key) in enumerate([
                ("Median size (sieve through which 50% pass)  mm", "ald_median"),
                ("Average Least Dimension – ALD (from nomograph)  mm", "ald_result")]):
            tk.Label(ald_f, text=lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=40, anchor="w").grid(row=ri, column=0,
                                                 padx=1, pady=2, sticky="ew")
            e = entry(ald_f, w=12)
            e.grid(row=ri, column=1, padx=4, pady=2)
            self.cells[(key, 0)] = e

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=5, column=0, columnspan=N + 2, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate FI", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=6, column=0, columnspan=N + 2, sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        m0_vals, m1_total = [], 0
        for ci in range(len(self.FI_FRACS)):
            try:
                m0 = (get_float(self.cells[("bg_tray_agg", ci)], 0)
                      - get_float(self.cells[("bg_tray", ci)], 0))
                set_val(self.cells[("bg_m0", ci)], f"{m0:.1f}")
                m0_vals.append(m0)
                m1_total += m0
            except Exception:
                m0_vals.append(0)
        lt5 = sum(m0 for m0 in m0_vals
                  if (m0 / m1_total * 100 if m1_total else 0) < 5)
        m2 = m1_total - lt5
        for ci, m0 in enumerate(m0_vals):
            pct = (m0 / m1_total * 100) if m1_total else 0
            set_val(self.cells[("bg_pct", ci)], f"{pct:.1f}")
            set_val(self.cells[("bg_m1", ci)], f"{m1_total:.1f}")
            set_val(self.cells[("bg_m2", ci)], f"{m2:.1f}")
        try:
            m3 = (get_float(self.cells[("ag_tray_pass", 0)], 0)
                  - get_float(self.cells[("ag_tray", 0)], 0))
            set_val(self.cells[("ag_m3", 0)], f"{m3:.1f}")
            fi = (m3 / m2 * 100) if m2 else 0
            set_val(self.cells[("fi_result", 0)], f"{fi:.1f}")
        except Exception:
            pass

    def _save_log(self):
        fi = self.cells[("fi_result", 0)].get()
        if not fi:
            return messagebox.showwarning("Warning", "Calculate first.")
        data = {"fi_result": fi,
                "ald": self.cells[("ald_result", 0)].get(),
                "median": self.cells[("ald_median", 0)].get()}
        ts = self.save_to_log("Flakiness", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")


# =====================================================================
# 4. ELONGATION INDEX
# =====================================================================
class ElongationTab(BaseTab):
    tab_label = "📏 Elongation Index"
    log_category = "agg_ei"
    log_columns = (("ei_result", "EI (%)", 80),)

    EI_FRACS = [("50", "37.5", "78.7"), ("37.5", "28", "59.0"),
                ("28", "20", "43.2"), ("20", "14", "30.6"),
                ("14", "10", "21.6"), ("10", "6.3", "14.7")]

    def build(self):
        N = len(self.EI_FRACS)
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Elongation Index - EI",
                   "CML TEST 2.5,  ref. BS 812 : Section 105.2 : 1990",
                   row=0, colspan=N + 2)

        FRAC_LABELS = [f"{f[0]}/{f[1]}" for f in self.EI_FRACS]
        spec_f = section(inner, "Fraction Gauged", 1, 0, colspan=N + 2)
        for ci, h_txt in enumerate(["", "mm"] + FRAC_LABELS):
            w = 28 if ci == 0 else (5 if ci == 1 else 8)
            tk.Label(spec_f, text=h_txt, bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=w, anchor="center", wraplength=55).grid(
                row=0, column=ci, padx=1, pady=1, sticky="ew")
        for ri, (lbl, unit, vals_idx) in enumerate([
                ("Passing sieve", "mm", 0),
                ("Retained on sieve", "mm", 1),
                ("Gaps between pins", "mm", 2),
                ("Fraction Gauged", "x", None)]):
            tk.Label(spec_f, text=lbl, bg="#f0f8ff",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=28, anchor="w").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(spec_f, text=unit, bg="#f0f8ff",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri + 1, column=1, padx=1, pady=1)
            for ci, frac in enumerate(self.EI_FRACS):
                if vals_idx is not None:
                    tk.Label(spec_f, text=frac[vals_idx], bg="#f0f8ff",
                             font=("Times New Roman", 12), relief=tk.RIDGE,
                             width=8, anchor="center").grid(
                        row=ri + 1, column=ci + 2, padx=1, pady=1)
                else:
                    entry(spec_f, w=8).grid(row=ri + 1, column=ci + 2,
                                             padx=1, pady=1)

        bg_f = section(inner, "Before Gauging", 2, 0, colspan=N + 2)
        self.cells = {}
        for ri, (lbl, unit, key, is_c) in enumerate([
                ("Mass of tray + Aggregate fraction", "g", "bg_tray_agg", False),
                ("Mass of tray", "g", "bg_tray", False),
                ("Mass of Aggregate fraction  M₀", "g", "bg_m0", True),
                ("Individual percentage  M₀/M₁ × 100", "%", "bg_pct", True),
                ("Sum of Aggregate mass  M₁", "g", "bg_m1", True),
                ("Sum of fractions less than 5% of M₁", "g", "bg_lt5", True),
                ("Remaining sum of Aggregate mass  M₂", "g", "bg_m2", True)]):
            tk.Label(bg_f, text=lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=28, anchor="w", wraplength=200).grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(bg_f, text=unit, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            for ci in range(N):
                e = calc_entry(bg_f, w=8) if is_c else entry(bg_f, w=8)
                e.grid(row=ri, column=ci + 2, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e

        ag_f = section(inner, "After Gauging", 3, 0, colspan=4)
        for ri, (lbl, unit, key, is_c) in enumerate([
                ("Mass of tray + Sum not passing gaps", "g",
                 "ag_tray_notpass", False),
                ("Mass of tray", "g", "ag_tray", False),
                ("Sum of Aggregate mass not passing gaps  M₃", "g",
                 "ag_m3", True),
                ("Elongation Index  EI = M₃/M₂ × 100", "%",
                 "ei_result", True)]):
            tk.Label(ag_f, text=lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12,
                           "bold" if "EI" in lbl else "normal"),
                     relief=tk.RIDGE, width=28, anchor="w").grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(ag_f, text=unit, bg="#f8f8f8",
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=5, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            e = calc_entry(ag_f, w=12) if is_c else entry(ag_f, w=12)
            e.grid(row=ri, column=2, padx=1, pady=1, sticky="ew")
            self.cells[(key, 0)] = e

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=N + 2, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate EI", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=5, column=0, columnspan=N + 2, sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        m1_total, m0_vals = 0, []
        for ci in range(len(self.EI_FRACS)):
            try:
                m0 = (get_float(self.cells[("bg_tray_agg", ci)], 0)
                      - get_float(self.cells[("bg_tray", ci)], 0))
                set_val(self.cells[("bg_m0", ci)], f"{m0:.1f}")
                m0_vals.append(m0)
                m1_total += m0
            except Exception:
                m0_vals.append(0)
        lt5 = sum(m0 for m0 in m0_vals
                  if (m0 / m1_total * 100 if m1_total else 0) < 5)
        m2 = m1_total - lt5
        for ci, m0 in enumerate(m0_vals):
            set_val(self.cells[("bg_pct", ci)],
                    f"{(m0/m1_total*100) if m1_total else 0:.1f}")
            set_val(self.cells[("bg_m1", ci)], f"{m1_total:.1f}")
            set_val(self.cells[("bg_lt5", ci)], f"{lt5:.1f}")
            set_val(self.cells[("bg_m2", ci)], f"{m2:.1f}")
        try:
            m3 = (get_float(self.cells[("ag_tray_notpass", 0)], 0)
                  - get_float(self.cells[("ag_tray", 0)], 0))
            set_val(self.cells[("ag_m3", 0)], f"{m3:.1f}")
            set_val(self.cells[("ei_result", 0)],
                    f"{(m3/m2*100) if m2 else 0:.1f}")
        except Exception:
            pass

    def _save_log(self):
        ei = self.cells[("ei_result", 0)].get()
        if not ei:
            return messagebox.showwarning("Warning", "Calculate first.")
        ts = self.save_to_log("Elongation", {"ei_result": ei})
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")


# =====================================================================
# 5. ACV
# =====================================================================
class AcvTab(BaseTab):
    tab_label = "💥 ACV"
    log_category = "agg_acv"
    log_columns = (("mean", "Mean ACV", 90), ("median", "Median", 90))

    NUM = 5

    FRACTIONS = [("28 - 20 mm", "5.0 mm", ""),
                 ("20 - 14 mm", "3.35 mm", ""),
                 ("14 - 10 mm", "2.36 mm", "STANDARD"),
                 ("10 - 6.3 mm", "1.70 mm", ""),
                 ("6.3 - 5.0 mm", "1.18 mm", ""),
                 ("5.0 - 3.35 mm", "850 µm", ""),
                 ("3.35 - 2.36 mm", "600 µm", "")]

    def build(self):
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Aggregate Crushing Value  ACV",
                   "CML TEST 2.6,  ref. BS 812 : Part 110 : 1990",
                   row=0, colspan=self.NUM + 1)

        frac_f = section(inner, "Fraction Tested / Separating Sieve",
                         1, 0, colspan=3)
        for ri, (frac, sep, note) in enumerate(self.FRACTIONS):
            bg_c = "#fff3cd" if note else "#f8f8f8"
            tk.Label(frac_f, text=frac, bg=bg_c,
                     font=("Times New Roman", 12,
                           "bold" if note else "normal"),
                     relief=tk.RIDGE, width=16, anchor="w").grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(frac_f, text=sep, bg=bg_c,
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=12, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            if note:
                tk.Label(frac_f, text=note, bg="#fff3cd",
                         font=("Times New Roman", 12, "bold"),
                         relief=tk.RIDGE, width=14).grid(
                    row=ri, column=2, padx=1, pady=1)

        data_f = section(inner, "Test Data", 2, 0, colspan=self.NUM + 1)
        acv_rows = [
            ("Specimen reference", "spec_ref", False),
            ("Mass of tray + test specimen (g)", "tray_spec", False),
            ("Mass of tray alone (g)", "tray", False),
            ("Mass of original test specimen  M₁ (g)", "m1", True),
            ("Mass of tray + material passing separating sieve (g)",
             "tray_pass", False),
            ("Mass of tray alone (g)", "tray2", False),
            ("Mass of material passing separating sieve  M₂ (g)", "m2", True),
            ("Mass of tray alone (g)", "tray3", False),
            ("Mass of tray + material retained on separating sieve (g)",
             "tray_ret", False),
            ("Mass of material retained on separating sieve  M₃ (g)",
             "m3", True),
            ("M₂ + M₃  (check vs M₁)", "m2m3", True),
            ("Aggregate Crushing Value (%)  M₂/M₁ × 100", "acv_pct", True),
        ]
        tk.Label(data_f, text="Parameter", bg=C.HDR,
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=38, anchor="w").grid(row=0, column=0, padx=1, pady=1,
                                             sticky="ew")
        for ci in range(self.NUM):
            tk.Label(data_f, text=str(ci + 1), bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=10, anchor="center").grid(
                row=0, column=ci + 1, padx=1, pady=1)

        self.cells = {}
        for ri, (lbl, key, is_c) in enumerate(acv_rows):
            is_result = key == "acv_pct"
            bg_c = "#fff2cc" if is_result else "#f8f8f8"
            tk.Label(data_f, text=lbl, bg=bg_c,
                     font=("Times New Roman", 12,
                           "bold" if is_result else "normal"),
                     relief=tk.RIDGE, width=38, anchor="w",
                     wraplength=280, justify="left").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            for ci in range(self.NUM):
                e = calc_entry(data_f, w=10) if is_c else entry(data_f, w=10)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e

        sum_f = section(inner, "Summary", 3, 0, colspan=2)
        self.summary = {}
        for ri, (lbl, key) in enumerate([("ACV – mean value (%)", "mean"),
                                          ("ACV – median value (%)", "median")]):
            tk.Label(sum_f, text=lbl, bg="#fffacd",
                     font=("Times New Roman", 12, "bold"),
                     relief=tk.RIDGE, width=30, anchor="w").grid(
                row=ri, column=0, padx=1, pady=2, sticky="ew")
            e = calc_entry(sum_f, w=12)
            e.grid(row=ri, column=1, padx=4, pady=2)
            self.summary[key] = e

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=self.NUM + 1, sticky="w",
                padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate ACV", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=5, column=0, columnspan=self.NUM + 1,
                   sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        vals = []
        for ci in range(self.NUM):
            try:
                m1 = (get_float(self.cells[("tray_spec", ci)], 0)
                      - get_float(self.cells[("tray", ci)], 0))
                m2 = (get_float(self.cells[("tray_pass", ci)], 0)
                      - get_float(self.cells[("tray2", ci)], 0))
                m3 = (get_float(self.cells[("tray_ret", ci)], 0)
                      - get_float(self.cells[("tray3", ci)], 0))
                set_val(self.cells[("m1", ci)], f"{m1:.1f}")
                set_val(self.cells[("m2", ci)], f"{m2:.1f}")
                set_val(self.cells[("m3", ci)], f"{m3:.1f}")
                set_val(self.cells[("m2m3", ci)], f"{m2+m3:.1f}")
                acv = (m2 / m1 * 100) if m1 else 0
                set_val(self.cells[("acv_pct", ci)], f"{acv:.1f}")
                if m1 > 0:
                    vals.append(acv)
            except Exception:
                pass
        if vals:
            set_val(self.summary["mean"], f"{sum(vals)/len(vals):.1f}")
            sv = sorted(vals)
            n = len(sv)
            med = sv[n // 2] if n % 2 else (sv[n // 2 - 1] + sv[n // 2]) / 2
            set_val(self.summary["median"], f"{med:.1f}")

    def _save_log(self):
        m = self.summary["mean"].get()
        md = self.summary["median"].get()
        if not m:
            return messagebox.showwarning("Warning", "Calculate first.")
        # Share with coarse properties
        self.app.session["agg_acv_mean"] = m
        ts = self.save_to_log("ACV", {"mean": m, "median": md})
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"ACV mean={m} @ {ts}")

    def _clear(self):
        for e in list(self.cells.values()) + list(self.summary.values()):
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")


# =====================================================================
# 6. TFV
# =====================================================================
class TfvTab(BaseTab):
    tab_label = "🔟 TFV"
    log_category = "agg_tfv"
    log_columns = (("acv_400", "ACV 400kN", 90), ("tfv", "TFV", 90))

    FORCES = ["50 kN", "100 kN", "150 kN", "400 kN", "Control"]
    FRACTIONS = AcvTab.FRACTIONS

    def build(self):
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Ten Percent Fines Value (TFV)  10% FACT",
                   "CML TEST 2.7,  ref. BS 812 : Part 111 : 1990",
                   row=0, colspan=len(self.FORCES) + 1)

        frac_f = section(inner, "Fraction Tested / Separating Sieve",
                         1, 0, colspan=3)
        for ri, (frac, sep, note) in enumerate(self.FRACTIONS):
            bg_c = "#fff3cd" if note else "#f8f8f8"
            tk.Label(frac_f, text=frac, bg=bg_c,
                     font=("Times New Roman", 12,
                           "bold" if note else "normal"),
                     relief=tk.RIDGE, width=16, anchor="w").grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(frac_f, text=sep, bg=bg_c,
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=12, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            if note:
                tk.Label(frac_f, text=note, bg="#fff3cd",
                         font=("Times New Roman", 12, "bold"),
                         relief=tk.RIDGE, width=14).grid(
                    row=ri, column=2, padx=1, pady=1)

        data_f = section(inner, "Test Data by Applied Force",
                         2, 0, colspan=len(self.FORCES) + 1)
        tfv_rows = [
            ("Specimen reference", "spec_ref", False),
            ("Applied Force  F", "force", False),
            ("Mass of tray + test specimen (g)", "tray_spec", False),
            ("Mass of tray alone (g)", "tray", False),
            ("Mass of tray alone (g)", "tray2", False),
            ("Mass of material passing sep. sieve  M₂ (g)", "m2", True),
            ("Mass of original test specimen  M₁ (g)", "m1", True),
            ("Mass of tray + material passing sep. sieve (g)",
             "tray_pass", False),
            ("Mass of tray + material retained (g)", "tray_ret", False),
            ("Mass of tray alone (g)", "tray3", False),
            ("Mass of material retained  M₃ (g)", "m3", True),
            ("M₂ + M₃  (check vs M₁)", "m2m3", True),
            ("Percentage Fines (%)  M₂/M₁ × 100", "pct_fines", True),
        ]
        tk.Label(data_f, text="Parameter", bg=C.HDR,
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=38, anchor="w").grid(row=0, column=0, padx=1, pady=1,
                                             sticky="ew")
        for ci, f in enumerate(self.FORCES):
            tk.Label(data_f, text=f, bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=10, anchor="center").grid(
                row=0, column=ci + 1, padx=1, pady=1)

        self.cells = {}
        for ri, (lbl, key, is_c) in enumerate(tfv_rows):
            tk.Label(data_f, text=lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12,
                           "bold" if key == "pct_fines" else "normal"),
                     relief=tk.RIDGE, width=38, anchor="w",
                     wraplength=280, justify="left").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            for ci in range(len(self.FORCES)):
                e = calc_entry(data_f, w=10) if is_c else entry(data_f, w=10)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e
        for ci, f in enumerate(self.FORCES):
            self.cells[("force", ci)].insert(0, f)

        sum_f = section(inner, "Results", 3, 0, colspan=2)
        self.summary = {}
        for ri, (lbl, key) in enumerate([
                ("ACV (for F = 400 kN)  %", "acv_400"),
                ("10% Fines Value (from chart)  kN", "tfv")]):
            tk.Label(sum_f, text=lbl, bg="#fffacd",
                     font=("Times New Roman", 12, "bold"),
                     relief=tk.RIDGE, width=34, anchor="w").grid(
                row=ri, column=0, padx=1, pady=2, sticky="ew")
            e = calc_entry(sum_f, w=14)
            e.grid(row=ri, column=1, padx=4, pady=2)
            self.summary[key] = e

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=len(self.FORCES) + 1,
                sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=5, column=0, columnspan=len(self.FORCES) + 1,
                   sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        for ci in range(len(self.FORCES)):
            try:
                m1 = (get_float(self.cells[("tray_spec", ci)], 0)
                      - get_float(self.cells[("tray", ci)], 0))
                m2 = (get_float(self.cells[("tray_pass", ci)], 0)
                      - get_float(self.cells[("tray2", ci)], 0))
                m3 = (get_float(self.cells[("tray_ret", ci)], 0)
                      - get_float(self.cells[("tray3", ci)], 0))
                set_val(self.cells[("m1", ci)], f"{m1:.1f}")
                set_val(self.cells[("m2", ci)], f"{m2:.1f}")
                set_val(self.cells[("m3", ci)], f"{m3:.1f}")
                set_val(self.cells[("m2m3", ci)], f"{m2+m3:.1f}")
                pf = (m2 / m1 * 100) if m1 else 0
                set_val(self.cells[("pct_fines", ci)], f"{pf:.1f}")
                if ci == 3:
                    set_val(self.summary["acv_400"], f"{pf:.1f}")
            except Exception:
                pass

    def _save_log(self):
        acv400 = self.summary["acv_400"].get()
        tfv = self.summary["tfv"].get()
        if not acv400:
            return messagebox.showwarning("Warning", "Calculate first.")
        ts = self.save_to_log("TFV", {"acv_400": acv400, "tfv": tfv})
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for e in list(self.cells.values()) + list(self.summary.values()):
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")
        for ci, f in enumerate(self.FORCES):
            self.cells[("force", ci)].insert(0, f)


# =====================================================================
# 7. AIV
# =====================================================================
class AivTab(BaseTab):
    tab_label = "⚡ AIV"
    log_category = "agg_aiv"
    log_columns = (("mean", "Mean AIV", 90), ("median", "Median", 90))

    NUM = 4
    FRACTIONS = [("14 - 10 mm", "2.36 mm", "STANDARD"),
                 ("10 - 6.3 mm", "1.70 mm", ""),
                 ("6.3 - 5.0 mm", "1.18 mm", ""),
                 ("5.0 - 3.35 mm", "850 µm", ""),
                 ("3.35 - 2.36 mm", "600 µm", "")]

    def build(self):
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Aggregate Impact Value  AIV",
                   "CML TEST 2.8,  ref. BS 812 : Part 112 : 1990",
                   row=0, colspan=self.NUM + 1)

        cond_f = section(inner, "Test Condition", 1, 0, colspan=3)
        self.aiv_cond_var = tk.StringVar(value="DRY")
        for txt in ("DRY", "SOAKED"):
            ttk.Radiobutton(cond_f, text=txt, variable=self.aiv_cond_var,
                            value=txt).pack(side=tk.LEFT, padx=10, pady=4)

        frac_f = section(inner, "Fraction Tested / Separating Sieve",
                         2, 0, colspan=3)
        for ri, (frac, sep, note) in enumerate(self.FRACTIONS):
            bg_c = "#fff3cd" if note else "#f8f8f8"
            tk.Label(frac_f, text=frac, bg=bg_c,
                     font=("Times New Roman", 12,
                           "bold" if note else "normal"),
                     relief=tk.RIDGE, width=16, anchor="w").grid(
                row=ri, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(frac_f, text=sep, bg=bg_c,
                     font=("Times New Roman", 12), relief=tk.RIDGE,
                     width=12, anchor="center").grid(
                row=ri, column=1, padx=1, pady=1)
            if note:
                tk.Label(frac_f, text=note, bg="#fff3cd",
                         font=("Times New Roman", 12, "bold"),
                         relief=tk.RIDGE, width=14).grid(
                    row=ri, column=2, padx=1, pady=1)

        data_f = section(inner, "Test Data", 3, 0, colspan=self.NUM + 1)
        aiv_rows = [
            ("Specimen reference", "spec_ref", False),
            ("Number of blows (normally 15)  n", "blows", False),
            ("Mass of tray + test specimen (g)", "tray_spec", False),
            ("Mass of tray alone (g)", "tray", False),
            ("Mass of original test specimen  M₁ (g)", "m1", True),
            ("Mass of tray + material passing sep. sieve (g)",
             "tray_pass", False),
            ("Mass of tray alone (g)", "tray2", False),
            ("Mass of material passing sep. sieve  M₂ (g)", "m2", True),
            ("Mass of tray + material retained (g)", "tray_ret", False),
            ("Mass of tray alone (g)", "tray3", False),
            ("Mass of material retained  M₃ (g)", "m3", True),
            ("M₂ + M₃  (check vs M₁)", "m2m3", True),
            ("AIV (%) DRY  = M₂/M₁ × 100", "aiv_dry", True),
            ("AIV (%) SOAKED  = (M₂/M₁) × (15/n) × 100", "aiv_soak", True),
        ]
        tk.Label(data_f, text="Parameter", bg=C.HDR,
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=42, anchor="w").grid(row=0, column=0, padx=1, pady=1,
                                             sticky="ew")
        for ci in range(self.NUM):
            tk.Label(data_f, text=str(ci + 1), bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=10, anchor="center").grid(
                row=0, column=ci + 1, padx=1, pady=1)

        self.cells = {}
        for ri, (lbl, key, is_c) in enumerate(aiv_rows):
            is_result = key in ("aiv_dry", "aiv_soak")
            bg_c = "#fff2cc" if is_result else "#f8f8f8"
            tk.Label(data_f, text=lbl, bg=bg_c,
                     font=("Times New Roman", 12,
                           "bold" if is_result else "normal"),
                     relief=tk.RIDGE, width=42, anchor="w",
                     wraplength=300, justify="left").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            for ci in range(self.NUM):
                e = calc_entry(data_f, w=10) if is_c else entry(data_f, w=10)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e
        for ci in range(self.NUM):
            self.cells[("blows", ci)].insert(0, "15")

        sum_f = section(inner, "Summary", 4, 0, colspan=2)
        self.summary = {}
        for ri, (lbl, key) in enumerate([("AIV – mean value (%)", "mean"),
                                          ("AIV – median value (%)", "median")]):
            tk.Label(sum_f, text=lbl, bg="#fffacd",
                     font=("Times New Roman", 12, "bold"),
                     relief=tk.RIDGE, width=30, anchor="w").grid(
                row=ri, column=0, padx=1, pady=2, sticky="ew")
            e = calc_entry(sum_f, w=12)
            e.grid(row=ri, column=1, padx=4, pady=2)
            self.summary[key] = e

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=5, column=0, columnspan=self.NUM + 1, sticky="w",
                padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate AIV", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=6, column=0, columnspan=self.NUM + 1,
                   sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        vals = []
        for ci in range(self.NUM):
            try:
                m1 = (get_float(self.cells[("tray_spec", ci)], 0)
                      - get_float(self.cells[("tray", ci)], 0))
                m2 = (get_float(self.cells[("tray_pass", ci)], 0)
                      - get_float(self.cells[("tray2", ci)], 0))
                m3 = (get_float(self.cells[("tray_ret", ci)], 0)
                      - get_float(self.cells[("tray3", ci)], 0))
                n = float(self.cells[("blows", ci)].get() or 15)
                set_val(self.cells[("m1", ci)], f"{m1:.1f}")
                set_val(self.cells[("m2", ci)], f"{m2:.1f}")
                set_val(self.cells[("m3", ci)], f"{m3:.1f}")
                set_val(self.cells[("m2m3", ci)], f"{m2+m3:.1f}")
                aiv_dry = (m2 / m1 * 100) if m1 else 0
                aiv_soak = (m2 / m1 * (15 / n) * 100) if (m1 and n) else 0
                set_val(self.cells[("aiv_dry", ci)], f"{aiv_dry:.1f}")
                set_val(self.cells[("aiv_soak", ci)], f"{aiv_soak:.1f}")
                if m1 > 0:
                    vals.append(aiv_dry if self.aiv_cond_var.get() == "DRY"
                                else aiv_soak)
            except Exception:
                pass
        if vals:
            set_val(self.summary["mean"], f"{sum(vals)/len(vals):.1f}")
            sv = sorted(vals)
            n2 = len(sv)
            med = sv[n2 // 2] if n2 % 2 else (sv[n2 // 2 - 1] + sv[n2 // 2]) / 2
            set_val(self.summary["median"], f"{med:.1f}")

    def _save_log(self):
        m = self.summary["mean"].get()
        if not m:
            return messagebox.showwarning("Warning", "Calculate first.")
        self.app.session["agg_aiv_mean"] = m
        ts = self.save_to_log("AIV", {"mean": m,
                                       "median": self.summary["median"].get(),
                                       "condition": self.aiv_cond_var.get()})
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"AIV mean={m} @ {ts}")

    def _clear(self):
        for e in list(self.cells.values()) + list(self.summary.values()):
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")
        for ci in range(self.NUM):
            self.cells[("blows", ci)].insert(0, "15")


# =====================================================================
# 8. LAA
# =====================================================================
class LaaTab(BaseTab):
    tab_label = "🔄 LAA"
    log_category = "agg_laa"
    log_columns = (("laa_pct", "LAA %", 80),)

    GRADINGS = ["A", "B", "C", "D"]
    GRAD_ROWS = [
        ("37.5 mm", "25.0 mm", "1250 ± 25", "1250 ± 25", "—", "—"),
        ("25.0 mm", "19.0 mm", "1250 ± 25", "1250 ± 25", "—", "—"),
        ("19.0 mm", "12.5 mm", "1250 ± 10", "—", "—", "—"),
        ("12.5 mm", "9.5 mm", "1250 ± 10", "2500 ± 10", "—", "—"),
        ("9.5 mm", "6.3 mm", "—", "—", "2500 ± 10", "—"),
        ("6.3 mm", "4.75 mm", "—", "—", "2500 ± 10", "—"),
        ("4.75 mm", "2.36 mm", "—", "—", "—", "5000 ± 10"),
        ("Total", "", "5000 ± 10", "5000 ± 10", "5000 ± 10", "5000 ± 10"),
    ]

    def build(self):
        _, inner, _ = scrolled_frame(self)
        cml_header(inner, "Los Angeles Abrasion Test (LAA)",
                   "CML TEST 2.9,  ref. ASTM C 539 - 89",
                   row=0, colspan=len(self.GRADINGS) + 1)

        grad_f = section(inner, "Grading – Mass of Indicated Sizes (g)",
                         1, 0, colspan=6)
        for ci, h_txt in enumerate(["Passing", "Retained on", "A", "B", "C", "D"]):
            tk.Label(grad_f, text=h_txt, bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=12, anchor="center").grid(
                row=0, column=ci, padx=1, pady=1, sticky="ew")
        for ri, row_vals in enumerate(self.GRAD_ROWS):
            for ci, val in enumerate(row_vals):
                bg_c = "#f8f8f8" if ci < 2 else "#e8f4f8"
                tk.Label(grad_f, text=val, bg=bg_c,
                         font=("Times New Roman", 12), relief=tk.RIDGE,
                         width=12, anchor="center").grid(
                    row=ri + 1, column=ci, padx=1, pady=1, sticky="ew")

        data_f = section(inner, "Test Data", 2, 0,
                         colspan=len(self.GRADINGS) + 1)
        laa_rows = [
            ("Sample reference", "sample_ref", False),
            ("Sample description", "sample_desc", False),
            ("Grading used", "grading", False),
            ("Mass of sample before test  m₁ (g)", "m1", False),
            ("Mass retained on sieve size 1.70 mm  m₂ (g)", "m2", False),
            ("Mass passing sieve size 1.70 mm  (m₁ - m₂) (g)", "m1_m2", True),
            ("LAA Value  ((m₁ - m₂) / m₁) × 100  %", "laa_pct", True),
        ]
        tk.Label(data_f, text="Parameter", bg=C.HDR,
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=42, anchor="w").grid(row=0, column=0, padx=1, pady=1,
                                             sticky="ew")
        for ci, g in enumerate(self.GRADINGS):
            tk.Label(data_f, text=f"Grading {g}", bg=C.HDR,
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=12, anchor="center").grid(
                row=0, column=ci + 1, padx=1, pady=1)

        self.cells = {}
        for ri, (lbl, key, is_c) in enumerate(laa_rows):
            is_result = key == "laa_pct"
            bg_c = "#fff2cc" if is_result else "#f8f8f8"
            tk.Label(data_f, text=lbl, bg=bg_c,
                     font=("Times New Roman", 12,
                           "bold" if is_result else "normal"),
                     relief=tk.RIDGE, width=42, anchor="w",
                     wraplength=310, justify="left").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            for ci, g in enumerate(self.GRADINGS):
                e = calc_entry(data_f, w=12) if is_c else entry(data_f, w=12)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.cells[(key, ci)] = e
        for ci, g in enumerate(self.GRADINGS):
            self.cells[("grading", ci)].insert(0, g)

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=3, column=0, columnspan=len(self.GRADINGS) + 1,
                sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate LAA", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=4, column=0, columnspan=len(self.GRADINGS) + 1,
                   sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _calc(self):
        for ci in range(len(self.GRADINGS)):
            try:
                m1 = float(self.cells[("m1", ci)].get())
                m2 = float(self.cells[("m2", ci)].get())
                diff = m1 - m2
                laa = (diff / m1 * 100) if m1 else 0
                set_val(self.cells[("m1_m2", ci)], f"{diff:.1f}")
                set_val(self.cells[("laa_pct", ci)], f"{laa:.1f}")
            except Exception:
                pass

    def _save_log(self):
        data = {}
        for ci, g in enumerate(self.GRADINGS):
            v = self.cells[("laa_pct", ci)].get()
            if v:
                data[f"laa_{g}"] = v
                data["laa_pct"] = v
        if not data:
            return messagebox.showwarning("Warning", "Calculate first.")
        ts = self.save_to_log("LAA", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")
        for ci, g in enumerate(self.GRADINGS):
            self.cells[("grading", ci)].insert(0, g)


# =====================================================================
# 9. FINE AGGREGATES
# =====================================================================
class FineAggregateTab(BaseTab):
    tab_label = "🏖️ Fine Aggregates"
    log_category = "fine_aggregate"
    log_columns = (("desig", "Designation", 80), ("p5", "% Pass 5mm", 70),
                   ("p236", "% Pass 2.36mm", 80),
                   ("p0600", "% Pass 600µm", 85),
                   ("p0150", "% Pass 150µm", 85))

    FA_SIEVES = ["8.0", "6.3", "5.0", "4.0", "3.35", "2.36", "2.0",
                 "1.18", "0.600", "0.300", "0.150", "Pan"]
    FA_SIEVE_LABELS = ["8.0 mm", "6.3 mm", "5.0 mm", "4.0 mm", "3.35 mm",
                       "2.36 mm", "2.0 mm", "1.18 mm", "600 µm", "300 µm",
                       "150 µm", "Pan (<150µm)"]
    FA_SIEVE_NUMS = [8.0, 6.3, 5.0, 4.0, 3.35, 2.36, 2.0, 1.18, 0.600,
                     0.300, 0.150, 0.063]

    FA_LIMITS = {
        "0/3": [("8.0 mm", 8.00, None, None), ("6.3 mm", 6.30, None, None),
                ("5.0 mm", 5.00, None, None), ("4.0 mm", 4.00, None, None),
                ("3.35 mm", 3.35, 98, 100), ("2.36 mm", 2.36, 80, 99),
                ("2.0 mm", 2.00, 72, 94), ("1.18 mm", 1.18, 44, 74),
                ("600 µm", 0.600, 22, 48), ("300 µm", 0.300, 10, 28),
                ("150 µm", 0.150, 2, 12), ("Pan", 0.063, None, None)],
        "0/4": [("8.0 mm", 8.00, None, None), ("6.3 mm", 6.30, None, None),
                ("5.0 mm", 5.00, 98, 100), ("4.0 mm", 4.00, 90, 100),
                ("3.35 mm", 3.35, None, None), ("2.36 mm", 2.36, 70, 99),
                ("2.0 mm", 2.00, None, None), ("1.18 mm", 1.18, 38, 68),
                ("600 µm", 0.600, 18, 48), ("300 µm", 0.300, 8, 28),
                ("150 µm", 0.150, 2, 14), ("Pan", 0.063, None, None)],
        "0/6": [("8.0 mm", 8.00, 100, 100), ("6.3 mm", 6.30, 98, 100),
                ("5.0 mm", 5.00, 85, 99), ("4.0 mm", 4.00, None, None),
                ("3.35 mm", 3.35, None, None), ("2.36 mm", 2.36, 60, 98),
                ("2.0 mm", 2.00, None, None), ("1.18 mm", 1.18, 30, 70),
                ("600 µm", 0.600, 15, 52), ("300 µm", 0.300, 5, 32),
                ("150 µm", 0.150, 2, 18), ("Pan", 0.063, None, None)],
    }

    def build(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5,
                              sashrelief=tk.RAISED, bg="#aaa")
        pane.pack(fill=tk.BOTH, expand=True)
        left_outer = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left_outer, minsize=300, width=700)
        _, inner, _ = scrolled_frame(left_outer)
        right_outer = tk.Frame(pane, bg="white")
        pane.add(right_outer, minsize=300)
        _, right_frame, _ = scrolled_frame(right_outer)

        tk.Label(right_frame, text="Fine Aggregate Gradation Curve",
                 bg="#2c3e50", fg="white",
                 font=("Times New Roman", 12, "bold"), pady=6).pack(fill=tk.X)
        des_strip = tk.Frame(right_frame, bg="#ecf0f1", pady=4)
        des_strip.pack(fill=tk.X)
        tk.Label(des_strip, text="Designation:", bg="#ecf0f1",
                 font=("Times New Roman", 12, "bold")).pack(side=tk.LEFT, padx=8)
        self.fa_desig_var = tk.StringVar(value="0/6")
        des_cb = ttk.Combobox(des_strip, textvariable=self.fa_desig_var,
                              values=["0/3", "0/4", "0/6"], state="readonly",
                              width=8)
        des_cb.pack(side=tk.LEFT, padx=4)
        des_cb.bind("<<ComboboxSelected>>", self._on_fa_designation_changed)
        tk.Label(des_strip, text="← changes limits & checks", bg="#ecf0f1",
                 font=("Times New Roman", 12, "italic"),
                 fg="#666").pack(side=tk.LEFT, padx=6)
        self.fa_chart_frame = tk.Frame(right_frame, bg="white")
        self.fa_chart_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        top = section(inner, "Fine Aggregate Test  "
                             "(BS EN 12620 / PD 6682-1 Annex D)",
                      0, 0, colspan=4)
        fa_hdr_fields = [("Date:", "fa_date", 14), ("Operator:", "fa_op", 20),
                         ("Sample No.:", "fa_sno", 16),
                         ("Technician:", "fa_tech", 20),
                         ("Sample Source:", "fa_src", 20),
                         ("Checked By:", "fa_check", 20),
                         ("Mass Dry (g):", "fa_mass", 12),
                         ("Designation:", "fa_desig", 10),
                         ("Approved By:", "fa_approved", 20)]
        self.fa_info = {}
        for ri, (lt, key, w) in enumerate(fa_hdr_fields):
            r, c = divmod(ri, 2)
            tk.Label(top, text=lt, bg="#f0f0f0",
                     font=("Times New Roman", 12, "bold")).grid(
                row=r, column=c * 2, sticky="w", padx=4, pady=2)
            e = entry(top, w=w)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="w")
            self.fa_info[key] = e
        self.fa_info["fa_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.fa_info["fa_mass"].insert(0, "1000")

        des_f = section(inner, "Designation / Standard Limits", 1, 0, colspan=4)
        tk.Label(des_f, text="Select designation:", bg="#f0f0f0",
                 font=("Times New Roman", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=6, pady=4)
        des_cb2 = ttk.Combobox(des_f, textvariable=self.fa_desig_var,
                               values=["0/3", "0/4", "0/6"], state="readonly",
                               width=8)
        des_cb2.grid(row=0, column=1, padx=4, pady=4)
        des_cb2.bind("<<ComboboxSelected>>", self._on_fa_designation_changed)

        sieve_f = section(inner, "Sieve Analysis Data", 2, 0, colspan=4)
        fa_cols = ["Sieve", "Mass Retained (g)", "% Retained", "% Passing",
                   "BS Lower (%)", "BS Upper (%)", "PASS/FAIL"]
        for ci, h in enumerate(fa_cols):
            hdr(sieve_f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)

        self.fa_cells = {}
        self._fa_sieves = self.FA_SIEVES
        self._fa_sieve_nums = self.FA_SIEVE_NUMS
        self._fa_sieve_lbls = self.FA_SIEVE_LABELS

        for ri, (sv, sv_lbl) in enumerate(zip(self.FA_SIEVES,
                                              self.FA_SIEVE_LABELS)):
            tk.Label(sieve_f, text=sv_lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=11, anchor="w").grid(row=ri + 1, column=0,
                                                 padx=1, pady=1, sticky="ew")
            rd = {}
            e_ret = entry(sieve_f, w=13)
            e_ret.grid(row=ri + 1, column=1, padx=1, pady=1, sticky="ew")
            rd["retained"] = e_ret
            for key, col in [("ret", 2), ("pass", 3)]:
                e = calc_entry(sieve_f, w=10)
                e.grid(row=ri + 1, column=col, padx=1, pady=1, sticky="ew")
                rd[key] = e
            lo_lbl = tk.Label(sieve_f, text="—", bg="#dce6f1",
                              font=("Times New Roman", 12), relief=tk.RIDGE,
                              width=10, anchor="center")
            lo_lbl.grid(row=ri + 1, column=4, padx=1, pady=1, sticky="ew")
            hi_lbl = tk.Label(sieve_f, text="—", bg="#dce6f1",
                              font=("Times New Roman", 12), relief=tk.RIDGE,
                              width=10, anchor="center")
            hi_lbl.grid(row=ri + 1, column=5, padx=1, pady=1, sticky="ew")
            pf_lbl = tk.Label(sieve_f, text="—", bg="#fffacd",
                              font=("Times New Roman", 12, "bold"),
                              relief=tk.RIDGE, width=8, anchor="center")
            pf_lbl.grid(row=ri + 1, column=6, padx=1, pady=1, sticky="ew")
            rd["pf"] = pf_lbl
            rd["lo_lbl"] = lo_lbl
            rd["hi_lbl"] = hi_lbl
            rd["bs_lo"] = None
            rd["bs_hi"] = None
            self.fa_cells[sv] = rd

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Check vs Standard",
                   command=self._check_vs_bs).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Plot Gradation",
                   command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=4, column=0, columnspan=4, sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

        self._on_fa_designation_changed()

    def _on_fa_designation_changed(self, _=None):
        desig = self.fa_desig_var.get()
        limits = self.FA_LIMITS.get(desig, [])
        lim_by_lbl = {row[0]: (row[2], row[3]) for row in limits}
        for sv, rd in self.fa_cells.items():
            sv_lbl = self._fa_sieve_lbls[self._fa_sieves.index(sv)]
            lo, hi = lim_by_lbl.get(sv_lbl, (None, None))
            rd["bs_lo"] = lo
            rd["bs_hi"] = hi
            rd["lo_lbl"].config(text=str(lo) if lo is not None else "—",
                                 bg="#dce6f1" if lo is not None else "#f0f0f0")
            rd["hi_lbl"].config(text=str(hi) if hi is not None else "—",
                                 bg="#dce6f1" if hi is not None else "#f0f0f0")
            rd["pf"].config(text="—", bg="#fffacd", fg="black")
        e = self.fa_info.get("fa_desig")
        if e:
            e.delete(0, tk.END)
            e.insert(0, desig)

    def _calc(self):
        try:
            total = float(self.fa_info["fa_mass"].get())
        except ValueError:
            return messagebox.showerror("Error", "Enter valid total dry mass.")
        cum_ret = 0
        self._fa_data = {"sieve": [], "pct_pass": []}
        for sv, sv_num in zip(self._fa_sieves, self._fa_sieve_nums):
            rd = self.fa_cells[sv]
            act = get_float(rd["retained"], 0)
            cum_ret += act
            pct_ret = (cum_ret / total * 100) if total > 0 else 0
            pct_pass = max(0, 100 - pct_ret)
            set_val(rd["ret"], f"{pct_ret:.1f}")
            set_val(rd["pass"], f"{pct_pass:.1f}")
            self._fa_data["sieve"].append(sv_num)
            self._fa_data["pct_pass"].append(pct_pass)
        self._check_vs_bs(silent=True)
        self._plot()

    def _check_vs_bs(self, silent=False):
        all_pass = True
        for sv, rd in self.fa_cells.items():
            lo, hi = rd.get("bs_lo"), rd.get("bs_hi")
            pct = get_float(rd["pass"])
            pf = rd["pf"]
            if lo is None or hi is None or pct is None:
                pf.config(text="N/A", bg="#f0f0f0", fg="#888")
                continue
            passed = lo <= pct <= hi
            pf.config(text="PASS" if passed else "FAIL",
                      bg="#27ae60" if passed else "#e74c3c", fg="white")
            if not passed:
                all_pass = False
        if not silent:
            messagebox.showinfo("Check Complete",
                                "✅ ALL PASS" if all_pass
                                else "⚠️  Some sieves outside BS limits")

    def _plot(self):
        if not hasattr(self, "_fa_data") or not self._fa_data["sieve"]:
            return
        sieves = [s for s in self._fa_data["sieve"] if s > 0.05]
        passes = [p for s, p in zip(self._fa_data["sieve"],
                                     self._fa_data["pct_pass"]) if s > 0.05]
        if not sieves:
            return
        for w in self.fa_chart_frame.winfo_children():
            w.destroy()
        fig, ax = plt.subplots(figsize=(7, 5.5), dpi=96)
        fig.patch.set_facecolor("white")
        ax.semilogx(sieves, passes, "b-o", markersize=7, linewidth=2,
                    label="Test Results", zorder=5)
        desig = self.fa_desig_var.get()
        limits = self.FA_LIMITS.get(desig, [])
        bs_sievs = [r[1] for r in limits if r[2] is not None and r[1] > 0.05]
        bs_lo_pts = [r[2] for r in limits if r[2] is not None and r[1] > 0.05]
        bs_hi_pts = [r[3] for r in limits if r[3] is not None and r[1] > 0.05]
        if bs_sievs:
            ax.semilogx(bs_sievs, bs_hi_pts, "g--", linewidth=1.5,
                        label=f"{desig} Upper Limit")
            ax.semilogx(bs_sievs, bs_lo_pts, "r--", linewidth=1.5,
                        label=f"{desig} Lower Limit")
            ax.fill_between(bs_sievs, bs_lo_pts, bs_hi_pts, alpha=0.10,
                            color="green", label="BS Envelope")
        ax.set_xlabel("Sieve Size (mm)", fontsize=10)
        ax.set_ylabel("Cumulative % Passing", fontsize=10)
        ax.set_title(f"Fine Aggregate Gradation – Designation {desig}\n"
                     f"(BS EN 12620 / PD 6682-1 Annex D)",
                     fontsize=10, fontweight="bold")
        ax.set_xlim([0.05, 12])
        ax.set_ylim([0, 105])
        ax.set_yticks(range(0, 110, 10))
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(fontsize=9, loc="upper left")
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, self.fa_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def _save_log(self):
        if not hasattr(self, "_fa_data") or not self._fa_data["sieve"]:
            self._calc()
        sno = self.fa_info.get("fa_sno").get()
        desig = self.fa_desig_var.get()
        pct_map = dict(zip(self._fa_data["sieve"], self._fa_data["pct_pass"]))
        data = {
            "desig": desig,
            "p5": f"{pct_map.get(5.0, 0):.1f}",
            "p236": f"{pct_map.get(2.36, 0):.1f}",
            "p0600": f"{pct_map.get(0.600, 0):.1f}",
            "p0150": f"{pct_map.get(0.150, 0):.1f}",
            "sample": sno,
            "source": self.fa_info.get("fa_src").get(),
        }
        ts = self.save_to_log(f"{sno or 'Fine Agg'} ({desig})", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Fine aggregate {desig} stored at {ts}")

    def _clear(self):
        for sv, rd in self.fa_cells.items():
            for k in ("retained", "ret", "pass"):
                rd[k].config(state="normal")
                rd[k].delete(0, tk.END)
                if rd[k].cget("bg") == C.CALC:
                    rd[k].config(state="readonly")
            rd["pf"].config(text="—", bg="#fffacd", fg="black")
        for w in self.fa_chart_frame.winfo_children():
            w.destroy()


# =====================================================================
# 10. AGGREGATE REPORT (coarse grading vs BS 882)
# =====================================================================
class AggregateReportTab(BaseTab):
    tab_label = "🪨 Aggregate Report"
    log_category = "agg_report"

    BS_LIMITS = {
        "10/14": [("20", "100"), ("14", "85-100"), ("10", "0-50"),
                  ("5", "0-10"), ("2.36", "-")],
        "20/5": [("20", "90-100"), ("14", "40-80"), ("10", "30-60"),
                 ("5", "0-10"), ("2.36", "-")],
        "14/5": [("20", "100"), ("14", "90-100"), ("10", "50-85"),
                 ("5", "0-10"), ("2.36", "-")],
        "40/5": [("20", "35-70"), ("14", "25-55"), ("10", "10-40"),
                 ("5", "0-5"), ("2.36", "-")],
        "40mm": [("20", "0-25"), ("14", "-"), ("10", "0-25"), ("5", "-"),
                 ("2.36", "-")],
        "20mm": [("20", "85-100"), ("14", "0-70"), ("10", "0-25"),
                 ("5", "0-5"), ("2.36", "-")],
        "14mm": [("20", "100"), ("14", "85-100"), ("10", "0-50"),
                 ("5", "0-10"), ("2.36", "-")],
        "10mm": [("20", "100"), ("14", "100"), ("10", "85-100"),
                 ("5", "0-25"), ("2.36", "0-5")],
        "5mm": [("20", "-"), ("14", "-"), ("10", "100"), ("5", "45-100"),
                ("2.36", "0-30")],
        "14-20mm": [("40", "100"), ("28", "85-99"), ("20", "0-25"),
                    ("14", "0-5")],
        "20-40mm": [("50", "100"), ("40", "85-99"), ("28", "0-25"),
                    ("20", "0-5")],
        "0/3 (Fine)": [("3.35", "98-100"), ("2.36", "80-99"), ("2.0", "72-94"),
                       ("1.18", "44-74"), ("0.600", "22-48"),
                       ("0.300", "10-28"), ("0.150", "2-12")],
        "0/4 (Fine)": [("5.0", "98-100"), ("4.0", "90-100"),
                       ("2.36", "70-99"), ("1.18", "38-68"),
                       ("0.600", "18-48"), ("0.300", "8-28"),
                       ("0.150", "2-14")],
        "0/6 (Fine)": [("8.0", "100"), ("6.3", "98-100"), ("5.0", "85-99"),
                       ("2.36", "60-98"), ("1.18", "30-70"),
                       ("0.600", "15-52"), ("0.300", "5-32"),
                       ("0.150", "2-18")],
    }

    MAX_COLS = 8

    def build(self):
        _, inner, _ = scrolled_frame(self)

        banner = tk.Frame(inner, bg="#2c3e50", pady=4)
        banner.grid(row=0, column=0, columnspan=6, sticky="ew")
        tk.Label(banner, text="⚡  Coarse Aggregate Grading – BS 812-103.1 / "
                              "BS 882:1992  │  Enter % passing results below, "
                              "then Generate PDF",
                 bg="#2c3e50", fg="#ecf0f1",
                 font=("Times New Roman", 12, "bold")).pack(side=tk.LEFT,
                                                              padx=10)

        hdr_f = section(inner, "Report Header", 1, 0, colspan=6)
        hdr_fields = [("Date:", "ag_date", 14),
                      ("Project / Description:", "ag_project", 30),
                      ("Sample Reference:", "ag_sample", 20),
                      ("Location:", "ag_location", 30),
                      ("Aggregate Type/Size:", "ag_type", 20),
                      ("Technologist:", "ag_tech", 20),
                      ("Resident Engineer:", "ag_eng", 20),
                      ("Remarks:", "ag_remarks", 50)]
        self.ag_hdr = {}
        for ri, (lt, key, w) in enumerate(hdr_fields):
            r, c = divmod(ri, 2)
            tk.Label(hdr_f, text=lt, bg="#f0f0f0",
                     font=("Times New Roman", 12, "bold")).grid(
                row=r, column=c * 2, sticky="w", padx=6, pady=2)
            e = entry(hdr_f, w=w)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="w")
            self.ag_hdr[key] = e
        self.ag_hdr["ag_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

        sel_f = section(inner, "Test Configuration", 2, 0, colspan=6)
        tk.Label(sel_f, text="Aggregate Type for Analysis:", bg="#f0f0f0",
                 font=("Times New Roman", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=6, pady=4)
        self.ag_type_var = tk.StringVar(value="10/14")
        type_opts = list(self.BS_LIMITS.keys())
        ttk.Combobox(sel_f, textvariable=self.ag_type_var,
                     values=type_opts, state="readonly", width=16).grid(
            row=0, column=1, padx=4)
        tk.Label(sel_f, text="Selects BS/PD standard limits — sieve columns "
                             "update automatically",
                 bg="#f0f0f0", font=("Times New Roman", 12, "italic")).grid(
            row=0, column=2, sticky="w", padx=6)

        res_f = section(inner, "Grading Specifications as per British "
                               "Standards & Test Results",
                        3, 0, colspan=6)
        self._ag_sieve_hdrs = []
        self.ag_sieve_lbls = {}
        self.ag_result_entries = {}
        self.ag_pf_lbls = {}

        tk.Label(res_f, text="SIEVE SIZE mm", bg="#f8f8f8",
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=18, anchor="w").grid(row=1, column=0, padx=1, pady=1,
                                             sticky="ew")
        tk.Label(res_f, text="BRITISH STANDARDS", bg="#dce6f1",
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=18, anchor="w").grid(row=2, column=0, padx=1, pady=1,
                                             sticky="ew")
        tk.Label(res_f, text="RESULTS", bg="#e2efda",
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=18, anchor="w").grid(row=3, column=0, padx=1, pady=1,
                                             sticky="ew")
        tk.Label(res_f, text="PASS / FAIL", bg="#fffacd",
                 font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                 width=18, anchor="w").grid(row=4, column=0, padx=1, pady=1,
                                             sticky="ew")

        for ci in range(self.MAX_COLS):
            lbl_hdr = tk.Label(res_f, text="—", bg="#f8f8f8",
                               font=("Times New Roman", 12, "bold"),
                               relief=tk.RIDGE, width=10, anchor="center")
            lbl_hdr.grid(row=1, column=ci + 1, padx=1, pady=1, sticky="ew")
            self._ag_sieve_hdrs.append(lbl_hdr)
            lbl_bs = tk.Label(res_f, text="—", bg="#dce6f1",
                              font=("Times New Roman", 12), relief=tk.RIDGE,
                              width=10, anchor="center")
            lbl_bs.grid(row=2, column=ci + 1, padx=1, pady=1, sticky="ew")
            self.ag_sieve_lbls[ci] = lbl_bs
            e = entry(res_f, w=10, bg="#e2efda")
            e.grid(row=3, column=ci + 1, padx=1, pady=1, sticky="ew")
            self.ag_result_entries[ci] = e
            lbl_pf = tk.Label(res_f, text="—", bg="#fffacd",
                              font=("Times New Roman", 12, "bold"),
                              relief=tk.RIDGE, width=10, anchor="center")
            lbl_pf.grid(row=4, column=ci + 1, padx=1, pady=1, sticky="ew")
            self.ag_pf_lbls[ci] = lbl_pf

        self._agg_result_sieves = []
        self.ag_type_var.trace_add("write", lambda *_: self._update_bs_limits())
        self._update_bs_limits()

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=6, sticky="w", padx=6, pady=8)
        ttk.Button(bf, text="Check Results vs BS", command=self._check_vs_bs,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(bf, text="📄📝 Export Aggregate Report (PDF)",
                   command=self._export_pdf,
                   style="Success.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(bf, text="Clear Results",
                   command=self._clear).pack(side=tk.LEFT, padx=6)

    def _update_bs_limits(self):
        agg_type = self.ag_type_var.get()
        rows = self.BS_LIMITS.get(agg_type, [])
        n = len(rows)
        self._agg_result_sieves = [r[0] for r in rows]
        for ci in range(self.MAX_COLS):
            hdr_lbl = self._ag_sieve_hdrs[ci]
            bs_lbl = self.ag_sieve_lbls[ci]
            pf_lbl = self.ag_pf_lbls[ci]
            e = self.ag_result_entries[ci]
            if ci < n:
                sv_lbl, bs_spec = rows[ci]
                hdr_lbl.config(text=sv_lbl, bg="#f8f8f8", fg="black")
                bs_lbl.config(text=bs_spec if bs_spec else "—",
                              bg="#dce6f1", fg="black")
                e.config(state="normal", bg="#e2efda")
            else:
                hdr_lbl.config(text="", bg="#e8e8e8")
                bs_lbl.config(text="", bg="#e8e8e8")
                e.config(state="disabled", bg="#e8e8e8")
            pf_lbl.config(text="—", bg="#fffacd", fg="black")

    def _check_vs_bs(self):
        agg_type = self.ag_type_var.get()
        rows = self.BS_LIMITS.get(agg_type, [])
        all_pass = True
        for ci, (sv_lbl, bs_spec) in enumerate(rows):
            spec = bs_spec or "-"
            res_str = self.ag_result_entries[ci].get().strip()
            lbl = self.ag_pf_lbls[ci]
            if spec == "-" or not res_str:
                lbl.config(text="N/A", bg="#f0f0f0", fg="#888")
                continue
            try:
                res = float(res_str)
                if "-" in spec and not spec.startswith("-"):
                    parts = spec.replace("–", "-").split("-")
                    lo, hi = float(parts[0]), float(parts[1])
                    passed = lo <= res <= hi
                else:
                    passed = (res == float(spec))
                lbl.config(text="PASS" if passed else "FAIL",
                           bg="#27ae60" if passed else "#e74c3c", fg="white")
                if not passed:
                    all_pass = False
            except (ValueError, IndexError):
                lbl.config(text="—", bg="#fffacd", fg="black")
        messagebox.showinfo("Check Complete",
                            "✅ ALL PASS" if all_pass
                            else "⚠️  Some values outside BS limits")

    def _clear(self):
        for ci in range(self.MAX_COLS):
            e = self.ag_result_entries[ci]
            e.config(state="normal")
            e.delete(0, tk.END)
        for lbl in self.ag_pf_lbls.values():
            lbl.config(text="—", bg="#fffacd", fg="black")

    def _export_pdf(self):
        fn = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
            initialfile="Aggregate_Grading_Report.pdf")
        if not fn:
            return
        self._generate_pdf(fn)

    def _generate_pdf(self, fn):
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer)
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors as C2
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

        def sty(size=9, bold=False, align=TA_CENTER, color=None):
            return ParagraphStyle("_", fontSize=size, fontName="Times-Bold" if bold else "Times-Roman",
                                   alignment=align, textColor=color or C2.black, leading=size + 3, spaceAfter=0)

        def dl(t):
            return Paragraph(str(t) if t else "", sty(9, align=TA_LEFT))

        def dc(t):
            return Paragraph(str(t) if t else "", sty(9, align=TA_CENTER))

        doc = SimpleDocTemplate(fn, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=16 * mm, bottomMargin=16 * mm)
        W = A4[0] - 40 * mm
        story = []
        date_str = self.ag_hdr["ag_date"].get() or datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Date: {date_str}", sty(9, align=TA_RIGHT)))
        story.append(Spacer(1, 4 * mm))
        story.append(Paragraph("LABORATORY TEST REPORT",
                                sty(14, bold=True, align=TA_CENTER)))
        story.append(Spacer(1, 4 * mm))
        intro = ("When determined in accordance with <b>BS 812-103.1</b> using "
                 "test sieves of the sizes given in <b>table 3 of BS 882:1992</b>, "
                 "complying with BS 410, full tolerance, the grading of the "
                 "coarse aggregate shall be within the appropriate limits given " "in table below.")
        story.append(Paragraph(intro, sty(9, align=TA_JUSTIFY)))
        story.append(Spacer(1, 5 * mm))

        agg_type = self.ag_type_var.get()
        sample = self.ag_hdr["ag_sample"].get()
        is_fine = "Fine" in agg_type
        title_prefix = "FINE AGGREGATES" if is_fine else "COARSE AGGREGATES"
        story.append(Paragraph(
            f"ANALYSIS OF {title_prefix} ({agg_type})" +
            (f"  –  Sample: {sample}" if sample else ""),
            sty(11, bold=True, align=TA_CENTER)))
        story.append(Spacer(1, 4 * mm))

        rows_def = self.BS_LIMITS.get(agg_type, [])
        sieves = [r[0] for r in rows_def]
        bs_specs = [r[1] for r in rows_def]
        results = [self.ag_result_entries[ci].get().strip()
                   for ci in range(len(rows_def))]

        n = len(sieves)
        cw_res = [W * 0.28] + [W * 0.72 / n] * n if n else [W]
        std_name = "PD 6682-1 Annex D" if is_fine else "BS 882:1992 / BS EN 12620"
        res_data = [ [Paragraph(f"<b>GRADING SPECIFICATIONS  –  {std_name}</b>",
                       sty(9, bold=True, align=TA_CENTER))] + [""] * n, [dl("SIEVE SIZE mm")] + [dc(sv) for sv in sieves],
            [dl("BRITISH STANDARDS")] + [dc(spec) for spec in bs_specs], [dl("RESULTS")] + [dc(r) for r in results], ]
        pf_row = [dl("PASS / FAIL")]
        for ci, (spec, res_str) in enumerate(zip(bs_specs, results)):
            pf = ""
            if spec and spec != "-" and res_str:
                try:
                    res_v = float(res_str)
                    if "-" in spec and not spec.startswith("-"):
                        lo, hi = [float(x) for x in spec.replace("–", "-").split("-")]
                        pf = "PASS" if lo <= res_v <= hi else "FAIL"
                    else:
                        pf = "PASS" if res_v == float(spec) else "FAIL"
                except (ValueError, IndexError):
                    pf = ""
            pf_row.append(Paragraph(
                f"<b>{pf}</b>",
                sty(8, bold=True,
                    color=C2.HexColor("#27ae60") if pf == "PASS"
                    else C2.HexColor("#c0392b") if pf == "FAIL"
                    else C2.black)))
        res_data.append(pf_row)

        res_tbl = Table(res_data, colWidths=cw_res)
        res_tbl.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.2, C2.black),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, C2.HexColor("#aaa")),
            ("SPAN", (0, 0), (-1, 0)),
            ("BACKGROUND", (0, 0), (-1, 0), C2.HexColor("#1f3864")),
            ("TEXTCOLOR", (0, 0), (-1, 0), C2.white),
            ("BACKGROUND", (0, 1), (-1, 1), C2.HexColor("#f2f2f2")),
            ("BACKGROUND", (0, 2), (-1, 2), C2.HexColor("#dce6f1")),
            ("BACKGROUND", (0, 3), (-1, 3), C2.HexColor("#e2efda")),
            ("BACKGROUND", (0, 4), (-1, 4), C2.HexColor("#fffacd")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 1), (0, -1), "Times-Bold"),
            ("LEFTPADDING", (0, 0), (0, -1), 6),
        ]))
        story.append(res_tbl)
        story.append(Spacer(1, 6 * mm))

        remarks = self.ag_hdr["ag_remarks"].get().strip()
        story.append(Paragraph("REMARKS" + "." * 120, sty(8, align=TA_LEFT)))
        if remarks:
            story.append(Paragraph(remarks, sty(9, align=TA_LEFT)))
        story.append(Paragraph("." * 150, sty(8, align=TA_LEFT)))
        story.append(Spacer(1, 8 * mm))

        tech = self.ag_hdr["ag_tech"].get() or "Project Material Technologist"
        eng = self.ag_hdr["ag_eng"].get() or "Resident Engineer"
        sig_data = [
            [dl(tech), dl(eng)],
            [Paragraph("." * 44, sty(9, align=TA_LEFT)),
             Paragraph("." * 44, sty(9, align=TA_LEFT))],
            [Paragraph("Date………………………………………………", sty(9, align=TA_LEFT)),
             Paragraph("Date………………………………………………", sty(9, align=TA_LEFT))],
        ]
        sig = Table(sig_data, colWidths=[W / 2, W / 2])
        sig.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("TOPPADDING", (0, 1), (-1, 1), 6),
            ("TOPPADDING", (0, 2), (-1, 2), 8),
        ]))
        story.append(sig)

        doc.build(story)
        messagebox.showinfo("Success", f"Report saved:\n{fn}")
        if messagebox.askyesno("Open", "Open report now?"):
            webbrowser.open(fn)


# 11. COARSE AGGREGATE PROPERTIES
class CoarsePropertiesTab(BaseTab):
    tab_label = "📋 Coarse Agg. Properties"
    log_category = "coarse_properties"
    log_columns = (("laa_0", "LAA 0/3 (%)", 80),
                   ("laa_2", "LAA 10/14 (%)", 90),
                   ("acv_0", "ACV 0/3 (%)", 80),
                   ("project", "Project", 120))

    NOM_SIZES = ["0/3", "6/10", "10/14", "14/20"]
    ROW_DEFS = [
        ("STONE TYPE", "stone_type", False),
        ("SAMPLE NO", "sample_no", False),
        ("NOMINAL SIZE (mm)", "nominal_size", False),
        ("A.C.V (%)", "acv", False),
        ("L.A.A (%)", "laa", False),
        ("ALD", "ald", False),
        ("SPECIFIC GRAVITY\n(S.S.D.)", "sg_ssd", False),
        ("WATER ABSORPTION\n(%)", "wa", False),
        ("FLAKINESS INDEX\n(%)", "fi", False),
    ]

    def build(self):
        banner = tk.Frame(self, bg="#1a5276", pady=4)
        banner.pack(fill=tk.X)
        tk.Label(banner, text="⚡  Values auto-fill from Aggregate Tests tab as "
                              "you calculate each test.  Select the Nominal "
                              "Size before calculating.",
                 bg="#1a5276", fg="#d6eaf8",
                 font=("Times New Roman", 12, "bold")).pack(side=tk.LEFT,
                                                              padx=10)
        self.cp_autofill_lbl = tk.Label(banner, text="No auto-fill yet",
                                         bg="#1a5276", fg="#a9cce3",
                                         font=("Times New Roman", 12, "italic"))
        self.cp_autofill_lbl.pack(side=tk.RIGHT, padx=10)

        _, inner, _ = scrolled_frame(self)

        top = section(inner, "Coarse Aggregate Properties Report – Lab Test Report",
                      0, 0, colspan=6)
        cp_hdr = [("Date:", "cp_date", 14),
                  ("Project Engineer:", "cp_eng", 24),
                  ("Stone to be used for:", "cp_project", 40),
                  ("Technologist:", "cp_tech", 24),
                  ("Quarry Location/Name:", "cp_quarry", 40),
                  ("Checked By:", "cp_check", 24),
                  ("Sample Location:", "cp_loc", 40),
                  ("Approved By:", "cp_appr", 24)]
        self.cp_hdr = {}
        for ri, (lt, key, w) in enumerate(cp_hdr):
            r, c = divmod(ri, 2)
            tk.Label(top, text=lt, bg="#f0f0f0",
                     font=("Times New Roman", 12, "bold")).grid(
                row=r, column=c * 2, sticky="w", padx=6, pady=2)
            e = entry(top, w=w)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="w")
            self.cp_hdr[key] = e
        self.cp_hdr["cp_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

        tbl_f = section(inner, "Test Results by Nominal Size", 1, 0, colspan=6)
        hdr(tbl_f, "Parameter", w=22, row=0, column=0, sticky="ew", padx=1, pady=2)
        for ci, ns in enumerate(self.NOM_SIZES):
            hdr(tbl_f, ns, w=12, row=0, column=ci + 1, sticky="ew", padx=1, pady=2)

        self.cp_cells = {}
        for ri, (row_lbl, row_key, is_calc) in enumerate(self.ROW_DEFS):
            tk.Label(tbl_f, text=row_lbl, bg="#f8f8f8",
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=22, anchor="w", wraplength=160,
                     justify="left").grid(row=ri + 1, column=0, padx=1, pady=1,
                                           sticky="ew")
            for ci in range(len(self.NOM_SIZES)):
                e = calc_entry(tbl_f, w=10) if is_calc else entry(tbl_f, w=10)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.cp_cells[(row_key, ci)] = e
        for ci, ns in enumerate(self.NOM_SIZES):
            self.cp_cells[("nominal_size", ci)].insert(0, ns)

        rem_f = section(inner, "Remarks", 2, 0, colspan=6)
        self.cp_remarks = tk.Text(rem_f, height=3, width=80,
                                   font=("Times New Roman", 12))
        self.cp_remarks.pack(fill=tk.X, padx=4, pady=4)

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=3, column=0, columnspan=6, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="🔄 Refresh from Saved Tests",
                   command=self._refresh_from_db,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="📄📝 Export (PDF)", command=self._export_pdf,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

        log_f = tk.Frame(inner, bg="#f0f0f0")
        log_f.grid(row=4, column=0, columnspan=6, sticky="ew", padx=6, pady=4)
        _, self.log_tree = self.make_stored_panel(log_f)
        self.add_delete_bar(log_f, self.log_tree)

    def _refresh_from_db(self):
        TEST_MAP = [ ("Crushing", "acv", "crushing_value", ".1f"),
            ("Abrasion", "laa", "abrasion_value", ".1f"),("Impact", "acv", "abrasion_value", ".1f"),
            ("Flakiness", "fi", "crushing_value", ".1f"), ("Gravity", "sg_ssd", "specific_gravity", ".3f"),
            ("Absorption", "wa", "water_absorption", ".2f"), ("Absorption", "sg_ssd", "specific_gravity", ".3f"),]
        try:
            cur = self.db.cursor()
            cur.execute("""SELECT test_name, sample_id, crushing_value,
                                  abrasion_value, specific_gravity,
                                  water_absorption, notes
                           FROM aggregate_tests ORDER BY date DESC""")
            rows = cur.fetchall()
        except Exception as e:
            return messagebox.showerror("DB Error", str(e))

        filled = 0
        for tn, sid, cv, av, sg, wa, notes in rows:
            tn = tn or ""
            nom_col = None
            for ni, ns in enumerate(self.NOM_SIZES):
                if ns in (sid or "") or ns in (notes or ""):
                    nom_col = ni
                    break
            if nom_col is None:
                for ni, ns in enumerate(self.NOM_SIZES):
                    clean = ns.replace("/", "").replace("-", "")
                    if clean in (sid or "").replace("/", "").replace("-", ""):
                        nom_col = ni
                        break
            if nom_col is None:
                continue
            for keyword, row_key, db_col, fmt in TEST_MAP:
                if keyword not in tn:
                    continue
                val_map = {"crushing_value": cv, "abrasion_value": av,
                           "specific_gravity": sg, "water_absorption": wa}
                val = val_map.get(db_col, 0) or 0
                if val == 0:
                    continue
                e = self.cp_cells.get((row_key, nom_col))
                if e is not None:
                    e.delete(0, tk.END)
                    e.insert(0, format(float(val), fmt))
                    filled += 1
                sno_e = self.cp_cells.get(("sample_no", nom_col))
                if sno_e and not sno_e.get() and sid:
                    sno_e.delete(0, tk.END)
                    sno_e.insert(0, sid)
        ts = datetime.now().strftime("%H:%M:%S")
        msg = f"Refreshed {filled} value(s) from saved tests  [{ts}]"
        if hasattr(self, "cp_autofill_lbl"):
            self.cp_autofill_lbl.config(text=msg)
        messagebox.showinfo("Refreshed",
                            f"{filled} value(s) loaded from saved aggregate tests.")

    def _save_log(self):
        data = {}
        for (key, ci), e in self.cp_cells.items():
            data[f"{key}_{ci}"] = e.get()
        data["project"] = self.cp_hdr.get("cp_project").get()
        ts = self.save_to_log(self.cp_hdr.get("cp_quarry").get() or "Coarse Agg",
                               data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Coarse properties saved at {ts}")

    def _export_pdf(self):
        fn = filedialog.asksaveasfilename(
            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")],
            initialfile="Coarse_Aggregate_Properties.pdf")
        if not fn:
            return
        self._generate_pdf(fn)

    def _generate_pdf(self, fn):
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                        Paragraph, Spacer)
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors as C2
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        doc = SimpleDocTemplate(fn, pagesize=A4, leftMargin=15 * mm,
                                 rightMargin=15 * mm, topMargin=12 * mm,
                                 bottomMargin=12 * mm)
        W = A4[0] - 30 * mm

        def sty(sz=9, bold=False, align=TA_CENTER, color=None):
            return ParagraphStyle("_", fontSize=sz,
                                   fontName="Times-Bold" if bold else "Times-Roman",
                                   alignment=align,
                                   textColor=color or C2.black,
                                   leading=sz + 3, spaceAfter=0)

        def d(t, sz=8, al=TA_CENTER, bold=False):
            return Paragraph(str(t) if t else "",
                             sty(sz, bold=bold, align=al))

        DARK = C2.HexColor("#1f3864")
        LGREY = C2.HexColor("#f2f2f2")
        LBLUE = C2.HexColor("#dce6f1")
        WHITE = C2.white

        story = []
        story.append(Paragraph(f"Date: {self.cp_hdr['cp_date'].get()}",
                                sty(9, bold=True, align=TA_RIGHT)))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("LABORATORY TEST REPORT",
                                sty(14, bold=True, align=TA_CENTER)))
        story.append(Spacer(1, 4 * mm))

        for key, label in [("cp_project", "Stone to be used for"),
                           ("cp_quarry", "Quarry Location/Name"),
                           ("cp_loc", "Sample Location")]:
            val = self.cp_hdr[key].get()
            if val:
                story.append(Paragraph(f"<b>{label}:</b>  {val}",
                                        sty(9, align=TA_LEFT)))
        story.append(Spacer(1, 4 * mm))

        nom = self.NOM_SIZES
        cw = [W * 0.38] + [W * 0.62 / len(nom)] * len(nom)
        hrow = [Paragraph("<b>TEST RESULTS FOR COARSE AGGREGATES</b>",
                          sty(8, bold=True, align=TA_CENTER))] + [d("")] * len(nom)
        h2row = [d("Parameter", bold=True)] + [d(n, bold=True) for n in nom]
        rows = [hrow, h2row]
        for row_lbl, row_key, _ in self.ROW_DEFS:
            row = [d(row_lbl, al=TA_LEFT)]
            for ci in range(len(nom)):
                row.append(d(self.cp_cells[(row_key, ci)].get()))
            rows.append(row)
        t = Table(rows, colWidths=cw)
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.2, DARK),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, C2.HexColor("#bbb")),
            ("SPAN", (0, 0), (-1, 0)),
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("BACKGROUND", (0, 1), (-1, 1), LBLUE),
            ("ROWBACKGROUNDS", (0, 2), (-1, -1), [WHITE, LGREY]),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 2), (0, -1), "LEFT"),
            ("FONTNAME", (0, 2), (0, -1), "Times-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 6 * mm))

        rem = self.cp_remarks.get("1.0", tk.END).strip()
        if rem:
            story.append(Paragraph(f"<b>Remarks:</b>  {rem}",
                                    sty(9, align=TA_LEFT)))
            story.append(Spacer(1, 4 * mm))

        tech = self.cp_hdr.get("cp_tech").get() or "Project Material Technologist"
        eng = self.cp_hdr.get("cp_eng").get() or "Resident Engineer"
        sig = Table([
            [d(tech, bold=True, al=TA_LEFT), d(eng, bold=True, al=TA_LEFT)],
            [Paragraph("." * 44, sty(9, align=TA_LEFT)),
             Paragraph("." * 44, sty(9, align=TA_LEFT))],
            [Paragraph("Date………………………………………………", sty(9, align=TA_LEFT)),
             Paragraph("Date………………………………………………", sty(9, align=TA_LEFT))],
        ], colWidths=[W / 2, W / 2])
        sig.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
            ("TOPPADDING", (0, 1), (-1, 2), 6),
            ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
        ]))
        story.append(sig)

        doc.build(story)
        messagebox.showinfo("Success", f"Report saved:\n{fn}")
        if messagebox.askyesno("Open", "Open report now?"):
            webbrowser.open(fn)

    def _clear(self):
        for (key, ci), e in self.cp_cells.items():
            if key != "nominal_size":
                e.config(state="normal")
                e.delete(0, tk.END)
                if e.cget("bg") == C.CALC:
                    e.config(state="readonly")
        self.cp_remarks.delete("1.0", tk.END)