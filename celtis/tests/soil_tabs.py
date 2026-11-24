
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ..config import C, FONT
from ..core import soil as calc
from ..ui.base_tab import BaseTab
from ..ui.widgets import (entry, calc_entry, hdr, section, scrolled_frame, set_val, get_float)


# 1. ATTERBERG LIMITS
class AtterbergTab(BaseTab):
    tab_label = "Atterberg Limits"
    log_category = "atterberg"
    log_columns = (("ll", "LL (%)", 60), ("pl", "PL (%)", 60), ("pi", "PI", 50), ("ls", "LS (%)", 60))

    def build(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED, bg="#aaa")
        pane.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left, minsize=1000)
        _, inner, _ = scrolled_frame(left)

        right = tk.Frame(pane, bg="white")
        pane.add(right, minsize=450)
        _, rinner, _ = scrolled_frame(right)
        tk.Label(rinner, text="Cone Penetration vs Moisture Content",
                 bg="#2c3e50", fg="white", font=(FONT, 12, "bold"), pady=4).pack(fill=tk.X)
        self.chart = tk.Frame(rinner, bg="white")
        self.chart.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._build_info(inner)
        self._build_table(inner)
        self._build_summary(inner)
        self._build_shrinkage(inner)
        self._build_buttons(inner)
        self._build_log(inner)

    def _build_info(self, parent):
        f = section(parent, "Determination of Atterberg Limits of a Soil",
                    0, 0, colspan=6)
        fields = [("Date:", "att_date"), ("Operator:", "att_operator"),
                  ("Sample No.:", "att_sampleno"), ("Technician:", "att_tech"), ("Location:", "att_location"), ("Checked By:", "att_checked"),
                  ("Sample Description:", "att_desc"), ("Approved By:", "att_approved"), ("Soil Condition:", "att_condition")]
        self.info = {}
        for ri, (lt, key) in enumerate(fields):
            r, c = divmod(ri, 3)
            tk.Label(f, text=lt, bg="#f0f0f0",
                     font=(FONT, 12, "bold")).grid(row=r, column=c * 2,  sticky="w", padx=2, pady=1)
            e = entry(f, w=12)
            e.grid(row=r, column=c * 2 + 1, padx=2, pady=1, sticky="w")
            self.info[key] = e
        self.info["att_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

    def _build_table(self, parent):
        f = section(parent, "Liquid Limit – Cone Penetrometer Method", 1, 0, colspan=6)
        tk.Label(f, text="Test No.", font=(FONT, 12, "bold"),
                 bg="#2c3e50", fg="white").grid(row=0, column=0, sticky="ew", padx=0, pady=1, ipady=2)
        for ti, lab in enumerate(["1", "2", "3", "4", "PL"]):
            tk.Label(f, text=lab, font=(FONT, 12, "bold"),
                     bg="#2c3e50", fg="white").grid(row=0, column=1 + ti * 2, columnspan=2, sticky="ew", padx=0, pady=1, ipady=2)

        rows = [("Cone Penetration (mm)", "cone"), ("Tin No.", "tin_no"), ("Wt of wet soil+Tin (g)", "wt_wet"),
                ("Wt of dry soil+Tin (g)", "wt_dry"), ("Wt of Tin (g)", "wt_tin"),("Wt of moisture (g)", "wt_moist"), 
                ("Wt of dry soil (g)", "wt_drysoil"), ("Moisture content (%)", "mc"),("Average", "avg")]
        calc_rows = {"wt_moist", "wt_drysoil", "mc"}
        self.cells = {}
        for ri, (label, key) in enumerate(rows):
            tk.Label(f, text=label, bg="#f8f8f8", font=(FONT, 12),
                     anchor="w", relief=tk.RIDGE).grid( row=ri + 1, column=0, sticky="ew", padx=0, pady=1, ipady=1)
            is_calc = key in calc_rows
            for ci in range(10):
                if key == "avg" or is_calc:
                    e = tk.Entry(f, font=(FONT, 12), justify="center", bg=C.CALC, state="readonly", relief=tk.RIDGE, width=7)
                else:
                    e = tk.Entry(f, font=(FONT, 12), justify="center", bg="white", relief=tk.RIDGE, width=7)
                if key == "cone" and ci == 8:
                    e.config(state="disabled", bg="#d8d8d8")
                e.grid(row=ri + 1, column=ci + 1, sticky="ew", padx=0, pady=1)
                self.cells[(key, ci)] = e

    def _build_summary(self, parent):
        f = section(parent, "Atterberg Limit Tests Summary", 3, 0, colspan=3)
        for ri, (lt, key) in enumerate([("Liquid Limit", "sum_ll"), ("Plastic Limit", "sum_pl"), ("Plasticity Index", "sum_pi"), 
                                      ("Linear Shrinkage", "sum_ls")]):
            tk.Label(f, text=lt, font=(FONT, 12, "bold"), bg="#f0f0f0",
                     anchor="w").grid(row=ri, column=0, sticky="w", padx=2, pady=1)
            e = calc_entry(f, w=15)
            e.grid(row=ri, column=1, padx=2, pady=1)
            setattr(self, key, e)

    def _build_shrinkage(self, parent):
        f = section(parent, "Linear Shrinkage", 3, 3, colspan=3)
        labels = ["Trough No.:", "Initial Length (A) mm:", "Oven Dry Length (B) mm:", "Linear Shrinkage % = 100(1-B/A):"]
        for i, lt in enumerate(labels):
            tk.Label(f, text=lt, bg="#f0f0f0", font=(FONT, 12)).grid(
                row=i, column=0, sticky="w", padx=2, pady=1)
        self.ls_trough = entry(f, w=12)
        self.ls_trough.grid(row=0, column=1)
        self.ls_initial = entry(f, w=12)
        self.ls_initial.grid(row=1, column=1)
        self.ls_final = entry(f, w=12)
        self.ls_final.grid(row=2, column=1)
        self.ls_result = calc_entry(f, w=12)
        self.ls_result.grid(row=3, column=1)

    def _build_buttons(self, parent):
        bf = tk.Frame(parent, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=6, sticky="w", padx=4, pady=4)
        ttk.Button(bf, text="Calculate All", command=self._calculate, style="Primary.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Plot Cone Chart", command=self._plot).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Save", command=self._save_soil).pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log, style="Success.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=2)

    def _build_log(self, parent):
        f = tk.Frame(parent, bg="#f0f0f0")
        _, self.log_tree = self.make_stored_panel(f)
        self.add_delete_bar(f, self.log_tree)
        f.grid(row=5, column=0, columnspan=6, sticky="ew", padx=4, pady=2)

    def _calculate(self):
        for ci in range(10):
            ww = get_float(self.cells[("wt_wet", ci)])
            wd = get_float(self.cells[("wt_dry", ci)])
            wt = get_float(self.cells[("wt_tin", ci)])
            if None in (ww, wd, wt):
                continue
            mc = calc.moisture_content(ww, wd, wt)
            if mc is None:
                continue
            set_val(self.cells[("wt_moist", ci)], round(ww - wd, 2))
            set_val(self.cells[("wt_drysoil", ci)], round(wd - wt, 2))
            set_val(self.cells[("mc", ci)], f"{mc:.1f}")
        cones, mcs = [], []
        for pair in range(4):
            v1 = get_float(self.cells[("mc", pair * 2)])
            v2 = get_float(self.cells[("mc", pair * 2 + 1)])
            vals = [v for v in (v1, v2) if v is not None]
            if not vals:
                continue
            avg = sum(vals) / len(vals)
            set_val(self.cells[("avg", pair * 2)], f"{avg:.1f}")
            cp = get_float(self.cells[("cone", pair * 2)])
            if cp is None:
                continue
            cones.append(cp)
            mcs.append(avg)
        ll, coeffs = calc.liquid_limit_from_cone(cones, mcs)
        if ll is not None:
            set_val(self.sum_ll, f"{ll:.1f}")
        self._cones, self._mcs, self._coeffs, self._ll = cones, mcs, coeffs, ll

        pl_vals = [v for v in (get_float(self.cells[("mc", 8)]), get_float(self.cells[("mc", 9)])) if v is not None]
        pl = sum(pl_vals) / len(pl_vals) if pl_vals else None
        if pl is not None:
            set_val(self.cells[("avg", 8)], f"{pl:.1f}")
            set_val(self.sum_pl, f"{pl:.1f}")
        pi = calc.plasticity_index(ll, pl)
        if pi is not None:
            set_val(self.sum_pi, f"{pi:.1f}")
        A = get_float(self.ls_initial)
        B = get_float(self.ls_final)
        if A and B:
            ls = calc.linear_shrinkage(A, B)
            if ls is not None:
                set_val(self.ls_result, f"{ls:.1f}")
                set_val(self.sum_ls, f"{ls:.1f}")

    def _plot(self):
        cones = getattr(self, "_cones", [])
        mcs = getattr(self, "_mcs", [])
        if not cones:
            self._calculate()
            cones = getattr(self, "_cones", [])
            mcs = getattr(self, "_mcs", [])
        if not cones:
            messagebox.showwarning("Warning", "Need at least 1 data point.")
            return
        for w in self.chart.winfo_children():
            w.destroy()
        fig, ax = plt.subplots(figsize=(7, 6), dpi=100)
        fig.patch.set_facecolor("white")
        ll = getattr(self, "_ll", mcs[0] if mcs else 0)
        if len(cones) >= 2:
            coeffs = getattr(self, "_coeffs", None)
            if coeffs is None:
                c_arr, m_arr = zip(*zip(cones, mcs))
                coeffs = np.polyfit(c_arr, m_arr, 1)
            c_range = np.linspace(min(cones) - 2, max(cones) + 2, 200)
            ax.plot(np.polyval(coeffs, c_range), c_range, "b-", linewidth=1)
        ax.plot(mcs, cones, "bs", markersize=7, zorder=5)
        ax.axhline(20, color="gray", linestyle="--", linewidth=0.8)
        ax.axvline(ll, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xlabel("MOISTURE CONTENT (%)")
        ax.set_ylabel("CONE PENETRATION (mm)")
        ax.set_title(f"Liquid Limit = {ll:.1f}%", fontsize=10, fontweight="bold")
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        c = FigureCanvasTkAgg(fig, self.chart)
        c.draw()
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def _save_soil(self):
        ll = get_float(self.sum_ll)
        pl = get_float(self.sum_pl)
        if ll is None or pl is None:
            return messagebox.showwarning("Warning", "Calculate first!")
        pi = ll - pl
        self.db.execute(
            """INSERT INTO soil_tests (test_name, sample_id, date,
               moisture_content, liquid_limit, plastic_limit, plasticity_index,
               soil_classification, technician, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            ("Atterberg Limits", self.info["att_sampleno"].get(),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, ll, pl, pi,
             f"PI={pi:.1f}", self.info["att_tech"].get(), ""))
        self.db.commit()

    def _save_log(self):
        ll = get_float(self.sum_ll)
        pl = get_float(self.sum_pl)
        ls = get_float(self.ls_result)
        sno = self.info["att_sampleno"].get()
        data = {"ll": f"{ll:.1f}" if ll else "", "pl": f"{pl:.1f}" if pl else "", "pi": f"{ll - pl:.1f}" if (ll and pl) else "",
                "ls": f"{ls:.1f}" if ls else "", "sample": sno, "technician": self.info["att_tech"].get()}
        ts = self.save_to_log(sno or "Atterberg", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"Stored at {ts}")

    def _clear(self):
        for (key, ci), e in self.cells.items():
            try:
                e.config(state="normal")
                e.delete(0, tk.END)
                if key == "cone" and ci == 8:
                    e.config(state="disabled", bg="#d8d8d8")
                elif e.cget("bg") == C.CALC:
                    e.config(state="readonly")
            except Exception:
                pass
        for attr in ("sum_ll", "sum_pl", "sum_pi", "sum_ls", "ls_result"):
            e = getattr(self, attr)
            e.config(state="normal")
            e.delete(0, tk.END)
            e.config(state="readonly")
        for k, e in self.info.items():
            if k != "att_date":
                e.delete(0, tk.END)
        for w in (self.ls_trough, self.ls_initial, self.ls_final):
            w.delete(0, tk.END)
        for w in self.chart.winfo_children():
            w.destroy()

# 2. COMPACTION (T99/T180)
class CompactionTab(BaseTab):
    tab_label = "Compaction (T99/T180)"
    log_category = "compaction"
    log_columns = (("mdd", "MDD (kg/m³)", 90), ("omc", "OMC (%)", 70), ("sample", "Sample", 120))

    def build(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED, bg="#aaa")
        pane.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left, minsize=1000, width=700)
        _, inner, _ = scrolled_frame(left)

        right = tk.Frame(pane, bg="white")
        pane.add(right, minsize=1000)
        _, rinner, _ = scrolled_frame(right)
        tk.Label(rinner, text="Dry Density / Moisture Content Curve",
                 bg="#2c3e50", fg="white", font=(FONT, 12, "bold"),  pady=6).pack(fill=tk.X)

        readout = tk.Frame(rinner, bg="#ecf0f1", pady=4)
        readout.pack(fill=tk.X)
        tk.Label(readout, text="MDD (kg/m³):", bg="#ecf0f1",
                 font=(FONT, 12, "bold")).grid(row=0, column=0, padx=10, pady=2)
        self.mdd_r = calc_entry(readout, w=10)
        self.mdd_r.grid(row=0, column=1, padx=4)
        tk.Label(readout, text="OMC (%):", bg="#ecf0f1",
                 font=(FONT, 12, "bold")).grid(row=0, column=2, padx=10, pady=2)
        self.omc_r = calc_entry(readout, w=10)
        self.omc_r.grid(row=0, column=3, padx=4)
        self.chart = tk.Frame(rinner, bg="white")
        self.chart.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._build_info(inner)
        self._build_table(inner)
        self._build_buttons(inner)
        self._build_log(inner)

    def _build_info(self, parent):
        f = section(parent, "Dry Density / Moisture Content Relationship (T99/T180)", 0, 0, colspan=8)
        fields = [("Location:", "comp_location"), ("Date:", "comp_date"), ("Sample Description:", "comp_desc"),
                  ("Rammer Used:", "comp_rammer"), ("Sample No.:", "comp_sampleno"), ("Technician:", "comp_tech"),
                  ("Operator:", "comp_operator"), ("Checked By:", "comp_checked"), ("Compaction Type:", "comp_type")]
        self.info = {}
        for ri, (lt, key) in enumerate(fields):
            r, c = divmod(ri, 3)
            tk.Label(f, text=lt, bg="#f0f0f0",
                     font=(FONT, 12, "bold")).grid(
                row=r, column=c * 2, sticky="w", padx=4, pady=2)
            e = entry(f, w=16)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="w")
            self.info[key] = e
        self.info["comp_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

    def _build_table(self, parent):
        f = section(parent, "Test Data", 1, 0, colspan=8)
        for ci, h in enumerate(["Parameter", "Units", "Point 1", "Point 2", "Point 3", "Point 4", "Point 5"]):
            hdr(f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)

        row_defs = [ ("Water to added", "ml", "water", False),("Mould No.", "No.", "mould_no", False), ("Wt of Wet soil+Mould", "g", "wt_wet_mould", False),
            ("Wt of Mould", "g", "wt_mould", False), ("Wt of Wet soil", "g", "wt_wet", True), ("Volume of Mould", "cm³", "vol", False),
            ("Bulk Density of soil", "g/cm³", "bulk_dens", True), ("Dry Density of soil", "Kg/m³", "dry_dens", True), ("Tin No.", "No", "tin_no", False),
            ("Wt of Wet soil+Tin", "g", "wt_wet_tin", False), ("Wt of Dry soil+Tin", "g", "wt_dry_tin", False), ("Wt of Tin", "g", "wt_tin", False),
            ("Wt of Moisture", "g", "wt_moist", True), ("Wt of Dry soil", "g", "wt_drysoil", True),  ("Moisture Content", "%", "mc", True)]
        self.cells = {}
        for ri, (lbl_, unit, key, is_calc) in enumerate(row_defs):
            tk.Label(f, text=lbl_, bg="#f8f8f8", font=(FONT, 12),
                     anchor="w", width=22, relief=tk.RIDGE).grid(
                row=ri + 1, column=0, sticky="ew", padx=1, pady=1)
            tk.Label(f, text=unit, bg="#f8f8f8", font=(FONT, 12),
                     width=6, relief=tk.RIDGE).grid(
                row=ri + 1, column=1, sticky="ew", padx=1, pady=1)
            for pi in range(5):
                e = calc_entry(f, w=9) if is_calc else entry(f, w=9)
                e.grid(row=ri + 1, column=pi + 2, padx=1, pady=1, sticky="ew")
                self.cells[(key, pi)] = e
        for pi in range(5):
            self.cells[("water", pi)].insert(0, str(50 * (pi + 1)))
            self.cells[("vol", pi)].insert(0, "1000")

    def _build_buttons(self, parent):
        bf = tk.Frame(parent, bg="#f0f0f0")
        bf.grid(row=2, column=0, columnspan=8, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="Calculate",
                   command=self._calc, style="Primary.TButton"
                   ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Plot Curve",
                   command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log",
                   command=self._save_log, style="Success.TButton"
                   ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear",
                   command=self._clear).pack(side=tk.LEFT, padx=4)

    def _build_log(self, parent):
        f = tk.Frame(parent, bg="#f0f0f0")
        _, self.log_tree = self.make_stored_panel(f)
        self.add_delete_bar(f, self.log_tree)
        f.grid(row=3, column=0, columnspan=8, sticky="ew", padx=6, pady=4)

    def _calc(self):
        self._mcs, self._dds = [], []
        for pi in range(5):
            try:
                wm = get_float(self.cells[("wt_wet_mould", pi)])
                wmo = get_float(self.cells[("wt_mould", pi)])
                vol = get_float(self.cells[("vol", pi)], 1000)
                wt = get_float(self.cells[("wt_tin", pi)])
                ww = get_float(self.cells[("wt_wet_tin", pi)])
                wd = get_float(self.cells[("wt_dry_tin", pi)])
                if None in (wm, wmo, wt, ww, wd):
                    continue
                wt_wet = wm - wmo
                moist = ww - wd
                dry_s = wd - wt
                if dry_s <= 0:
                    continue
                mc = (moist / dry_s) * 100
                dry = calc.dry_density_kgm3(wt_wet, vol, mc)
                set_val(self.cells[("wt_wet", pi)], round(wt_wet, 1))
                set_val(self.cells[("wt_moist", pi)], round(moist, 2))
                set_val(self.cells[("wt_drysoil", pi)], round(dry_s, 2))
                set_val(self.cells[("mc", pi)], f"{mc:.1f}")
                set_val(self.cells[("bulk_dens", pi)], f"{dry/1000 * (1+mc/100):.3f}")
                set_val(self.cells[("dry_dens", pi)], f"{dry:.0f}")
                self._mcs.append(mc)
                self._dds.append(dry)
            except Exception:
                pass

        self._coeffs = None
        self._omc = self._mdd = None
        if len(self._mcs) >= 3:
            try:
                omc, mdd, coeffs = calc.proctor_fit(self._mcs, self._dds)
                set_val(self.mdd_r, f"{mdd:.0f}")
                set_val(self.omc_r, f"{omc:.1f}")
                self._omc, self._mdd, self._coeffs = omc, mdd, coeffs
                self.app.session["proctor_mdd"] = mdd
                self.app.session["proctor_omc"] = omc
            except Exception as e:
                messagebox.showerror("Polyfit Error",
                                     f"Could not fit curve.\n{e}")
        self._plot()

    def _plot(self):
        mcs = getattr(self, "_mcs", [])
        dds = getattr(self, "_dds", [])
        for w in self.chart.winfo_children():
            w.destroy()
        fig, ax = plt.subplots(figsize=(7, 6), dpi=96)
        fig.patch.set_facecolor("white")
        if mcs and dds:
            ax.plot(mcs, dds, "bo", markersize=8, zorder=5, label="Data Points")
            c = getattr(self, "_coeffs", None)
            if c is not None:
                x = np.linspace(min(mcs) * 0.85, max(mcs) * 1.15, 300)
                ax.plot(x, np.polyval(c, x), "b-", linewidth=2,
                        label="MDD/OMC Curve")
                omc, mdd = getattr(self, "_omc", None), getattr(self, "_mdd", None)
                if omc is not None and mdd is not None:
                    ax.axvline(omc, color="red", linestyle="--",
                               label=f"OMC = {omc:.1f}%")
                    ax.axhline(mdd, color="green", linestyle=":",
                               label=f"MDD = {mdd:.0f} kg/m³")
                    ax.annotate(f"MDD={mdd:.0f}\nOMC={omc:.1f}%",
                                xy=(omc, mdd), xytext=(omc + 0.5, mdd - 20),
                                fontsize=9, color="darkred",
                                arrowprops=dict(arrowstyle="->", color="darkred"))
            else:
                ax.text(0.5, 0.5, "Need ≥3 valid points for curve fit",
                        transform=ax.transAxes, ha="center", va="center",
                        fontsize=12, color="gray")
        else:
            ax.text(0.5, 0.5, "No data entered yet",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=12, color="gray")
        ax.set_xlabel("Moisture Content (%)")
        ax.set_ylabel("Dry Density (Kg/m³)")
        ax.set_title("Compaction Curve", fontweight="bold")
        ax.grid(True, alpha=0.35)
        if mcs and dds:
            ax.legend(fontsize=9)
        plt.tight_layout()
        c = FigureCanvasTkAgg(fig, self.chart)
        c.draw()
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def _save_log(self):
        mdd = self.app.session.get("proctor_mdd")
        omc = self.app.session.get("proctor_omc")
        if mdd is None:
            return messagebox.showwarning("Warning", "Calculate compaction first.")
        sno = self.info["comp_sampleno"].get()
        data = {"mdd": f"{mdd:.0f}",
                "omc": f"{omc:.1f}" if omc else "",
                "sample": sno,
                "location": self.info["comp_location"].get(),
                "type": self.info["comp_type"].get()}
        ts = self.save_to_log(sno or "Compaction", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"MDD={mdd:.0f}, OMC={omc:.1f} @ {ts}")

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")
        for pi in range(5):
            self.cells[("water", pi)].insert(0, str(50 * (pi + 1)))
            self.cells[("vol", pi)].insert(0, "1000")
        for attr in ("mdd_r", "omc_r"):
            e = getattr(self, attr)
            e.config(state="normal")
            e.delete(0, tk.END)
            e.config(state="readonly")
        for w in self.chart.winfo_children():
            w.destroy()


# =====================================================================
# # =====================================================================
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Try importing scipy for smooth interpolation
try:
    from scipy.interpolate import PchipInterpolator
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Try importing the report generation libraries
try:
    import openpyxl
    from openpyxl.drawing.image import Image as XLImage
    from docx import Document
    from docx.shared import Inches
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as PDFImage, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    REPORT_LIBS_AVAILABLE = True
except ImportError:
    REPORT_LIBS_AVAILABLE = False

# Dummy imports for the provided context (Assuming these exist in your project)
from ..config import C, FONT
from ..core import soil as calc
from ..ui.base_tab import BaseTab
from ..ui.widgets import (entry, calc_entry, hdr, section, scrolled_frame, set_val, get_float)

class PsdTab(BaseTab):
    tab_label = "PSD (BS 1377 pt2)"
    log_category = "psd"
    log_columns = (("d10", "D10 (mm)", 70), ("d60", "D60 (mm)", 70),
                   ("cu", "Cu", 50), ("gravel", "Gravel %", 70),
                   ("sand", "Sand %", 70), ("silt", "Silt %", 70))

    SIEVES = ["75", "63", "50", "37.5", "28", "20", "14", "10", "6.3", "5", "2", "1",
              "0.600", "0.425", "0.300", "0.150", "0.075", "0.0"]

    def build(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED, bg="#aaa")
        pane.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left, minsize=300, width=700)
        _, inner, _ = scrolled_frame(left)

        right = tk.Frame(pane, bg="white")
        pane.add(right, minsize=300)
        _, rinner, _ = scrolled_frame(right)
        tk.Label(rinner, text="Particle Size Distribution – Gradation Curve",
                 bg="#2c3e50", fg="white", font=(FONT, 12, "bold"),
                 pady=6).pack(fill=tk.X)

        res_strip = tk.Frame(rinner, bg="#ecf0f1", padx=8, pady=4)
        res_strip.pack(fill=tk.X)
        self.res = {}
        
        row0_items = [("D10 (mm)", "d10"), ("D30 (mm)", "d30"),
                      ("D60 (mm)", "d60"), ("Cu", "cu"), ("Ck", "ck"),
                      ("GM", "gm"), ("Classification", "psd_cls")]
                      
        for ci, (lt, key) in enumerate(row0_items):
            r, c = divmod(ci, 3)
            tk.Label(res_strip, text=lt, bg="#ecf0f1",
                     font=(FONT, 12, "bold")).grid(row=r, column=c * 2, sticky="w", padx=6, pady=2)
            e = calc_entry(res_strip, w=18 if "cls" in key else 10)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2)
            self.res[key] = e
            
        tk.Label(res_strip, text="─── Soil Composition (ASTM) ───", bg="#ecf0f1",
                 font=(FONT, 12, "bold"), fg="#2c3e50").grid(
            row=3, column=0, columnspan=6, sticky="w", padx=6, pady=(6, 2))
            
        for ci, (lt, key) in enumerate([("Gravel % (60mm - 2.0mm)", "gravel"), ("Sand % (2.0mm–0.075mm)", "sand"), ("Silt+Clay % (<0.075mm)", "silt")]):
            tk.Label(res_strip, text=lt, bg="#ecf0f1",
                     font=(FONT, 12, "bold")).grid(row=4, column=ci * 2, sticky="w", padx=6, pady=2)
            e = calc_entry(res_strip, w=10)
            e.grid(row=4, column=ci * 2 + 1, padx=4, pady=2)
            self.res[key] = e
            
        self.comp_label = tk.Label(res_strip, text="", bg="#ecf0f1", font=(FONT, 12, "bold"), fg="#2c3e50")
        self.comp_label.grid(row=5, column=0, columnspan=6, sticky="w", padx=6, pady=2)
                             
        self.chart = tk.Frame(rinner, bg="white")
        self.chart.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._build_info(inner)
        self._build_mvalues(inner)
        self._build_sieves(inner)
        self._build_sedimentation(inner)
        self._build_buttons(inner)
        self._build_log(inner)

    def _build_info(self, parent):
        top = section(parent, "Particle Size Distribution (BS 1377: part 2: 1990)", 0, 0, colspan=4)
        fields = [("Date:", "psd_date"), ("Operator:", "psd_op"),
                  ("Sample No.:", "psd_sno"), ("Technician:", "psd_tech"),
                  ("Sample Source:", "psd_src"), ("Checked By:", "psd_checked"),
                  ("Mass of Dry Sample (M1):", "psd_mass"),
                  ("Approved By:", "psd_approved"),
                  ("Soil Condition:", "psd_cond")]
        self.info = {}
        for ri, (lt, key) in enumerate(fields):
            r, c = divmod(ri, 2)
            tk.Label(top, text=lt, bg="#f0f0f0",
                     font=(FONT, 12, "bold")).grid(row=r, column=c * 2, sticky="w", padx=4, pady=2)
            e = entry(top, w=18)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2)
            self.info[key] = e
        self.info["psd_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.info["psd_mass"].insert(0, "1000")

    def _build_mvalues(self, parent):
        f = section(parent, "M-Values & Correction Factor (BS 1377)", 1, 0, colspan=2)
        items = [ ("M2 (Mass passing 20mm sieve, g)", "M2", False),
            ("M3 (Mass of sub-sample, g)\n[Use M2 if not sub-sampled]", "M3", False),
            ("M4 (Mass retained on 75μm after washing, g)\n[Leave blank for dry sieve]", "M4", False),
            ("M5 (Mass passing 75μm during dry sieving, g)\n[Leave blank for dry sieve]", "M5", False),
            ("Correction Factor (M2/M3) [Auto]", "C-FACTOR", True) ]
        self.m = {}
        for ri, (lt, key, ro) in enumerate(items):
            tk.Label(f, text=lt, bg="#f0f0f0", font=(FONT, 11), justify="left").grid(
                row=ri, column=0, sticky="w", padx=4, pady=2)
            e = entry(f, w=15)
            e.grid(row=ri, column=1, padx=4, pady=2)
            if ro:
                e.config(state="readonly", bg="#f0f0f0")
            self.m[key] = e

    def _build_sieves(self, parent):
        sieve_f = section(parent, "Sieve Analysis Data", 2, 0, colspan=4)
        self._sieve_frame = sieve_f
        headers = ["Sieve size (mm)", "Retained (g)", "Retained (%)", "Cumulative\nretained (%)", "Cumulative\nPassing (%)"]
        for ci, h in enumerate(headers):
            hdr(sieve_f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)
            
        self.cells = {}
        self._sieve_labels = self.SIEVES
        for ri, sv in enumerate(self._sieve_labels):
            tk.Label(sieve_f, text=sv, bg="#f8f8f8", font=(FONT, 12), relief=tk.RIDGE, width=8, anchor="center").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            for ci, key in enumerate(["actual", "ret_pct", "cum_ret", "pass"]):
                is_calc = key != "actual"
                e = calc_entry(sieve_f, w=12) if is_calc else entry(sieve_f, w=12)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                if sv == "0.0" and key == "actual":
                    e.config(state="readonly", bg="#f0f0f0")
                self.cells[(sv, key)] = e

    def _build_sedimentation(self, parent):
        f = section(parent, "Equivalent Particle Diameter (Sedimentation Method)", 3, 0, colspan=2)
        items = [ ("η (Viscosity) [20°C=1.0, 25°C=0.9, 30°C=0.8]", "eta", "1.0"), ("H (Effective depth of hydrometer)", "H", ""),
            ("Gs (Specific gravity of soil)", "Gs", "2.65"), ("t (Elapsed time in minutes)", "t", ""), ]
        self.sed = {}
        for ri, (lt, key, default) in enumerate(items):
            tk.Label(f, text=lt, bg="#f0f0f0", font=(FONT, 11), justify="left").grid(
                row=ri, column=0, sticky="w", padx=4, pady=2)
            e = entry(f, w=15)
            if default: e.insert(0, default)
            e.grid(row=ri, column=1, padx=4, pady=2)
            self.sed[key] = e
            
        tk.Label(f, text="D (mm) =", bg="#f0f0f0", font=(FONT, 11, "bold")).grid(row=4, column=0, sticky="e", padx=4, pady=2)
        self.sed_result = calc_entry(f, w=15)
        self.sed_result.grid(row=4, column=1, padx=4, pady=2, sticky="w")
        
        ttk.Button(f, text="Calc D", command=self._calc_sedimentation).grid(row=5, column=0, columnspan=2, pady=4)

    def _calc_sedimentation(self):
        try:
            eta = float(self.sed["eta"].get())
            H = float(self.sed["H"].get())
            Gs = float(self.sed["Gs"].get())
            t = float(self.sed["t"].get())
            
            if t <= 0 or Gs <= 1:
                raise ValueError
                
            D = 0.005531 * np.sqrt((eta * H) / ((Gs - 1) * t))
            set_val(self.sed_result, f"{D:.4f}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numerical values for Sedimentation Method.\nEnsure t > 0 and Gs > 1.")

    def _build_buttons(self, parent):
        bf = tk.Frame(parent, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=4, sticky="w", padx=6, pady=8)
        ttk.Button(bf, text="Calculate", command=self._calc, style="Primary.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Plot Curve", command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="📄 Export Reports (Excel/Word/PDF)", command=self._export_reports, style="Success.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

    def _build_log(self, parent):
        f = tk.Frame(parent, bg="#f0f0f0")
        _, self.log_tree = self.make_stored_panel(f)
        self.add_delete_bar(f, self.log_tree)
        f.grid(row=5, column=0, columnspan=4, sticky="ew", padx=6, pady=4)

    def _calc(self):
        try:
            m1 = float(self.info["psd_mass"].get())
        except ValueError:
            return messagebox.showerror("Error", "Enter M1 (Total Dry Mass)")
        if m1 <= 0:
            return messagebox.showerror("Error", "M1 must be > 0")

        m2 = get_float(self.m["M2"], m1) 
        m3 = get_float(self.m["M3"], m1)
        
        if m2 <= 0 or m3 <= 0:
            return messagebox.showerror("Error", "M2 and M3 must be > 0")

        cf = m2 / m3
        set_val(self.m["C-FACTOR"], f"{cf:.4f}")

        # --- AUTO-CALCULATE MISSING PAN MASS (0.0 row) ---
        total_actual = sum(get_float(self.cells[(sv, "actual")], 0) for sv in self._sieve_labels if sv != "0.0")
        pan_act = get_float(self.cells[("0.0", "actual")], 0)
        if pan_act == 0 or pan_act is None:
            pan_act = m1 - total_actual
            set_val(self.cells[("0.0", "actual")], f"{pan_act:.2f}")
        # -------------------------------------------------

        coarse_sieves = ["75", "63", "50", "37.5", "28", "20"]
        fine_sieves = ["14", "10", "6.3", "5", "2", "1", "0.600", "0.425", "0.300", "0.150", "0.075"]

        cum_ret_pct = 0.0
        plot_sieves = []
        plot_pass = []

        def process_row(sv, apply_cf):
            nonlocal cum_ret_pct
            act = get_float(self.cells[(sv, "actual")], 0)
            corr = act * cf if apply_cf else act
            
            ret_pct = (corr / m1) * 100
            cum_ret_pct += ret_pct
            pct_pass = max(0.0, 100.0 - cum_ret_pct)
                
            set_val(self.cells[(sv, "ret_pct")], f"{ret_pct:.0f}")
            set_val(self.cells[(sv, "cum_ret")], f"{cum_ret_pct:.0f}")
            set_val(self.cells[(sv, "pass")], f"{pct_pass:.0f}")
            return float(sv), pct_pass

        for sv in coarse_sieves:
            size, pct_pass = process_row(sv, apply_cf=False)
            plot_sieves.append(size)
            plot_pass.append(pct_pass)

        for sv in fine_sieves:
            size, pct_pass = process_row(sv, apply_cf=True)
            plot_sieves.append(size)
            plot_pass.append(pct_pass)

        # Set Pan (0.0) row values
        pan_corr = pan_act * cf
        pan_ret_pct = (pan_corr / m1) * 100
        cum_ret_pct += pan_ret_pct
        
        set_val(self.cells[("0.0", "ret_pct")], f"{pan_ret_pct:.0f}")
        set_val(self.cells[("0.0", "cum_ret")], f"{cum_ret_pct:.0f}")
        set_val(self.cells[("0.0", "pass")], f"{max(0.0, 100.0 - cum_ret_pct):.0f}")

        # Append Pan to plot data
        plot_sieves.append(0.0)
        plot_pass.append(max(0.0, 100.0 - cum_ret_pct))

        self._data = {"sieve": plot_sieves, "pass": plot_pass}

        sieves = np.array(plot_sieves)
        passes = np.array(plot_pass)
        idx = np.argsort(sieves)
        sieves, passes = sieves[idx], passes[idx]

        def interp_size(pct):
            for i in range(len(passes) - 1):
                if (passes[i] <= pct <= passes[i + 1]) or (passes[i] >= pct >= passes[i + 1]):
                    if abs(passes[i] - passes[i + 1]) > 1e-10:
                        return (sieves[i] + (pct - passes[i]) * (sieves[i + 1] - sieves[i]) / (passes[i + 1] - passes[i]))
            return None

        d10, d30, d60 = interp_size(10), interp_size(30), interp_size(60)
        for key, v in [("d10", d10), ("d30", d30), ("d60", d60)]:
            set_val(self.res[key], f"{abs(v):.4f}" if v and v > 0 else "")
            
        if d10 and d60:
            set_val(self.res["cu"], f"{d60/d10:.2f}")
            
            if d30:
                ck_val = (d30**2) / (d60*d10)
                set_val(self.res["ck"], f"{ck_val:.2f}")
                
                if d60 > 4.75:
                    if d60 / d10 >= 4 and 1 <= ck_val <= 3:
                        cls = "Well Graded Gravel (GW)"
                    elif d60 / d10 < 4:
                        cls = "Poorly Graded Gravel (GP)"
                    else:
                        cls = "Gravel"
                else:
                    if d60 / d10 >= 6 and 1 <= ck_val <= 3:
                        cls = "Well Graded Sand (SW)"
                    elif d60 / d10 < 6: 
                        cls = "Poorly Graded Sand (SP)"
                    else:
                        cls = "Sand"
                set_val(self.res["psd_cls"], cls)

        try:
            p2mm = float(self.cells[("2", "pass")].get() or 0)
            p0425mm = float(self.cells[("0.425", "pass")].get() or 0)
            p0075mm = float(self.cells[("0.075", "pass")].get() or 0)
            gm_val = (300 - p2mm - p0425mm - p0075mm) / 100
            set_val(self.res["gm"], f"{gm_val:.2f}")
        except ValueError:
            set_val(self.res["gm"], "Error")

        # --- Composition (Matches Excel) ---
        try:
            p2 = float(self.cells[("2", "pass")].get() or 0)
            p0075 = float(self.cells[("0.075", "pass")].get() or 0)
            
            set_val(self.res["gravel"], f"{max(0, 100 - p2):.0f}")
            set_val(self.res["sand"], f"{max(0, p2 - p0075):.0f}")
            set_val(self.res["silt"], f"{max(0, p0075):.0f}")
        except ValueError:
            pass
            
        self._comp_str = "  ".join(
            f"{k.upper()} = {self.res[k].get()}%"
            for k in ("gravel", "sand", "silt") if self.res[k].get())
        self.comp_label.config(text=self._comp_str)
        self._plot()

    def _plot(self):
        if not hasattr(self, "_data"):
            return
            
        # Map 0.0 to 0.01 so it plots perfectly on the log scale edge
        sv = [0.01 if s == 0.0 else s for s in self._data["sieve"]]
        ps = self._data["pass"]
        
        if not sv:
            return
            
        idx = np.argsort(sv)
        sv = np.array(sv)[idx]
        ps = np.array(ps)[idx]

        for w in self.chart.winfo_children():
            w.destroy()
            
        fig, ax = plt.subplots(figsize=(8, 6.5), dpi=96)
        fig.patch.set_facecolor("white")
        
        # Plot straight lines with markers to exactly mimic Excel
        ax.semilogx(sv, ps, 'b-', linewidth=1.5, marker='o', markersize=5, label="Gradation Curve")
        
        for key, pct, col in [("d10", 10, "red"), ("d30", 30, "green"), ("d60", 60, "orange")]:
            d = get_float(self.res.get(key))
            if d and d > 0:
                ax.axvline(d, color=col, linestyle="--", linewidth=1.2, label=f"D{pct}={d:.4f}mm")
                           
        ax.set_xlabel("Sieves (mm)", fontweight="bold")
        ax.set_ylabel("% Passing", fontweight="bold")
        ax.set_title("Gradation Curve", fontweight="bold", pad=10)
        
        ax.set_xlim([0.01, 100])
        ax.set_ylim([0, 100])
        
        ax.set_xticks([0.01, 0.1, 1, 10, 100])
        ax.set_xticklabels(['0.01', '0.1', '1', '10', '100'])
        ax.set_yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        
        # Add heavy grid lines like Excel
        ax.grid(True, which="major", color="black", linestyle="-", linewidth=0.6, alpha=0.6)
        ax.grid(True, which="minor", color="gray", linestyle="-", linewidth=0.3, alpha=0.4)
        
        ax.legend(fontsize=9, loc="lower right")
        plt.tight_layout()
        
        fig.savefig("psd_chart.png", dpi=150)
        
        c = FigureCanvasTkAgg(fig, self.chart)
        c.draw()
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    # --- Report Generation Functions Remain Unchanged ---
    def _export_reports(self):
        if not REPORT_LIBS_AVAILABLE:
            return messagebox.showerror("Missing Libraries", 
                "Please install required libraries:\npip install openpyxl python-docx reportlab")
                
        if not hasattr(self, "_data"):
            return messagebox.showwarning("No Data", "Please Calculate first.")
            
        sno = self.info["psd_sno"].get() or "Sample"
        folder = filedialog.askdirectory(title="Select Folder to Save Reports")
        if not folder:
            return
            
        try:
            self._export_excel(folder, sno)
            self._export_word(folder, sno)
            self._export_pdf(folder, sno)
            messagebox.showinfo("Success", f"Reports saved successfully in:\n{folder}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _get_table_data(self):
        headers = ["Sieve size (mm)", "Retained (g)", "Retained (%)", "Cumulative retained (%)", "Cumulative Passing (%)"]
        rows = []
        for sv in self._sieve_labels:
            rows.append([ sv, self.cells[(sv, "actual")].get(),
                self.cells[(sv, "ret_pct")].get(), self.cells[(sv, "cum_ret")].get(),self.cells[(sv, "pass")].get() ])
        return headers, rows

    def _export_excel(self, folder, sno):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "PSD Report"

        ws["A1"] = "Particle Size Distribution (BS 1377: part 2: 1990)"
        ws["A1"].font = openpyxl.styles.Font(bold=True, size=14)
        ws.merge_cells("A1:E1")

        info = [ ("Date:", self.info["psd_date"].get(), "Operator:", self.info["psd_op"].get()),
            ("Sample No.:", self.info["psd_sno"].get(), "Technician:", self.info["psd_tech"].get()),
            ("Sample Source:", self.info["psd_src"].get(), "Checked By:", self.info["psd_checked"].get()),
            ("Mass of Dry Sample:", self.info["psd_mass"].get(), "Approved By:", self.info["psd_approved"].get()),
            ("Soil Condition:", self.info["psd_cond"].get(), "", "") ]
        
        row_idx = 3
        for r in info:
            ws.cell(row=row_idx, column=1, value=r[0]).font = openpyxl.styles.Font(bold=True)
            ws.cell(row=row_idx, column=2, value=r[1])
            if r[2]:
                ws.cell(row=row_idx, column=4, value=r[2]).font = openpyxl.styles.Font(bold=True)
                ws.cell(row=row_idx, column=5, value=r[3])
            row_idx += 1

        headers, rows = self._get_table_data()
        start_row = row_idx + 1
        for col, h in enumerate(headers, start=1):
            cell = ws.cell(row=start_row, column=col, value=h)
            cell.font = openpyxl.styles.Font(bold=True)
            cell.alignment = openpyxl.styles.Alignment(horizontal="center", wrap_text=True)
            cell.border = openpyxl.styles.Border(left=openpyxl.styles.Side(style='thin'), right=openpyxl.styles.Side(style='thin'), 
                                                 top=openpyxl.styles.Side(style='thin'),  bottom=openpyxl.styles.Side(style='thin'))

        for r_idx, row in enumerate(rows, start=start_row + 1):
            for c_idx, val in enumerate(row, start=1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                cell.alignment = openpyxl.styles.Alignment(horizontal="center")
                cell.border = openpyxl.styles.Border(left=openpyxl.styles.Side(style='thin'),  right=openpyxl.styles.Side(style='thin'), 
                                                     top=openpyxl.styles.Side(style='thin'), bottom=openpyxl.styles.Side(style='thin'))

        sum_start = start_row
        ws.cell(row=sum_start, column=7, value="MAT. WT").font = openpyxl.styles.Font(bold=True)
        ws.cell(row=sum_start, column=8, value=self.info["psd_mass"].get())
        ws.cell(row=sum_start+1, column=7, value="GRAVEL").font = openpyxl.styles.Font(bold=True)
        ws.cell(row=sum_start+1, column=8, value=self.res["gravel"].get())
        ws.cell(row=sum_start+2, column=7, value="SAND").font = openpyxl.styles.Font(bold=True)
        ws.cell(row=sum_start+2, column=8, value=self.res["sand"].get())
        ws.cell(row=sum_start+3, column=7, value="CLAY/SILT").font = openpyxl.styles.Font(bold=True)
        ws.cell(row=sum_start+3, column=8, value=self.res["silt"].get())

        if os.path.exists("psd_chart.png"):
            img = XLImage("psd_chart.png")
            img.width = 500
            img.height = 400
            ws.add_image(img, f"A{start_row + len(rows) + 3}")

        wb.save(os.path.join(folder, f"PSD_Report_{sno}.xlsx"))

    def _export_word(self, folder, sno):
        doc = Document()
        doc.add_heading('Particle Size Distribution (BS 1377: part 2: 1990)', 0)

        info = [ ("Date:", self.info["psd_date"].get(), "Operator:", self.info["psd_op"].get()),
            ("Sample No.:", self.info["psd_sno"].get(), "Technician:", self.info["psd_tech"].get()),
            ("Sample Source:", self.info["psd_src"].get(), "Checked By:", self.info["psd_checked"].get()),
            ("Mass of Dry Sample:", self.info["psd_mass"].get(), "Approved By:", self.info["psd_approved"].get()),
            ("Soil Condition:", self.info["psd_cond"].get(), "", "") ]
        t_info = doc.add_table(rows=len(info), cols=4)
        t_info.style = 'Table Grid'
        for r_idx, r in enumerate(info):
            t_info.cell(r_idx, 0).text = r[0]
            t_info.cell(r_idx, 1).text = str(r[1])
            if r[2]:
                t_info.cell(r_idx, 2).text = r[2]
                t_info.cell(r_idx, 3).text = str(r[3])

        doc.add_paragraph()

        headers, rows = self._get_table_data()
        t_data = doc.add_table(rows=1, cols=5)
        t_data.style = 'Table Grid'
        hdr_cells = t_data.rows[0].cells
        for i, h in enumerate(headers):
            hdr_cells[i].text = h
            for paragraph in hdr_cells[i].paragraphs:
                paragraph.runs[0].bold = True

        for row in rows:
            cells = t_data.add_row().cells
            for i, val in enumerate(row):
                cells[i].text = str(val)

        doc.add_paragraph()
        
        doc.add_heading('Summary', level=1)
        doc.add_paragraph(f"Gravel: {self.res['gravel'].get()}%")
        doc.add_paragraph(f"Sand: {self.res['sand'].get()}%")
        doc.add_paragraph(f"Silt/Clay: {self.res['silt'].get()}%")

        doc.add_heading('Gradation Curve', level=1)
        if os.path.exists("psd_chart.png"):
            doc.add_picture("psd_chart.png", width=Inches(6.0))

        doc.save(os.path.join(folder, f"PSD_Report_{sno}.docx"))

    def _export_pdf(self, folder, sno):
        pdf_path = os.path.join(folder, f"PSD_Report_{sno}.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Particle Size Distribution (BS 1377: part 2: 1990)", styles['Title']))
        elements.append(Spacer(1, 12))

        info_data = [ ["Date:", self.info["psd_date"].get(), "Operator:", self.info["psd_op"].get()],
            ["Sample No.:", self.info["psd_sno"].get(), "Technician:", self.info["psd_tech"].get()],
            ["Sample Source:", self.info["psd_src"].get(), "Checked By:", self.info["psd_checked"].get()],
            ["Mass of Dry Sample:", self.info["psd_mass"].get(), "Approved By:", self.info["psd_approved"].get()],
            ["Soil Condition:", self.info["psd_cond"].get(), "", ""] ]
        t_info = Table(info_data, colWidths=[100, 150, 100, 150])
        t_info.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 1, colors.black)]))
        elements.append(t_info)
        elements.append(Spacer(1, 12))

        headers, rows = self._get_table_data()
        table_data = [headers] + rows
        t_data = Table(table_data, colWidths=[80, 80, 80, 100, 100])
        t_data.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.white),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(t_data)
        elements.append(Spacer(1, 24))

        elements.append(Paragraph("Summary", styles['Heading2']))
        elements.append(Paragraph(f"Gravel: {self.res['gravel'].get()}%", styles['Normal']))
        elements.append(Paragraph(f"Sand: {self.res['sand'].get()}%", styles['Normal']))
        elements.append(Paragraph(f"Silt/Clay: {self.res['silt'].get()}%", styles['Normal']))
        elements.append(Spacer(1, 12))

        if os.path.exists("psd_chart.png"):
            elements.append(PageBreak())
            elements.append(Paragraph("Gradation Curve", styles['Heading2']))
            img = PDFImage("psd_chart.png", width=500, height=400)
            elements.append(img)

        doc.build(elements)

    def _clear(self):
        for e in self.cells.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == "#f0f0f0":
                e.config(state="readonly")
        for e in self.res.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            e.config(state="readonly")
        for key, e in self.m.items():
            e.config(state="normal")
            e.delete(0, tk.END)
            if key == "C-FACTOR":
                e.config(state="readonly", bg="#f0f0f0")
        
        for key, e in self.sed.items():
            e.delete(0, tk.END)
            if key == "Gs": e.insert(0, "2.65")
            if key == "eta": e.insert(0, "1.0")
        self.sed_result.config(state="normal")
        self.sed_result.delete(0, tk.END)
        self.sed_result.config(state="readonly")

        for w in self.chart.winfo_children():
            w.destroy()
        self.comp_label.config(text="")

# 4. CBR (AASHTO T193)
class CbrTab(BaseTab):
    tab_label = "CBR (AASHTO T193)"
    log_category = "cbr"
    log_columns = (("cbr_62", "CBR 62bl (%)", 90), ("cbr_30", "CBR 30bl (%)", 90),  ("cbr_10", "CBR 10bl (%)", 90), ("location", "Location", 120))

    PENS = [x / 4 for x in range(25)]

    def build(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=6,
                              sashrelief=tk.RAISED, bg="#c0c0c0")
        pane.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left, minsize=640, width=720)
        _, inner, _ = scrolled_frame(left)

        right = tk.Frame(pane, bg="white")
        pane.add(right, minsize=420)
        tk.Label(right, text="CBR Test Results", bg="#2c3e50", fg="white",
                 font=(FONT, 12, "bold"), pady=6).pack(fill=tk.X)
        pro = tk.Frame(right, bg="#ecf0f1", pady=3)
        pro.pack(fill=tk.X)
        for ci, (lt, attr) in enumerate([("MDD (kg/m³):", "mdd_lbl"), ("95% MDD (kg/m³):", "mdd95_lbl"), ("OMC (%):", "omc_lbl")]):
            tk.Label(pro, text=lt, bg="#ecf0f1",
                     font=(FONT, 11, "bold")).grid(row=0, column=ci * 2,  padx=8, pady=2)
            e = calc_entry(pro, w=10)
            e.grid(row=0, column=ci * 2 + 1, padx=4)
            setattr(self, attr, e)
        ttk.Button(pro, text="← Pull from Proctor", command=self._pull_proctor).grid(row=0, column=6, padx=8)
        ring = tk.Frame(right, bg="#f0f0f0", pady=3)
        ring.pack(fill=tk.X)
        tk.Label(ring, text="Ring Factor:", bg="#f0f0f0", font=(FONT, 11, "bold")).grid(row=0, column=0, padx=8, pady=2)
        self.ring = entry(ring, w=8)
        self.ring.grid(row=0, column=1, padx=4)
        self.ring.insert(0, "0.1")
        ttk.Button(ring, text="Apply", command=self._calc).grid(row=0, column=2, padx=8)
        self.chart1 = tk.Frame(right, bg="white")
        self.chart1.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))
        self.chart2 = tk.Frame(right, bg="white")
        self.chart2.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

        self._build_info(inner)
        self._build_mc(inner)
        self._build_mould(inner)
        self._build_pen(inner)
        self._build_summary(inner)
        self._build_buttons(inner)
        self._build_log(inner)

        self._std = {2.5: 13.24, 5.0: 19.96}
        self._data = {"blows": [], "dd": [], "cbr": []}
        self._at95 = None

    def _build_info(self, parent):
        top = section(parent, "Determination of California Bearing Ratio " "(AASHTO T193)", 0, 0, colspan=10)
        fields = [("Location:", "cbr_loc"), ("Soil Type:", "cbr_soil"),
                  ("Layer:", "cbr_layer"), ("Material Source:", "cbr_src"), ("Sample No.:", "cbr_sampleno"),
                  ("Stabilizer type:", "cbr_stab"), ("Date of Proofing:", "cbr_dproof"), ("Stabilizer (%):", "cbr_stab_pct"),
                  ("Date of Soaking:", "cbr_dsoak"), ("Compaction Type:", "cbr_comp_type"), ("Date of Testing:", "cbr_dtest")]
        self.info = {}
        for ri, (lt, key) in enumerate(fields):
            r, c = divmod(ri, 4)
            tk.Label(top, text=lt, bg="#f0f0f0", font=(FONT, 12, "bold")).grid( row=r, column=c * 2, sticky="w", padx=3, pady=1)
            e = entry(top, w=14)
            e.grid(row=r, column=c * 2 + 1, padx=3, pady=1, sticky="w")
            self.info[key] = e

    def _build_mc(self, parent):
        f = section(parent, "Present Moisture Content & Compaction Data", 1, 0, colspan=5)
        rows = [("MDD ", "kg/m³", "cbr_mdd", False), ("OMC ", "%", "cbr_omc", False), ("95% MDD ", "kg/m³", "cbr_95mdd", True),
                ("Dry Soil Used ", "g", "cbr_dsoil", False), ("PMC ", "%", "cbr_pmc", False), ("Water to add ", "ml", "cbr_wadd", True)]
        for ci, h in enumerate(["Parameter", "Units", "62 Blows", "30 Blows", "10 Blows"]):
            hdr(f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)
        self.mc = {}
        for ri, (lbl_, unit, key, is_c) in enumerate(rows):
            tk.Label(f, text=lbl_, bg="#f8f8f8", font=(FONT, 12),
                     anchor="w", width=18).grid(row=ri + 1, column=0, sticky="ew", padx=1)
            tk.Label(f, text=unit, bg="#f8f8f8", font=(FONT, 12), width=6).grid(row=ri + 1, column=1, sticky="ew", padx=1)
            for bi, blows in enumerate([62, 30, 10]):
                k = f"{key}_{blows}"
                e = calc_entry(f, w=10) if is_c else entry(f, w=10)
                e.grid(row=ri + 1, column=bi + 2, padx=1, pady=1)
                self.mc[k] = e

    def _build_mould(self, parent):
        f = section(parent, "Mould Data (Before Soaking)", 1, 5, colspan=5)
        rows = [("Mould No.", "mould_no", False), ("Mould (g)", "wt_mould", False),
                ("Wet Soil (g)", "wt_wet", False), ("Vol of Mould (l)", "vol", False), ("Moisture content (%)", "mc_pre", False),
                ("Bulk density (kg/m³)", "bulk", True), ("Dry density (kg/m³)", "dry", True), ("Rel. Compaction (%)", "rel_comp", True)]
        for ci, h in enumerate(["Parameter", "Before 62", "Before 30", "Before 10"]):
            hdr(f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)
        self.mould = {}
        for ri, (lbl_, key, is_c) in enumerate(rows):
            tk.Label(f, text=lbl_, bg="#f8f8f8", font=(FONT, 12),
                     anchor="w", width=18).grid(row=ri + 1, column=0, sticky="ew", padx=1)
            for ci, phase in enumerate(["before_62", "before_30", "before_10"]):
                k = f"{key}_{phase}"
                e = calc_entry(f, w=9) if is_c else entry(f, w=9)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1)
                self.mould[k] = e
        for phase in ["before_62", "before_30", "before_10"]:
            self.mould[f"vol_{phase}"].insert(0, "2305")

    def _build_pen(self, parent):
        f = section(parent, "Penetration Results (Dial Gauge Readings)", 2, 0, colspan=10)
        for ci, h in enumerate(["Pen (mm)", "62 Blows\nTop", "62 Blows\nBot", "30 Blows\nTop", "30 Blows\nBot", "10 Blows\nTop", "10 Blows\nBot"]):
            hdr(f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)
        self.pen = {}
        cols = ["62T", "62B", "30T", "30B", "10T", "10B"]
        for ri, p in enumerate(self.PENS):
            tk.Label(f, text=f"{p:.2f}", bg="#f8f8f8", font=(FONT, 12), relief=tk.RIDGE, width=6).grid(row=ri + 1, column=0, padx=1, pady=1)
            for ci, ck in enumerate(cols):
                e = entry(f, w=10)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1)
                self.pen[(p, ck)] = e

    def _build_summary(self, parent):
        f = section(parent, "CBR Values", 3, 0, colspan=5)
        rows = [("No. of Strokes:", "cbr_strokes"), ("Reading at 2.50mm:", "cbr_25"), ("Reading at 5.00mm:", "cbr_50"),
                ("CBR Value 2.50mm (%):", "cbr_val25"), ("CBR Value 5.00mm (%):", "cbr_val50"), ("Design CBR (%):", "cbr_design")]
        self.sum = {}
        for ri, (lt, key) in enumerate(rows):
            tk.Label(f, text=lt, bg="#f0f0f0", font=(FONT, 12)).grid(row=ri, column=0, sticky="w", padx=4, pady=2)
            for bi, blows in enumerate([62, 30, 10]):
                k = f"{key}_{blows}"
                e = calc_entry(f, w=9)
                e.grid(row=ri, column=bi + 1, padx=2, pady=2)
                self.sum[k] = e

    def _build_buttons(self, parent):
        bf = tk.Frame(parent, bg="#f0f0f0")
        bf.grid(row=4, column=0, columnspan=10, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="Calculate CBR", command=self._calc, style="Primary.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Plot Charts", command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log, style="Success.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

    def _build_log(self, parent):
        f = tk.Frame(parent, bg="#f0f0f0")
        _, self.log_tree = self.make_stored_panel(f)
        self.add_delete_bar(f, self.log_tree)
        f.grid(row=5, column=0, columnspan=10, sticky="ew", padx=6, pady=4)

    def _pull_proctor(self):
        mdd = self.app.session.get("proctor_mdd")
        omc = self.app.session.get("proctor_omc")
        if mdd is None:
            return messagebox.showwarning( "No Proctor Data", "Calculate Compaction first (in Compaction tab).")
        mdd95 = mdd * 0.95
        set_val(self.mdd_lbl, f"{mdd:.0f}")
        set_val(self.mdd95_lbl, f"{mdd95:.0f}")
        if omc is not None:
            set_val(self.omc_lbl, f"{omc:.1f}")
        for blows in [62, 30, 10]:
            if not self.mc[f"cbr_mdd_{blows}"].get():
                set_val(self.mc[f"cbr_mdd_{blows}"], f"{mdd:.0f}")
            if omc is not None and not self.mc[f"cbr_omc_{blows}"].get():
                set_val(self.mc[f"cbr_omc_{blows}"], f"{omc:.1f}")
            set_val(self.mc[f"cbr_95mdd_{blows}"], f"{mdd95:.0f}")
        self._calc()

    def _calc(self):
        cmap = {"62T": (62, "Top"), "62B": (62, "Bot"), "30T": (30, "Top"), "30B": (30, "Bot"), "10T": (10, "Top"), "10B": (10, "Bot")}
        curves = {62: {"Top": [], "Bot": []}, 30: {"Top": [], "Bot": []}, 10: {"Top": [], "Bot": []}}
        for p in self.PENS:
            for ck, (bl, side) in cmap.items():
                v = get_float(self.pen[(p, ck)])
                if v is not None:
                    curves[bl][side].append((p, v))

        mdd = self.app.session.get("proctor_mdd")
        omc = self.app.session.get("proctor_omc")
        if mdd is None:
            mdd = get_float(self.mc.get("cbr_mdd_62"))
        if omc is None:
            omc = get_float(self.mc.get("cbr_omc_62"))
        if mdd:
            mdd95 = mdd * 0.95
            set_val(self.mdd_lbl, f"{mdd:.0f}")
            set_val(self.mdd95_lbl, f"{mdd95:.0f}")
            if omc is not None:
                set_val(self.omc_lbl, f"{omc:.1f}")

        if omc is not None:
            for bl in [62, 30, 10]:
                ds = get_float(self.mc.get(f"cbr_dsoil_{bl}"))
                pmc = get_float(self.mc.get(f"cbr_pmc_{bl}"))
                if ds and pmc is not None:
                    set_val(self.mc[f"cbr_wadd_{bl}"], f"{ds*(omc-pmc)/100:.1f}")

        for bl in [62, 30, 10]:
            ph = f"before_{bl}"
            try:
                wm = get_float(self.mould[f"wt_mould_{ph}"])
                ww = get_float(self.mould[f"wt_wet_{ph}"])
                vol = get_float(self.mould[f"vol_{ph}"], 2.305)
                mc = get_float(self.mould[f"mc_pre_{ph}"])
                if None in (wm, ww, mc):
                    continue
                dd = calc.cbr_dry_density(wm, ww, vol, mc)
                bulk = dd * (1 + mc / 100)
                set_val(self.mould[f"bulk_{ph}"], f"{bulk:.0f}")
                set_val(self.mould[f"dry_{ph}"], f"{dd:.0f}")
                if mdd:
                    set_val(self.mould[f"rel_comp_{ph}"], f"{dd/mdd*100:.1f}")
            except Exception:
                pass

        rf = get_float(self.ring, 0.1)
        for bl in [62, 30, 10]:
            for side, pen_mm, key in [("Top", 2.5, "25"), ("Top", 5.0, "50")]:
                d = self._interp(curves[bl]["Top"], pen_mm)
                if d is None:
                    d = self._interp(curves[bl]["Bot"], pen_mm)
                if d is None:
                    continue
                load = d * rf
                cbr = calc.cbr_percent(d, rf, self._std[pen_mm])
                set_val(self.sum[f"cbr_{key}_{bl}"], f"{load:.2f}")
                set_val(self.sum[f"cbr_val{key}_{bl}"], f"{cbr:.1f}")

        for bl in [62, 30, 10]:
            v25 = get_float(self.sum.get(f"cbr_val25_{bl}"))
            v50 = get_float(self.sum.get(f"cbr_val50_{bl}"))
            if v25 is not None and v50 is not None:
                set_val(self.sum[f"cbr_design_{bl}"], f"{max(v25, v50):.1f}")
            elif v25 is not None:
                set_val(self.sum[f"cbr_design_{bl}"], f"{v25:.1f}")
            elif v50 is not None:
                set_val(self.sum[f"cbr_design_{bl}"], f"{v50:.1f}")

        self._data = {"blows": [], "dd": [], "cbr": []}
        for bl in [62, 30, 10]:
            dd = get_float(self.mould.get(f"dry_before_{bl}"))
            cbr = get_float(self.sum.get(f"cbr_design_{bl}"))
            if dd and cbr:
                self._data["blows"].append(bl)
                self._data["dd"].append(dd)
                self._data["cbr"].append(cbr)
        self._at95 = None
        if mdd and len(self._data["dd"]) >= 2:
            self._at95 = calc.cbr_interp_at_95mdd(mdd, self._data["dd"], self._data["cbr"])
        self._plot()

    @staticmethod
    def _interp(points, pen_mm):
        if not points:
            return None
        pts = sorted(points)
        for (p1, d1), (p2, d2) in zip(pts, pts[1:]):
            if p1 <= pen_mm <= p2:
                if p2 - p1:
                    return d1 + (d2 - d1) * (pen_mm - p1) / (p2 - p1)
                return d1
        return pts[0][1] if pen_mm < pts[0][0] else pts[-1][1]

    def _plot(self):
        for w in self.chart1.winfo_children():
            w.destroy()
        for w in self.chart2.winfo_children():
            w.destroy()

        fig1, ax1 = plt.subplots(figsize=(5, 3.5), dpi=96)
        fig1.patch.set_facecolor("white")
        colors = {62: "blue", 30: "green", 10: "red"}
        markers = {62: "o", 30: "s", 10: "^"}
        for bl in [62, 30, 10]:
            for side, ls in [("T", "-"), ("B", "--")]:
                xs, ys = [], []
                for p in self.PENS:
                    v = get_float(self.pen[(p, f"{bl}{side}")])
                    if v is not None:
                        xs.append(p)
                        ys.append(v)
                if xs:
                    ax1.plot(xs, ys, color=colors[bl], linestyle=ls, marker=markers[bl], markersize=4, label=f"{bl} bl {side}")
        ax1.axvline(2.5, color="purple", linestyle=":", label="2.5mm")
        ax1.axvline(5.0, color="orange", linestyle=":", label="5.0mm")
        ax1.grid(True, alpha=0.3)
        ax1.set_xlabel("Penetration (mm)")
        ax1.set_ylabel("Dial Reading")
        ax1.set_title("Force vs Penetration", fontweight="bold")
        ax1.set_xlim(0, 6.5)
        ax1.legend(fontsize=7)
        plt.tight_layout()
        c1 = FigureCanvasTkAgg(fig1, self.chart1)
        c1.draw()
        c1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig1)

        fig2, ax2 = plt.subplots(figsize=(7, 4.5), dpi=96)
        fig2.patch.set_facecolor("white")
        d = getattr(self, "_data", {"blows": [], "dd": [], "cbr": []})
        mdd = self.app.session.get("proctor_mdd") or get_float(self.mdd_lbl)
        if d["blows"]:
            pairs = sorted(zip(d["dd"], d["cbr"], d["blows"]))
            dds = [p[0] for p in pairs]
            cbrs = [p[1] for p in pairs]
            ax2.plot(dds, cbrs, "bo-", linewidth=2, markersize=8)
            for dd, cbr, bl in zip(dds, cbrs, [p[2] for p in pairs]):
                ax2.annotate(f"{bl}bl", (dd, cbr), xytext=(5, 5), textcoords="offset points", fontsize=8)
            if mdd:
                ax2.axvline(mdd * 0.95, color="red", linestyle="--", label=f"95% MDD={mdd*0.95:.0f}")
                ax2.axvline(mdd, color="blue", linestyle=":", alpha=0.6, label=f"MDD={mdd:.0f}")
                if getattr(self, "_at95", None) is not None:
                    ax2.plot(mdd * 0.95, self._at95, "r*", markersize=15, label=f"CBR@95%MDD={self._at95:.1f}%")
        ax2.grid(True, alpha=0.3)
        ax2.set_xlabel("Dry Density (kg/m³)")
        ax2.set_ylabel("CBR (%)")
        ax2.set_title("CBR vs Dry Density with 95% MDD", fontweight="bold")
        ax2.legend(fontsize=8)
        plt.tight_layout()
        c2 = FigureCanvasTkAgg(fig2, self.chart2)
        c2.draw()
        c2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig2)

    def _save_log(self):
        data = {}
        for bl in [62, 30, 10]:
            for key in ["cbr_val25", "cbr_val50", "cbr_design"]:
                k = f"{key}_{bl}"
                if k in self.sum:
                    data[k] = self.sum[k].get()
            data[f"cbr_{bl}"] = self.sum.get(f"cbr_val25_{bl}").get()
        data["location"] = self.info["cbr_loc"].get()
        data["sample"] = self.info["cbr_sampleno"].get()
        mdd = self.app.session.get("proctor_mdd")
        data["mdd"] = f"{mdd:.0f}" if mdd else ""
        data["mdd_95"] = f"{mdd*0.95:.0f}" if mdd else ""
        data["cbr_at_95mdd"] = (f"{self._at95:.1f}" if getattr(self, "_at95", None) else "")
        ts = self.save_to_log(data["sample"] or "CBR", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"CBR @ {ts}")

    def _clear(self):
        for e in self.pen.values():
            e.config(state="normal")
            e.delete(0, tk.END)
        for e in self.sum.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            e.config(state="readonly")
        for k, e in self.mould.items():
            e.config(state="normal")
            e.delete(0, tk.END)
            if "rel_comp" in k or "dry" in k or "bulk" in k:
                e.config(state="readonly")
        for k, e in self.mc.items():
            e.config(state="normal")
            e.delete(0, tk.END)
            if "95mdd" in k:
                e.config(state="readonly")
        for lbl_ in [self.mdd_lbl, self.mdd95_lbl, self.omc_lbl]:
            lbl_.config(state="normal")
            lbl_.delete(0, tk.END)
            lbl_.config(state="readonly")
        for w in self.chart1.winfo_children():
            w.destroy()
        for w in self.chart2.winfo_children():
            w.destroy()
        self._data = {"blows": [], "dd": [], "cbr": []}
        self._at95 = None


# 5. FIELD DENSITY (SAND REPLACEMENT)
class FieldDensityTab(BaseTab):
    tab_label = "Field Density (Sand Repl.)"
    log_category = "field_density"
    log_columns = (("sample", "Sample", 100), ("mdd", "MDD", 80), ("passed", "Passed", 70))

    POSITIONS = ["CL", "LHS", "RHS", "CL-2", "LHS-2", "RHS-2"]

    def build(self):
        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(pane)
        pane.add(left, weight=55)
        _, lin, _ = scrolled_frame(left)

        right = ttk.Frame(pane)
        pane.add(right, weight=45)
        _, rin, _ = scrolled_frame(right)

        self._build_left(lin)
        self._build_right(rin)

    def _build_left(self, parent):
        tk.Label(parent, bg="#2c3e50", text="DETERMINATION OF FIELD COMPACTION " "(SAND REPLACEMENT METHOD)",
                 fg="#ecf0f1", font=(FONT, 14, "bold"), pady=6).pack(fill=tk.X, pady=(0, 6))

        info = tk.Frame(parent, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        info.pack(fill=tk.X, padx=6, pady=4)
        fields = [("Contractor:", "fd_contractor", 25),  ("Description:", "fd_desc", 35),
                  ("Date:", "fd_date", 12), ("Operator:", "fd_operator", 15), ("Classification:", "fd_class", 15)]
        self.info = {}
        for i, (lt, key, w) in enumerate(fields):
            tk.Label(info, text=lt, bg="#f0f0f0", font=(FONT, 11, "bold")).grid( row=i // 3, column=(i % 3) * 2, sticky="w", padx=4, pady=2)
            e = entry(info, w=w)
            e.grid(row=i // 3, column=(i % 3) * 2 + 1, padx=4, pady=2)
            self.info[key] = e
        self.info["fd_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

        sand = tk.Frame(parent, bg="#d4edda", relief=tk.RIDGE, bd=1)
        sand.pack(fill=tk.X, padx=6, pady=4)
        tk.Label(sand, text="SAND BULK DENSITY (g/cm³):", bg="#d4edda", font=(FONT, 11, "bold")).pack(side=tk.LEFT, padx=8, pady=3)
        self.sand_dens = entry(sand, w=8)
        self.sand_dens.pack(side=tk.LEFT, padx=4)
        self.sand_dens.insert(0, "1.247")

        pro = tk.Frame(parent, bg="#ecf0f1", relief=tk.RIDGE, bd=1)
        pro.pack(fill=tk.X, padx=6, pady=4)
        tk.Label(pro, text="Proctor MDD (kg/m³):", bg="#ecf0f1", font=(FONT, 11, "bold")).pack(side=tk.LEFT, padx=8, pady=2)
        self.proctor_mdd = calc_entry(pro, w=9)
        self.proctor_mdd.pack(side=tk.LEFT, padx=4)
        tk.Label(pro, text="Proctor OMC (%):", bg="#ecf0f1",  font=(FONT, 11, "bold")).pack(side=tk.LEFT, padx=8, pady=2)
        self.proctor_omc = calc_entry(pro, w=8)
        self.proctor_omc.pack(side=tk.LEFT, padx=4)
        ttk.Button(pro, text="← Pull from Proctor", command=self._pull_proctor).pack(side=tk.LEFT, padx=10)

        tbl = tk.LabelFrame(parent, text="Test Data", bg="#f0f0f0",  font=(FONT, 11, "bold"), padx=4, pady=4)
        tbl.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)
        row_defs = [ ("Location (Chainage / offset)", "loc", False), ("Depth (MM)", "depth", False),
            ("Wt. of sample (g)", "w1", False), ("Wt. of sand before pouring (g)", "w2", False), ("Wt. of sand after pouring (g)", "w3", False),
            ("Wt. of sand in cone (g)", "w4", False), ("Wt. of sand in hole (g)", "sand_hole", True), ("Wet Density (g/cm³)", "wet_density", True),
            ("Tin No.", "tin_no", False), ("Wt. of wet soil + tin (g)", "wet_tin", False), ("Wt. of dry soil + tin (g)", "dry_tin", False),
            ("Wt. of tin (g)", "tin_wt", False), ("Wt. of moisture (g)", "moisture", True),
            ("Wt. of dry soil (g)", "dry_soil", True), ("Moisture Content (%)", "mc", True),
            ("Field Dry Density (kg/m³)", "dry_density", True),  ("BS Compaction MDD (kg/m³)", "mdd", False),
            ("BS Optimum moisture content (%)", "OMC", False), ("Relative Compaction (%)", "rel_comp", True),
            ("Relative Moisture Content (%)", "rel_mc", True), ("FMC vs OMC", "fmc_omc", True), ("Result", "result", True)]
        for ci, pos in enumerate(self.POSITIONS):
            tk.Label(tbl, text=pos, bg=C.HDR, font=(FONT, 10, "bold"),
                     relief=tk.RIDGE, width=10, anchor="center").grid( row=0, column=ci + 1, padx=1, pady=1, sticky="ew")
        self.cells = {}
        for ri, (lbl_, key, is_c) in enumerate(row_defs):
            bg = "#e8f4f8" if key in ("dry_density", "rel_comp") else "#f8f8f8"
            tk.Label(tbl, text=lbl_, bg=bg, font=(FONT, 9), relief=tk.RIDGE,
                     width=28, anchor="w", wraplength=180, justify="left").grid( row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            for ci, pos in enumerate(self.POSITIONS):
                e = calc_entry(tbl, w=10) if is_c else entry(tbl, w=10)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.cells[(key, pos)] = e

        remarks = tk.LabelFrame(parent, text="Remarks", bg="#f0f0f0", font=(FONT, 11, "bold"), padx=4, pady=4)
        remarks.pack(fill=tk.X, padx=6, pady=6)
        self.remarks = tk.Text(remarks, height=3, width=80, font=(FONT, 11))
        self.remarks.pack(fill=tk.X, padx=4, pady=4)

        bf = tk.Frame(parent, bg="#f0f0f0")
        bf.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate All", command=self._calc, style="Primary.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

    def _build_right(self, parent):
        tk.Label(parent, text="Position Summary", bg="#2c3e50", fg="white",
                 font=(FONT, 12, "bold"), pady=6).pack(fill=tk.X, pady=(0, 6))
        pro = tk.Frame(parent, bg="#ecf0f1", relief=tk.RIDGE, bd=1)
        pro.pack(fill=tk.X, padx=8, pady=4)
        self.lbl_mdd = tk.Label(pro, text="Proctor MDD: --", bg="#ecf0f1", font=(FONT, 10, "bold"))
        self.lbl_mdd.pack(side=tk.LEFT, padx=10, pady=3)
        self.lbl_omc = tk.Label(pro, text="Proctor OMC: --", bg="#ecf0f1", font=(FONT, 10, "bold"))
        self.lbl_omc.pack(side=tk.LEFT, padx=10, pady=3)

        tbl = tk.Frame(parent, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        tbl.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        for ci, h in enumerate(["Position", "Dry Density (kg/m³)",  "Moisture (%)", "Rel. MC (%)", "Rel. Comp (%)", "Result"]):
            tk.Label(tbl, text=h, bg=C.HDR, font=(FONT, 9, "bold"),
                     relief=tk.RIDGE, padx=4, pady=2).grid( row=0, column=ci, sticky="ew", padx=1, pady=1)
        self.summary_labels = {}
        for r, pos in enumerate(self.POSITIONS, start=1):
            tk.Label(tbl, text=pos, bg="#f8f8f8", font=(FONT, 9),
                     relief=tk.RIDGE, padx=4, pady=2).grid(  row=r, column=0, sticky="ew", padx=1, pady=1)
            self.summary_labels[pos] = {}
            for ci, key in enumerate(["dd", "mc", "rel_mc", "rc", "result"], start=1):
                lbl_ = tk.Label(tbl, text="--", bg=C.CALC, font=(FONT, 9),  relief=tk.RIDGE, padx=4, pady=2)
                lbl_.grid(row=r, column=ci, sticky="ew", padx=1, pady=1)
                self.summary_labels[pos][key] = lbl_

        # Charts
        tk.Label(parent, text="Analysis Charts", bg="#2c3e50", fg="white",
                 font=(FONT, 12, "bold"), pady=6).pack(fill=tk.X, pady=(6, 6))
        chart = tk.Frame(parent, bg="#f0f0f0")
        chart.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.fig = Figure(figsize=(5, 8), dpi=160, facecolor="#f0f0f0")
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _pull_proctor(self):
        mdd = self.app.session.get("proctor_mdd")
        omc = self.app.session.get("proctor_omc")
        if mdd is None or omc is None:
            return messagebox.showwarning(
                "No Proctor Data",
                "Calculate Compaction first.")
        set_val(self.proctor_mdd, f"{mdd:.0f}")
        set_val(self.proctor_omc, f"{omc:.1f}")
        self.lbl_mdd.config(text=f"Proctor MDD: {mdd:.0f} kg/m³")
        self.lbl_omc.config(text=f"Proctor OMC: {omc:.1f}%")
        for pos in self.POSITIONS:
            set_val(self.cells[("mdd", pos)], f"{mdd:.0f}")
            set_val(self.cells[("OMC", pos)], f"{omc:.1f}")
        messagebox.showinfo("Pulled", f"MDD={mdd:.0f}, OMC={omc:.1f}")

    def _calc(self):
        sand_dens = get_float(self.sand_dens, 1.247)
        mdd_global = get_float(self.proctor_mdd, 0) or 0
        omc_global = get_float(self.proctor_omc, 0) or 0
        self.lbl_mdd.config(
            text=f"Proctor MDD: {mdd_global:.0f} kg/m³" if mdd_global
            else "Proctor MDD: --")
        self.lbl_omc.config(
            text=f"Proctor OMC: {omc_global:.1f}%" if omc_global
            else "Proctor OMC: --")

        dd_data, rc_data, rmc_data, labels = [], [], [], []
        passed = failed = marginal = 0

        for pos in self.POSITIONS:
            w1 = get_float(self.cells[("w1", pos)])
            w2 = get_float(self.cells[("w2", pos)])
            w3 = get_float(self.cells[("w3", pos)])
            w4 = get_float(self.cells[("w4", pos)])
            wet_tin = get_float(self.cells[("wet_tin", pos)])
            dry_tin = get_float(self.cells[("dry_tin", pos)])
            tin = get_float(self.cells[("tin_wt", pos)])
            mdd_c = get_float(self.cells[("mdd", pos)], mdd_global)
            omc_c = get_float(self.cells[("OMC", pos)], omc_global)
            if None in (w1, w2, w3, w4):
                continue
            sand_hole = w2 - (w3 + w4)
            set_val(self.cells[("sand_hole", pos)], f"{sand_hole:.1f}")
            if sand_hole <= 0:
                continue
            wet_d = (w1 / sand_hole) * sand_dens
            set_val(self.cells[("wet_density", pos)], f"{wet_d:.3f}")
            mc = 0.0
            if None not in (wet_tin, dry_tin, tin) and (dry_tin - tin) > 0:
                moist = wet_tin - dry_tin
                drys = dry_tin - tin
                mc = (moist / drys) * 100
                set_val(self.cells[("moisture", pos)], f"{moist:.1f}")
                set_val(self.cells[("dry_soil", pos)], f"{drys:.1f}")
                set_val(self.cells[("mc", pos)], f"{mc:.1f}")
            dry_d = wet_d * 1000 / (1 + mc / 100) if mc > 0 else wet_d * 1000
            set_val(self.cells[("dry_density", pos)], f"{dry_d:.0f}")
            rc = 0.0
            if mdd_c:
                rc = (dry_d / mdd_c) * 100
                set_val(self.cells[("rel_comp", pos)], f"{rc:.1f}")
            rmc = 0.0
            if omc_c and mc > 0:
                rmc = (mc / omc_c) * 100
                set_val(self.cells[("rel_mc", pos)], f"{rmc:.1f}")
            if omc_c and mc > 0:
                ratio = (mc / omc_c) * 100
                if ratio < 75:
                    s = f"{ratio:.0f}% (DRY)"
                elif ratio > 105:
                    s = f"{ratio:.0f}% (WET)"
                else:
                    s = f"{ratio:.0f}% (OK)"
                set_val(self.cells[("fmc_omc", pos)], s)
            result, color = "FAIL", "#e74c3c"
            if mdd_c and omc_c:
                comp_ok = 95 <= rc <= 105
                mc_ok = 75 <= rmc <= 105
                if comp_ok and mc_ok:
                    result, color, passed = "PASS", "#27ae60", passed + 1
                elif comp_ok or mc_ok:
                    result, color = "MARGINAL", "#f39c12"
                    marginal += 1
                else:
                    failed += 1
            elif mdd_c:
                if 95 <= rc <= 105:
                    result, color, passed = "PASS", "#27ae60", passed + 1
                else:
                    failed += 1
            else:
                failed += 1
            set_val(self.cells[("result", pos)], result)
            if pos in self.summary_labels:
                L = self.summary_labels[pos]
                L["dd"].config(text=f"{dry_d:.0f}")
                L["mc"].config(text=f"{mc:.1f}")
                L["rel_mc"].config(text=f"{rmc:.1f}" if rmc else "--")
                L["rc"].config(text=f"{rc:.1f}" if rc else "--")
                L["result"].config(text=result, bg=color, fg="white")
            dd_data.append(dry_d)
            rc_data.append(rc)
            rmc_data.append(rmc)
            labels.append(pos)
        self._update_charts(dd_data, rc_data, labels, mdd_global, passed, failed, marginal)

    def _update_charts(self, dds, rcs, labels, mdd, passed, failed, marginal):
        self.ax1.clear(); self.ax2.clear(); self.ax3.clear()
        if dds:
            colors = ["#27ae60" if d >= mdd else "#e74c3c" for d in dds]
            bars = self.ax1.bar(labels, dds, color=colors, edgecolor="black")
            if mdd:
                self.ax1.axhline(mdd, color="blue", linestyle="--", label=f"MDD={mdd:.0f}")
            self.ax1.set_ylabel("Dry Density (kg/m³)")
            self.ax1.set_title("Dry Density by Position")
            self.ax1.legend()
            for b, d in zip(bars, dds):
                self.ax1.text(b.get_x() + b.get_width()/2, b.get_height() + 10, f"{d:.0f}", ha="center", va="bottom", fontsize=8)
        if rcs:
            colors = ["#27ae60" if 95 <= r <= 105 else "#e74c3c" for r in rcs]
            bars = self.ax2.bar(labels, rcs, color=colors, edgecolor="black")
            self.ax2.axhspan(95, 105, alpha=0.2, color="green")
            self.ax2.set_ylabel("Relative Compaction (%)")
            self.ax2.set_title("Relative Compaction")
            for b, r in zip(bars, rcs):
                self.ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{r:.1f}%", ha="center", va="bottom", fontsize=8)
        total = passed + failed + marginal
        if total:
            sizes, colors_pie, lbls = [], [], []
            if passed: sizes.append(passed); colors_pie.append("#27ae60"); lbls.append("PASS")
            if marginal: sizes.append(marginal); colors_pie.append("#f39c12"); lbls.append("MARG")
            if failed: sizes.append(failed); colors_pie.append("#e74c3c"); lbls.append("FAIL")
            self.ax3.pie(sizes, labels=lbls, colors=colors_pie, autopct="%1.1f%%", startangle=90)
            self.ax3.set_title("Overall Test Results")
        self.fig.tight_layout()
        self.canvas.draw()

    def _clear(self):
        for (key, pos), e in self.cells.items():
            e.config(state="normal")
            e.delete(0, tk.END)
            if e.cget("bg") == C.CALC:
                e.config(state="readonly")
        for pos, L in self.summary_labels.items():
            for v in L.values():
                v.config(text="--", bg=C.CALC, fg="black")
        self.remarks.delete("1.0", tk.END)
        for ax in (self.ax1, self.ax2, self.ax3):
            ax.clear()
        self.canvas.draw()


# 6. STABILIZATION
class StabilizationTab(BaseTab):
    tab_label = " STABILIZATION (Stab.)"
    log_category = "stabilization"
    log_columns = (("mdd_62", "MDD 62", 70), ("omc_62", "OMC 62", 60), ("wet_62", "Wet 62", 70), 
                   ("stab_62", "Stab 62", 65), ("mdd_10", "MDD 10", 70))

    def build(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5,
                              sashrelief=tk.RAISED, bg="#aaa")
        pane.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left, minsize=900, width=600)
        _, lin, _ = scrolled_frame(left)

        right = tk.Frame(pane, bg="white")
        pane.add(right, minsize=500)
        _, rin, _ = scrolled_frame(right)

        tk.Label(rin, text="Stabilization Calculation Results",
                 bg="#2c3e50", fg="white", font=(FONT, 12, "bold"), pady=6).pack(fill=tk.X)
        res = tk.Frame(rin, bg="#ecf0f1", padx=8, pady=8)
        res.pack(fill=tk.X, padx=4, pady=4)
        for ci, h in enumerate(["Parameter", "62 Blows", "30 Blows", "10 Blows"]):
            tk.Label(res, text=h, bg=C.HDR, font=(FONT, 11, "bold"),
                     relief=tk.RIDGE, padx=4, pady=2).grid( row=0, column=ci, sticky="ew", padx=1, pady=1)
        self.summary = {}
        rows = [("MDD (kg/m³)", "mdd"), ("OMC (%)", "omc"), ("PMC (%)", "pmc"), ("Volume (cm³)", "volume"),
                ("STAB %", "stab_pct"), ("Wet Soil (g)", "wet_soil"), ("Dry Soil (g)", "dry_soil"),
                ("Stab to Add (g)", "stab_to_add"), ("TOTAL MAT. (g)", "total_mat"), ("Water to Add (ml)", "water_to_add")]
        for ri, (lt, key) in enumerate(rows):
            tk.Label(res, text=lt, bg="#f8f8f8", font=(FONT, 11),
                     relief=tk.RIDGE, padx=4, pady=2, anchor="w").grid(row=ri + 1, column=0, sticky="ew", padx=1, pady=1)
            for ci, bl in enumerate([62, 30, 10]):
                e = calc_entry(res, w=12)
                e.grid(row=ri + 1, column=ci + 1, padx=1, pady=1, sticky="ew")
                self.summary[(key, bl)] = e
        self.chart = tk.Frame(rin, bg="white")
        self.chart.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._build_info(lin)
        self._build_common(lin)
        self._build_volume(lin)
        self._build_buttons(lin)
        self._build_log(lin)

    def _build_info(self, parent):
        top = section(parent, "Stabilization Test Data (STAB)", 0, 0, colspan=6)
        fields = [("Date:", "stab_date"), ("Operator:", "stab_operator"), ("Sample No.:", "stab_sampleno"), ("Technician:", "stab_tech"),
                  ("Location:", "stab_location"), ("Checked By:", "stab_checked"), ("Sample Description:", "stab_desc"),
                  ("Approved By:", "stab_approved"), ("Soil Condition:", "stab_condition"), ("Stabilizer Type:", "stab_type")]
        self.info = {}
        for ri, (lt, key) in enumerate(fields):
            r, c = divmod(ri, 3)
            tk.Label(top, text=lt, bg="#f0f0f0", font=(FONT, 12, "bold")).grid( row=r, column=c * 2, sticky="w", padx=4, pady=2)
            e = entry(top, w=16)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="w")
            self.info[key] = e
        self.info["stab_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

    def _build_common(self, parent):
        f = section(parent, "Common Parameters", 1, 0, colspan=6)
        params = [("MDD (kg/m³) for 62 Blows:", "stab_mdd_ref", 10), ("OMC (%):", "stab_omc", 10), ("PMC (%):", "stab_pmc", 10), ("STAB %:", "stab_pct", 10)]
        self.common = {}
        for ri, (lt, key, w) in enumerate(params):
            r, c = divmod(ri, 2)
            tk.Label(f, text=lt, bg="#f0f0f0",
                     font=(FONT, 12, "bold")).grid( row=r, column=c * 2, sticky="w", padx=6, pady=3)
            e = entry(f, w=w)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=3)
            self.common[key] = e
        self.common["stab_mdd_ref"].insert(0, "2.170")
        self.common["stab_omc"].insert(0, "7.7")
        self.common["stab_pmc"].insert(0, "2.0")
        self.common["stab_pct"].insert(0, "1.5")

    def _build_volume(self, parent):
        f = section(parent, "Volume & MDD by Blow Count (Auto)", 2, 0, colspan=6)
        for ci, h in enumerate(["Parameter", "Unit", "62 Blows", "30 Blows", "10 Blows"]):
            hdr(f, h, row=0, column=ci, sticky="ew", padx=1, pady=2)
        rows = [("Volume", "cm³", "vol"), ("MDD", "kg/m³", "mdd_vol"), ("MDD", "%", "mdd_pct"), ("OMC", "%", "omc_vol"), ("PMC", "%", "pmc_vol")]
        self.vol = {}
        for ri, (lt, unit, key) in enumerate(rows):
            tk.Label(f, text=lt, bg="#f8f8f8", font=(FONT, 12), relief=tk.RIDGE, width=18, anchor="w").grid(
                row=ri + 1, column=0, padx=1, pady=1, sticky="ew")
            tk.Label(f, text=unit, bg="#f8f8f8", font=(FONT, 12),
                     relief=tk.RIDGE, width=8, anchor="center").grid( row=ri + 1, column=1, padx=1, pady=1)
            for ci, bl in enumerate([62, 30, 10]):
                e = calc_entry(f, w=12) if key in ("mdd_vol", "mdd_pct") \
                    else entry(f, w=12)
                e.grid(row=ri + 1, column=ci + 2, padx=1, pady=1, sticky="ew")
                self.vol[(key, bl)] = e
        for bl in [62, 30, 10]:
            self.vol[("vol", bl)].insert(0, "2305")
            self.vol[("omc_vol", bl)].insert(0, "7.7")
            self.vol[("pmc_vol", bl)].insert(0, "2.0")
        self.vol[("mdd_pct", 62)].insert(0, "100")
        self.vol[("mdd_pct", 30)].insert(0, "95")
        self.vol[("mdd_pct", 10)].insert(0, "90")
        self.vol[("mdd_vol", 62)].insert(0, "2.1700")
        self.vol[("mdd_vol", 30)].insert(0, "2.0615")
        self.vol[("mdd_vol", 10)].insert(0, "1.9530")

    def _build_buttons(self, parent):
        bf = tk.Frame(parent, bg="#f0f0f0")
        bf.grid(row=3, column=0, columnspan=6, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text="⚙ Calculate All", command=self._calc, style="Primary.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="📊 Plot Chart", command=self._plot).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="💾 Save to Log", command=self._save_log, style="Success.TButton" ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear).pack(side=tk.LEFT, padx=4)

    def _build_log(self, parent):
        f = tk.Frame(parent, bg="#f0f0f0")
        _, self.log_tree = self.make_stored_panel(f)
        self.add_delete_bar(f, self.log_tree)
        f.grid(row=4, column=0, columnspan=6, sticky="ew", padx=6, pady=4)

    def _calc(self):
        mdd62 = get_float(self.vol[("mdd_vol", 62)], 2.17)
        mdd30 = get_float(self.vol[("mdd_vol", 30)], mdd62 * 0.95)
        mdd10 = get_float(self.vol[("mdd_vol", 10)], mdd62 * 0.90)
        vol62 = get_float(self.vol[("vol", 62)], 2305)
        vol30 = get_float(self.vol[("vol", 30)], 2305)
        vol10 = get_float(self.vol[("vol", 10)], 2305)
        omc62 = get_float(self.vol[("omc_vol", 62)], 7.7)
        omc30 = get_float(self.vol[("omc_vol", 30)], 7.7)
        omc10 = get_float(self.vol[("omc_vol", 10)], 7.7)
        pmc62 = get_float(self.vol[("pmc_vol", 62)], 2.0)
        pmc30 = get_float(self.vol[("pmc_vol", 30)], 2.0)
        pmc10 = get_float(self.vol[("pmc_vol", 10)], 2.0)
        stab_pct = get_float(self.common["stab_pct"], 1.5)

        self._data = {"blows": [], "wet": [], "dry": [], "water": []}
        for bl, mdd, vol, omc, pmc in [(62, mdd62, vol62, omc62, pmc62), (30, mdd30, vol30, omc30, pmc30), (10, mdd10, vol10, omc10, pmc10)]:
            if mdd <= 0:
                continue
            wet = vol * mdd * (1 + omc / 100) + 500
            dry = wet / (1 + pmc / 100)
            stab = dry * stab_pct / 100
            total = dry + stab
            water = total * (omc - pmc) / 100
            set_val(self.summary[("mdd", bl)], f"{mdd:.4f}")
            set_val(self.summary[("omc", bl)], f"{omc:.1f}")
            set_val(self.summary[("pmc", bl)], f"{pmc:.1f}")
            set_val(self.summary[("volume", bl)], f"{vol:.1f}")
            set_val(self.summary[("stab_pct", bl)], f"{stab_pct:.1f}%")
            set_val(self.summary[("wet_soil", bl)], f"{wet:.1f}")
            set_val(self.summary[("dry_soil", bl)], f"{dry:.1f}")
            set_val(self.summary[("stab_to_add", bl)], f"{stab:.1f}")
            set_val(self.summary[("total_mat", bl)], f"{total:.1f}")
            set_val(self.summary[("water_to_add", bl)], f"{water:.1f}")
            self._data["blows"].append(bl)
            self._data["wet"].append(wet)
            self._data["dry"].append(dry)
            self._data["water"].append(water)
        self._plot()

    def _plot(self):
        d = getattr(self, "_data", None)
        if not d or not d["blows"]:
            return
        for w in self.chart.winfo_children():
            w.destroy()
        fig, ax = plt.subplots(figsize=(7, 5.5), dpi=96)
        fig.patch.set_facecolor("white")
        x = np.arange(len(d["blows"]))
        width = 0.25
        ax.bar(x - width, d["wet"], width, label="Wet Soil", color="#2ecc71")
        ax.bar(x, d["dry"], width, label="Dry Soil", color="#f39c12")
        ax.bar(x + width, d["water"], width, label="Water to Add", color="#3498db")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{b} blows" for b in d["blows"]])
        ax.set_ylabel("Values")
        ax.set_title("Stabilization Test Results", fontweight="bold")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        c = FigureCanvasTkAgg(fig, self.chart)
        c.draw()
        c.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def _save_log(self):
        data = {}
        for bl in [62, 30, 10]:
            for key in ["mdd", "omc", "pmc", "volume", "wet_soil", "dry_soil", "stab_to_add", "total_mat", "water_to_add"]:
                e = self.summary.get((key, bl))
                if e:
                    data[f"{key}_{bl}"] = e.get()
        data["stab_pct"] = self.common["stab_pct"].get()
        data["sample"] = self.info["stab_sampleno"].get()
        data["location"] = self.info["stab_location"].get()
        data["stab_type"] = self.info["stab_type"].get()
        ts = self.save_to_log(data["sample"] or "STAB", data)
        self.reload_log(self.log_tree)
        self.log_tree._refresh_count()
        messagebox.showinfo("Saved", f"STAB @ {ts}")

    def _clear(self):
        for e in self.summary.values():
            e.config(state="normal")
            e.delete(0, tk.END)
            e.config(state="readonly")
        for (key, bl), e in self.vol.items():
            e.config(state="normal")
            e.delete(0, tk.END)
            if key == "vol":
                e.insert(0, "2305")
            elif key == "mdd_pct":
                e.insert(0, {"62": "100", "30": "95", "10": "90"}[str(bl)])
            elif key in ("omc_vol",):
                e.insert(0, "7.7")
            elif key in ("pmc_vol",):
                e.insert(0, "2.0")
            elif key == "mdd_vol":
                e.insert(0, {"62": "2.1700", "30": "2.0615", "10": "1.9530"}[str(bl)])
        for w in self.chart.winfo_children():
            w.destroy()