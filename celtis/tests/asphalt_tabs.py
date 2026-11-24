import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

from ..ui.base_tab import BaseTab
from ..ui.widgets import (entry, calc_entry, set_val, get_float,
                          section, section_pack, scrolled_frame, hdr, lbl)
from ..config import C

CALC_BG = C.CALC
HDR_BG  = C.HDR


class ExtractionTab(BaseTab):
    tab_label = "Bitumen Extraction"
    log_category = "asphalt_extraction"
    log_columns = (("avg_bt", "Bitumen %", 90), ("station", "Station", 140))

    def build(self):
        _, inner, _ = scrolled_frame(self)

        header_f = tk.Frame(inner, bg='#1f3864', pady=4)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text="QUANTITATIVE EXTRACTION OF BITUMEN & MECHANICAL ANALYSIS OF EXTRACTED AGGREGATE",
                 bg='#1f3864', fg='white', font=('Times New Roman', 12, 'bold')).pack()

        info_f = tk.LabelFrame(inner, text="Sample Information", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        info_f.pack(fill=tk.X, padx=6, pady=4)
        ext_fields = [("Sampling Station:", "ext_station", 20), ("Sample Ref:", "ext_ref", 20),
                      ("Represented Section:", "ext_section", 20), ("Date Sampled:", "ext_date_s", 12),
                      ("Date Tested:", "ext_date_t", 12), ("Technician:", "ext_tech", 20)]
        self.ext_info = {}
        for ri, (lt, key, w) in enumerate(ext_fields):
            r, c = divmod(ri, 3)
            tk.Label(info_f, text=lt, bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(row=r, column=c*2, sticky='w', padx=4, pady=2)
            e = entry(info_f, w=w)
            e.grid(row=r, column=c*2+1, padx=4, pady=2, sticky='w')
            self.ext_info[key] = e
        self.ext_info['ext_date_t'].insert(0, datetime.now().strftime('%d/%m/%Y'))

        left_f = tk.LabelFrame(inner, text="Bitumen Extraction", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        left_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=4)

        col_hdrs = ["Specimen Reference", "T1", "T2", "T3", "T4"]
        self.ext_bt_cells = {}
        for ci, h in enumerate(col_hdrs):
            hdr(left_f, h, row=0, column=ci, sticky='ew', padx=1, pady=2)

        bt_rows = [("Mass of sample (g) A", "A"), ("Mass of aggregate (g) after extraction B", "B"),
                   ("Mass of filter paper (g) C", "C"), ("Mass of filler+filter (g) after extraction D", "D"),
                   ("Mass of filler (g) E=D-C", "E"), ("Mass of total aggregate (g) F=B+E", "F"),
                   ("Mass of bitumen (g) G=A-F", "G"), ("Bitumen content (%) H=G/F*100", "H")]
        for ri, (lbl_txt, key) in enumerate(bt_rows):
            is_calc = key in ['E', 'F', 'G', 'H']
            tk.Label(left_f, text=lbl_txt, bg='#f8f8f8', font=('Times New Roman', 11), relief=tk.RIDGE, width=28, anchor='w', wraplength=190).grid(row=ri+1, column=0, padx=1, pady=1, sticky='ew')
            for ci in range(1, 5):
                e = calc_entry(left_f, w=8) if is_calc else entry(left_f, w=8)
                e.grid(row=ri+1, column=ci, padx=1, pady=1, sticky='ew')
                self.ext_bt_cells[(key, ci)] = e

        avg_f = tk.Frame(left_f, bg='#f0f0f0')
        avg_f.grid(row=len(bt_rows)+1, column=0, columnspan=5, sticky='ew', padx=4, pady=4)
        tk.Label(avg_f, text="Average Bitumen Content (%)", bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).pack(side=tk.LEFT)
        self.ext_avg_bt = calc_entry(avg_f, w=12)
        self.ext_avg_bt.pack(side=tk.LEFT, padx=6)

        right_f = tk.LabelFrame(inner, text="Mechanical Analysis of Extracted Aggregate", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        right_f.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6, pady=4)

        SIEVES = ["28", "20", "14", "10", "6.3", "4", "2", "1", "0.425", "0.300", "0.150", "0.075", "Pan"]
        cols = ["Sieve (mm)", "Wt Ret. (g)", "Wt.% Ret.", "Com. % Ret.", "% Passing", "Spec Limit\nLower", "Spec Limit\nUpper"]
        for ci, h in enumerate(cols):
            hdr(right_f, h, row=0, column=ci, sticky='ew', padx=1, pady=2)

        self.ext_sieve_cells = {}
        total_wt_idx = 0
        for ri, sv in enumerate(SIEVES):
            tk.Label(right_f, text=sv, bg='#f8f8f8', font=('Times New Roman', 11), relief=tk.RIDGE, width=7, anchor='center').grid(row=ri+1, column=0, padx=1, pady=1, sticky='ew')
            row_cells = {}
            for ci, key in enumerate(["wt_ret", "wt_pct", "com_ret", "pass", "lower", "upper"]):
                is_calc = key in ["wt_pct", "com_ret", "pass"]
                is_spec = key in ["lower", "upper"]
                e = calc_entry(right_f, w=8) if is_calc else entry(right_f, w=8)
                if is_spec:
                    e.insert(0, "100" if sv in ["28", "20"] else ("0" if sv == "Pan" else ""))
                e.grid(row=ri+1, column=ci+1, padx=1, pady=1, sticky='ew')
                row_cells[key] = e
            self.ext_sieve_cells[sv] = row_cells
            if sv == "Pan":
                total_wt_idx = ri + 1

        self.ext_total_wt = calc_entry(right_f, w=8)
        self.ext_total_wt.grid(row=total_wt_idx+1, column=1, padx=1, pady=1, sticky='ew')
        tk.Label(right_f, text="Total", bg='#f8f8f8', font=('Times New Roman', 11, 'bold'), relief=tk.RIDGE).grid(row=total_wt_idx+1, column=0, padx=1, pady=1, sticky='ew')

        self.ext_chart_frame = tk.Frame(inner, bg='white')
        self.ext_chart_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=6, pady=4)

        bf = tk.Frame(inner, bg='#f0f0f0')
        bf.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate Extraction", command=self._calc_extraction, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Plot Gradation", command=self._plot_extraction_gradation, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save to Log", command=self._save_extraction_to_log, style='Success.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear_extraction).pack(side=tk.LEFT, padx=4)

    def _calc_extraction(self):
        bt_vals = []
        for ci in range(1, 5):
            A = get_float(self.ext_bt_cells[("A", ci)])
            B = get_float(self.ext_bt_cells[("B", ci)])
            C = get_float(self.ext_bt_cells[("C", ci)])
            D = get_float(self.ext_bt_cells[("D", ci)])
            if None in (A, B, C, D):
                continue
            E = D - C
            F = B + E
            G = A - F
            H = (G / F) * 100 if F > 0 else 0
            set_val(self.ext_bt_cells[("E", ci)], f"{E:.2f}")
            set_val(self.ext_bt_cells[("F", ci)], f"{F:.2f}")
            set_val(self.ext_bt_cells[("G", ci)], f"{G:.2f}")
            set_val(self.ext_bt_cells[("H", ci)], f"{H:.2f}")
            bt_vals.append(H)

        if bt_vals:
            avg_bt = sum(bt_vals) / len(bt_vals)
            set_val(self.ext_avg_bt, f"{avg_bt:.2f}")
        total_wt = 0
        for sv in ["28", "20", "14", "10", "6.3", "4", "2", "1", "0.425", "0.300", "0.150", "0.075"]:
            wt = get_float(self.ext_sieve_cells[sv]["wt_ret"], 0)
            total_wt += wt
        set_val(self.ext_total_wt, f"{total_wt:.2f}")

        cum_ret = 0
        for sv in ["28", "20", "14", "10", "6.3", "4", "2", "1", "0.425", "0.300", "0.150", "0.075", "Pan"]:
            wt = get_float(self.ext_sieve_cells[sv]["wt_ret"], 0)
            cum_ret += wt
            wt_pct = (wt / total_wt) * 100 if total_wt > 0 else 0
            com_ret = (cum_ret / total_wt) * 100 if total_wt > 0 else 0
            pct_pass = 100 - com_ret
            set_val(self.ext_sieve_cells[sv]["wt_pct"], f"{wt_pct:.2f}")
            set_val(self.ext_sieve_cells[sv]["com_ret"], f"{com_ret:.2f}")
            set_val(self.ext_sieve_cells[sv]["pass"], f"{pct_pass:.2f}")

    def _plot_extraction_gradation(self):
        for w in self.ext_chart_frame.winfo_children():
            w.destroy()
        fig, ax = plt.subplots(figsize=(7, 5))
        sieves = []
        passes = []
        for sv, cells in self.ext_sieve_cells.items():
            if sv == "Pan":
                continue
            try:
                p = get_float(cells["pass"])
                if p is not None:
                    sieves.append(float(sv) if sv != "0.075" else 0.075)
                    passes.append(p)
            except Exception:
                pass

        if sieves:
            ax.semilogx(sieves, passes, 'bo-', linewidth=1.5, markersize=6, label='Extracted Gradation')
            ax.grid(True, which="both", alpha=0.3)
            ax.set_xlabel("Sieve Size (mm)")
            ax.set_ylabel("% Passing")
            ax.set_title("Gradation Curve of Extracted Aggregate")
            ax.set_ylim(0, 100)
            ax.set_xlim(0.05, 40)
            ax.legend()
        else:
            ax.text(0.5, 0.5, "No data to plot", ha='center', va='center', transform=ax.transAxes)

        canvas = FigureCanvasTkAgg(fig, self.ext_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    def _clear_extraction(self):
        for (key, ci), e in self.ext_bt_cells.items():
            e.config(state='normal'); e.delete(0, tk.END)
            if e.cget('bg') == CALC_BG:
                e.config(state='readonly')
        for sv, cells in self.ext_sieve_cells.items():
            for e in cells.values():
                e.config(state='normal'); e.delete(0, tk.END)
                if e.cget('bg') == CALC_BG:
                    e.config(state='readonly')
        self.ext_avg_bt.config(state='normal'); self.ext_avg_bt.delete(0, tk.END); self.ext_avg_bt.config(state='readonly')
        self.ext_total_wt.config(state='normal'); self.ext_total_wt.delete(0, tk.END); self.ext_total_wt.config(state='readonly')
        for w in self.ext_chart_frame.winfo_children():
            w.destroy()

    def _save_extraction_to_log(self):
        data = {"avg_bt": self.ext_avg_bt.get(), "station": self.ext_info["ext_station"].get()}
        for sv, cells in self.ext_sieve_cells.items():
            data[f"pass_{sv}"] = cells["pass"].get()
        ts = self.save_to_log(self.log_category, f'Extraction {self.ext_info["ext_station"].get() or "N/A"}', data)
        messagebox.showinfo("Saved", f"Extraction results stored at {ts}")


class MarshallTab(BaseTab):
    tab_label = "Marshall Test"
    log_category = "asphalt_marshall"
    log_columns = (("avg_stability", "Stability", 90),
                   ("avg_flow", "Flow", 90),
                   ("sample", "Sample", 120))

    def build(self):
        _, inner, _ = scrolled_frame(self)

        header_f = tk.Frame(inner, bg='#27ae60', pady=4)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text="MARSHALL STABILITY AND FLOW TEST", bg='#27ae60', fg='white', font=('Times New Roman', 12, 'bold')).pack()

        info_f = tk.LabelFrame(inner, text="General Information", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        info_f.pack(fill=tk.X, padx=6, pady=4)
        mar_fields = [("Date:", "mar_date", 12), ("Project:", "mar_project", 30), ("Sample ID:", "mar_sample", 20), ("Bitumen Content (%):", "mar_bt_pct", 8)]
        self.mar_info = {}
        for ri, (lt, key, w) in enumerate(mar_fields):
            r, c = divmod(ri, 2)
            tk.Label(info_f, text=lt, bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(row=r, column=c*2, sticky='w', padx=4, pady=2)
            e = entry(info_f, w=w)
            e.grid(row=r, column=c*2+1, padx=4, pady=2, sticky='w')
            self.mar_info[key] = e
        self.mar_info['mar_date'].insert(0, datetime.now().strftime('%d/%m/%Y'))

        data_f = tk.LabelFrame(inner, text="Specimen Data", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        data_f.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        MAR_SPEC = 6
        cols = ["Specimen Height", "Bulk SG (Gmb)", "Max SG (Gmm)", "Air Voids %", "VMA %", "VFB %", "Stability (kN)", "Flow (mm)"]
        col_keys = ["height", "gmb", "gmm", "voids", "vma", "vfb", "stability", "flow"]

        hdr(data_f, "Specimen", row=0, column=0, w=20)
        for ci, h in enumerate(cols):
            hdr(data_f, h, row=0, column=ci+1, w=20)

        self.mar_cells = {}
        for ri in range(MAR_SPEC):
            lbl(data_f, f"Spec {ri+1}", row=ri+1, column=0, sticky='ew', padx=2, pady=2)
            for ci, key in enumerate(col_keys):
                is_calc = key in ["voids", "vma", "vfb"]
                e = calc_entry(data_f, w=10) if is_calc else entry(data_f, w=10)
                e.grid(row=ri+1, column=ci+1, padx=1, pady=1, sticky='ew')
                self.mar_cells[(ri, key)] = e

        hdr(data_f, "AVERAGE", row=MAR_SPEC+2, column=0, w=8)
        hdr(data_f, "SPEC", row=MAR_SPEC+3, column=0, w=8)
        self.mar_avg = {}
        self.mar_spec = {}
        for ci, key in enumerate(col_keys):
            e_avg = calc_entry(data_f, w=10); e_avg.grid(row=MAR_SPEC+2, column=ci+1, padx=1, pady=1, sticky='ew'); self.mar_avg[key] = e_avg
            e_spec = entry(data_f, w=10); e_spec.grid(row=MAR_SPEC+3, column=ci+1, padx=1, pady=1, sticky='ew'); self.mar_spec[key] = e_spec

        bf = tk.Frame(inner, bg='#f0f0f0'); bf.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc_marshall, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save to Log", command=self._save_marshall_to_log, style='Success.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear_marshall).pack(side=tk.LEFT, padx=4)

    def _calc_marshall(self):
        sums = {k: 0 for k in ["gmb", "voids", "vma", "vfb", "stability", "flow"]}
        counts = {k: 0 for k in ["gmb", "voids", "vma", "vfb", "stability", "flow"]}
        for ri in range(6):
            gmb = get_float(self.mar_cells[(ri, "gmb")])
            gmm = get_float(self.mar_cells[(ri, "gmm")])
            stab = get_float(self.mar_cells[(ri, "stability")])
            flow = get_float(self.mar_cells[(ri, "flow")])

            if gmb and gmm and gmm > 0:
                voids = ((gmm - gmb) / gmm) * 100
                set_val(self.mar_cells[(ri, "voids")], f"{voids:.2f}")
                sums["voids"] += voids; counts["voids"] += 1
            if stab:
                sums["stability"] += stab; counts["stability"] += 1
            if flow:
                sums["flow"] += flow; counts["flow"] += 1

        for k in ["voids", "vma", "vfb", "stability", "flow"]:
            if counts[k] > 0:
                set_val(self.mar_avg[k], f"{sums[k]/counts[k]:.2f}")

    def _clear_marshall(self):
        for (_, k), e in self.mar_cells.items():
            e.config(state='normal'); e.delete(0, tk.END)
            if e.cget('bg') == CALC_BG:
                e.config(state='readonly')
        for e in self.mar_avg.values():
            e.config(state='normal'); e.delete(0, tk.END); e.config(state='readonly')
        for e in self.mar_spec.values():
            e.config(state='normal'); e.delete(0, tk.END)

    def _save_marshall_to_log(self):
        data = {}
        for (ri, k), e in self.mar_cells.items():
            data[f"sp{ri+1}_{k}"] = e.get()
        for k, e in self.mar_avg.items():
            data[f"avg_{k}"] = e.get()
        data["sample"] = self.mar_info["mar_sample"].get()
        ts = self.save_to_log(self.log_category, f'Marshall {self.mar_info["mar_sample"].get() or "N/A"}', data)
        messagebox.showinfo("Saved", f"Marshall results stored at {ts}")


class GmmTab(BaseTab):
    tab_label = "Max Sp. Gravity (Gmm)"
    log_category = "asphalt_gmm"
    log_columns = (("avg", "Gmm", 80), ("source", "Source", 200))

    def build(self):
        _, inner, _ = scrolled_frame(self)

        header_f = tk.Frame(inner, bg='#8BC34A', pady=4)
        header_f.pack(fill=tk.X)
        tk.Label(header_f, text="THEORETICAL MAXIMUM SPECIFIC GRAVITY (Gmm) - VACUUM PYCNOMETER", bg='#8BC34A', fg='white', font=('Times New Roman', 12, 'bold')).pack()

        info_f = tk.LabelFrame(inner, text="Information", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        info_f.pack(fill=tk.X, padx=6, pady=4)
        gmm_fields = [("Source:", "gmm_src", 30), ("Date Mixed:", "gmm_date", 14), ("Technician:", "gmm_tech", 20)]
        self.gmm_info = {}
        for ri, (lt, key, w) in enumerate(gmm_fields):
            r, c = divmod(ri, 2)
            tk.Label(info_f, text=lt, bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(row=r, column=c*2, sticky='w', padx=4, pady=2)
            e = entry(info_f, w=w)
            e.grid(row=r, column=c*2+1, padx=4, pady=2, sticky='w')
            self.gmm_info[key] = e
        self.gmm_info['gmm_date'].insert(0, datetime.now().strftime('%d/%m/%Y'))

        data_f = tk.LabelFrame(inner, text="Pyknometer Data (Jar 1 & 2)", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        data_f.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        hdr(data_f, "Description", row=0, column=0, w=30)
        hdr(data_f, "Jar 1", row=0, column=1, w=15)
        hdr(data_f, "Jar 2", row=0, column=2, w=15)

        self.gmm_cells = {}
        rows = [("Mass of Jar (g)", "m_jar"), ("A. Mass of Dry Sample in Air (g)", "m_dry"),
                ("B. Mass of Jar Filled With Water (g)", "m_jar_water"),
                ("C. Mass of Jar + Sample + Water (g)", "m_total")]
        for ri, (desc, key) in enumerate(rows):
            tk.Label(data_f, text=desc, bg='#f8f8f8', font=('Times New Roman', 11), relief=tk.RIDGE, width=30, anchor='w').grid(row=ri+1, column=0, padx=1, pady=1)
            for ci in (1, 2):
                e = entry(data_f, w=15)
                e.grid(row=ri+1, column=ci, padx=1, pady=1, sticky='ew')
                self.gmm_cells[(key, ci)] = e

        k_f = tk.LabelFrame(inner, text="Water Temperature Correction", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        k_f.pack(fill=tk.X, padx=6, pady=4)
        tk.Label(k_f, text="Temp. (C):", bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(row=0, column=0, padx=4, pady=2, sticky='w')
        self.gmm_temp = entry(k_f, w=6)
        self.gmm_temp.grid(row=0, column=1, padx=4, pady=2, sticky='w')
        self.gmm_temp.insert(0, "25")
        self.gmm_temp.bind('<KeyRelease>', self._calc_gmm_auto)

        self.K_FACTORS = {18: 1.0016, 19: 1.001, 20: 1.0012, 21: 1.0010, 22: 1.0007,
                          23: 1.0005, 24: 1.0003, 25: 1.0000, 26: 0.9997, 28: 0.9992, 29: 0.9989}

        res_f = tk.LabelFrame(inner, text="Calculated Gmm", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        res_f.pack(fill=tk.X, padx=6, pady=4)

        self.gmm_res = {}
        for ci in (1, 2):
            tk.Label(res_f, text=f"Gmm Jar {ci}:", bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(row=0, column=ci*2-2, padx=4, pady=2)
            e = calc_entry(res_f, w=14)
            e.grid(row=0, column=ci*2-1, padx=4, pady=2)
            self.gmm_res[ci] = e

        tk.Label(res_f, text="Average Gmm:", bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(row=1, column=0, padx=4, pady=4)
        self.gmm_avg = calc_entry(res_f, w=14)
        self.gmm_avg.grid(row=1, column=1, padx=4, pady=4)

        bf = tk.Frame(inner, bg='#f0f0f0'); bf.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc_gmm, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save to Log", command=self._save_gmm_to_log, style='Success.TButton').pack(side=tk.LEFT, padx=4)

    def _calc_gmm_auto(self, event=None):
        self._calc_gmm()

    def _calc_gmm(self):
        try:
            temp = float(self.gmm_temp.get())
            K = self.K_FACTORS.get(int(round(temp)), 1.0000)
        except Exception:
            K = 1.0000

        gmm_vals = []
        for ci in (1, 2):
            A = get_float(self.gmm_cells[("m_dry", ci)])
            B = get_float(self.gmm_cells[("m_jar_water", ci)])
            C = get_float(self.gmm_cells[("m_total", ci)])
            m_jar = get_float(self.gmm_cells[("m_jar", ci)])

            if A and B and C and m_jar and (A + B - C) != 0:
                gmm = K * A / (A + B - C)
                set_val(self.gmm_res[ci], f"{gmm:.3f}")
                gmm_vals.append(gmm)

        if gmm_vals:
            set_val(self.gmm_avg, f"{sum(gmm_vals)/len(gmm_vals):.3f}")

    def _save_gmm_to_log(self):
        data = {"avg": self.gmm_avg.get(), "source": self.gmm_info["gmm_src"].get()}
        ts = self.save_to_log(self.log_category, f'Gmm {self.gmm_info["gmm_src"].get() or "N/A"}', data)
        messagebox.showinfo("Saved", f"Gmm results stored at {ts}")


class CoreDensityTab(BaseTab):
    tab_label = "Core Density"
    log_category = "core_density"
    log_columns = (("offset", "Offset", 80), ("core_dens", "Core Dens.", 80),
                   ("rel_comp", "Rel. Comp %", 80))

    def build(self):
        _, inner, _ = scrolled_frame(self)

        hdr_frame = tk.Frame(inner, bg='#2c3e50', pady=4)
        hdr_frame.pack(fill=tk.X)
        tk.Label(hdr_frame, text="Core Analysis - Compaction (BS/EN)", bg='#2c3e50', fg='white',
                 font=('Times New Roman', 12, 'bold')).pack()

        info_f = tk.LabelFrame(inner, text="Project Information", bg='#f0f0f0',
                               font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        info_f.pack(fill=tk.X, padx=6, pady=4)
        info_fields = [("Date:", "cd_date", 12), ("Project:", "cd_project", 30), ("Technologist:", "cd_tech", 20), ("Location:", "cd_loc", 20)]
        self.cd_info = {}
        for ri, (lt, key, w) in enumerate(info_fields):
            r, c = divmod(ri, 2)
            tk.Label(info_f, text=lt, bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(
                row=r, column=c*2, sticky='w', padx=4, pady=2)
            e = entry(info_f, w=w)
            e.grid(row=r, column=c*2+1, padx=4, pady=2, sticky='w')
            self.cd_info[key] = e
        self.cd_info['cd_date'].insert(0, datetime.now().strftime('%d/%m/%Y'))

        table_f = tk.LabelFrame(inner, text="Core Data", bg='#f0f0f0',
                                font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        table_f.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        cols = [("Offset", "offset", 15), ("Thickness (mm)", "thick", 15),
                ("Weight In Air (g)", "air_wt", 18), ("Weight In Water (g)", "water_wt", 18),
                ("After Soak (g)", "soak_wt", 15), ("Volume (g)", "vol", 15),
                ("Core Density (g/cc)", "core_dens", 15), ("Max Density (g/cc)", "max_dens", 15),
                ("Rel. Comp. (%)", "rel_comp", 15), ("Av. Comp. (%)", "avg_comp", 15)]
        NUM_ROWS = 6

        for ci, (h, _, w) in enumerate(cols):
            tk.Label(table_f, text=h, bg=HDR_BG, font=('Times New Roman', 11, 'bold'),
                     relief=tk.RIDGE, width=w, anchor='center').grid(
                row=0, column=ci, padx=1, pady=1, sticky='ew')

        self.cd_cells = {}
        all_entries = []
        for ri in range(NUM_ROWS):
            row_data = {}
            for ci, (_, key, w) in enumerate(cols):
                is_calc = key in ('vol', 'core_dens', 'rel_comp', 'avg_comp')
                e = calc_entry(table_f, w=w) if is_calc else entry(table_f, w=w)
                e.grid(row=ri+1, column=ci, padx=1, pady=1, sticky='ew')
                row_data[key] = e
                all_entries.append(e)
            self.cd_cells[ri] = row_data

        bf = tk.Frame(inner, bg='#f0f0f0')
        bf.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc_core_density, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save to Log", command=self._save_core_density_to_log, style='Success.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear_core_density).pack(side=tk.LEFT, padx=4)

    def _calc_core_density(self):
        for ri, row in self.cd_cells.items():
            try:
                air = get_float(row['air_wt'])
                water = get_float(row['water_wt'])
                soak = get_float(row['soak_wt'])
                max_dens = get_float(row['max_dens'])
                if air is None or water is None or soak is None:
                    continue
                vol = soak - water
                if vol > 0:
                    core_dens = air / vol
                    set_val(row['vol'], f"{vol:.1f}")
                    set_val(row['core_dens'], f"{core_dens:.3f}")
                    if max_dens and max_dens > 0:
                        rel = (core_dens / max_dens) * 100
                        set_val(row['rel_comp'], f"{rel:.0f}")
                else:
                    set_val(row['vol'], "")
                    set_val(row['core_dens'], "")
                    set_val(row['rel_comp'], "")
            except Exception:
                pass

        rel_vals = [get_float(row['rel_comp']) for row in self.cd_cells.values() if get_float(row['rel_comp']) is not None]
        if rel_vals:
            avg = sum(rel_vals) / len(rel_vals)
            for row in self.cd_cells.values():
                set_val(row['avg_comp'], f"{avg:.0f}")

    def _save_core_density_to_log(self):
        data = {}
        for ri, row in self.cd_cells.items():
            data[f'row_{ri}'] = {k: row[k].get() for k in row}
        data['project'] = self.cd_info['cd_project'].get()
        data['location'] = self.cd_info['cd_loc'].get()
        ts = self.save_to_log(self.log_category, self.cd_info['cd_project'].get() or 'Core Density', data)
        messagebox.showinfo("Saved", f"Core density data stored at {ts}")

    def _clear_core_density(self):
        for row in self.cd_cells.values():
            for e in row.values():
                e.config(state='normal')
                e.delete(0, tk.END)
                if e.cget('bg') == CALC_BG:
                    e.config(state='readonly')


class SprayRateTab(BaseTab):
    tab_label = "Spray Rate"
    log_category = "spray_rate"
    log_columns = (("loc", "Location", 100), ("rate", "Spray Rate", 90))

    def build(self):
        _, inner, _ = scrolled_frame(self)

        hdr_frame = tk.Frame(inner, bg='#2c3e50', pady=4)
        hdr_frame.pack(fill=tk.X)
        tk.Label(hdr_frame, text="Determination of Spray Rate (Truck Distributor Method)",
                 bg='#2c3e50', fg='white', font=('Times New Roman', 12, 'bold')).pack()

        info_f = tk.LabelFrame(inner, text="Job Information", bg='#f0f0f0',
                               font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        info_f.pack(fill=tk.X, padx=6, pady=4)
        info_fields = [("Date:", "sr_date", 12), ("Request No.:", "sr_req", 16),
                       ("Type of Bitumen:", "sr_bitumen", 20), ("Density (g/cm3):", "sr_density", 12),
                       ("Spray Temp. (C):", "sr_temp", 12), ("Tray Size (m2):", "sr_tray", 12)]
        self.sr_info = {}
        for ri, (lt, key, w) in enumerate(info_fields):
            r, c = divmod(ri, 3)
            tk.Label(info_f, text=lt, bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(
                row=r, column=c*2, sticky='w', padx=4, pady=2)
            e = entry(info_f, w=w)
            e.grid(row=r, column=c*2+1, padx=4, pady=2, sticky='w')
            self.sr_info[key] = e
        self.sr_info['sr_date'].insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.sr_info['sr_density'].insert(0, "1.02")
        self.sr_info['sr_tray'].insert(0, "0.09")

        table_f = tk.LabelFrame(inner, text="Tray Data", bg='#f0f0f0', font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        table_f.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        cols = [("Location", "loc", 14), ("Tray No.", "tray", 10), ("Tray+Bitumen (kg)", "tray_bit", 16),
                ("Tray Weight (kg)", "tray_wt", 14), ("Bitumen (kg)", "bit_wt", 12),
                ("Volume (l)", "vol", 10), ("Spray Rate (l/m2)", "rate", 14), ("Avg. Rate (l/m2)", "avg_rate", 14)]

        NUM_ROWS = 8

        for ci, (h, _, w) in enumerate(cols):
            tk.Label(table_f, text=h, bg=HDR_BG, font=('Times New Roman', 11, 'bold'),
                     relief=tk.RIDGE, width=w, anchor='center').grid(
                row=0, column=ci, padx=1, pady=1, sticky='ew')

        self.sr_cells = {}
        all_entries = []
        for ri in range(NUM_ROWS):
            row_data = {}
            for ci, (_, key, w) in enumerate(cols):
                is_calc = key in ('bit_wt', 'vol', 'rate', 'avg_rate')
                e = calc_entry(table_f, w=w) if is_calc else entry(table_f, w=w)
                e.grid(row=ri+1, column=ci, padx=1, pady=1, sticky='ew')
                row_data[key] = e
                all_entries.append(e)
            self.sr_cells[ri] = row_data

        bf = tk.Frame(inner, bg='#f0f0f0')
        bf.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc_spray_rate, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save to Log", command=self._save_spray_rate_to_log, style='Success.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear_spray_rate).pack(side=tk.LEFT, padx=4)

    def _calc_spray_rate(self):
        density = get_float(self.sr_info['sr_density'], 1.02)
        tray_area = get_float(self.sr_info['sr_tray'], 0.09)
        if density <= 0 or tray_area <= 0:
            messagebox.showerror("Error", "Density and Tray Area must be positive.")
            return

        rates = []
        for row in self.sr_cells.values():
            try:
                tray_bit = get_float(row['tray_bit'])
                tray_wt = get_float(row['tray_wt'])
                if tray_bit is None or tray_wt is None:
                    continue
                bit_wt = tray_bit - tray_wt
                if bit_wt <= 0:
                    continue
                vol = bit_wt / density
                rate = vol / tray_area
                set_val(row['bit_wt'], f"{bit_wt:.3f}")
                set_val(row['vol'], f"{vol:.3f}")
                set_val(row['rate'], f"{rate:.2f}")
                if rate > 0:
                    rates.append(rate)
            except Exception:
                pass

        for row in self.sr_cells.values():
            set_val(row['avg_rate'], "")
        if rates:
            avg = sum(rates) / len(rates)
            for row in self.sr_cells.values():
                set_val(row['avg_rate'], f"{avg:.2f}")

    def _save_spray_rate_to_log(self):
        data = {}
        for ri, row in self.sr_cells.items():
            data[f'row_{ri}'] = {k: row[k].get() for k in row}
        data['bitumen'] = self.sr_info['sr_bitumen'].get()
        data['date'] = self.sr_info['sr_date'].get()
        ts = self.save_to_log(self.log_category, self.sr_info['sr_req'].get() or 'Spray Rate', data)
        messagebox.showinfo("Saved", f"Spray rate data stored at {ts}")

    def _clear_spray_rate(self):
        for row in self.sr_cells.values():
            for e in row.values():
                e.config(state='normal')
                e.delete(0, tk.END)
                if e.cget('bg') == CALC_BG:
                    e.config(state='readonly')


class SpecificGravityTab(BaseTab):
    tab_label = "Specific Gravity"
    log_category = "specific_gravity"
    log_columns = (("sg", "Sp. Gr.", 80), ("wa", "Abs. %", 80),
                   ("material", "Material", 120))

    def build(self):
        _, inner, _ = scrolled_frame(self)

        hdr_frame = tk.Frame(inner, bg='#2c3e50', pady=4)
        hdr_frame.pack(fill=tk.X)
        tk.Label(hdr_frame, text="Specific Gravity of Coarse Aggregate (IS 2720 Part III)",
                 bg='#2c3e50', fg='white', font=('Times New Roman', 12, 'bold')).pack()

        info_f = tk.LabelFrame(inner, text="Sample Information", bg='#f0f0f0',
                               font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        info_f.pack(fill=tk.X, padx=6, pady=4)
        info_fields = [("Date:", "sg_date", 12), ("Project:", "sg_project", 30),
                       ("Location:", "sg_loc", 20), ("Material:", "sg_material", 20)]
        self.sg_info = {}
        for ri, (lt, key, w) in enumerate(info_fields):
            r, c = divmod(ri, 2)
            tk.Label(info_f, text=lt, bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(
                row=r, column=c*2, sticky='w', padx=4, pady=2)
            e = entry(info_f, w=w)
            e.grid(row=r, column=c*2+1, padx=4, pady=2, sticky='w')
            self.sg_info[key] = e
        self.sg_info['sg_date'].insert(0, datetime.now().strftime('%d/%m/%Y'))

        table_f = tk.LabelFrame(inner, text="Test Data", bg='#f0f0f0',
                                font=('Times New Roman', 11, 'bold'), padx=4, pady=4)
        table_f.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        cols = [("Specimen Ref.", "ref", 14), ("Temp. C", "temp", 10), ("Dry Wt. W1 (g)", "dry_wt", 14),
                ("Under Water W2 (g)", "under_wt", 16), ("Saturated W3 (g)", "sat_wt", 16),
                ("Volume W4 (g)", "vol", 12), ("Sp. Gr.", "sg", 12), ("Water Abs. (%)", "wa", 14)]

        NUM_ROWS = 4

        for ci, (h, _, w) in enumerate(cols):
            tk.Label(table_f, text=h, bg=HDR_BG, font=('Times New Roman', 11, 'bold'),
                     relief=tk.RIDGE, width=w, anchor='center').grid(
                row=0, column=ci, padx=1, pady=1, sticky='ew')

        self.sg_cells = {}
        all_entries = []
        for ri in range(NUM_ROWS):
            row_data = {}
            for ci, (_, key, w) in enumerate(cols):
                is_calc = key in ('vol', 'sg', 'wa')
                e = calc_entry(table_f, w=w) if is_calc else entry(table_f, w=w)
                e.grid(row=ri+1, column=ci, padx=1, pady=1, sticky='ew')
                row_data[key] = e
                all_entries.append(e)
            self.sg_cells[ri] = row_data

        sum_f = tk.LabelFrame(inner, text="Average Results", bg='#f0f0f0',
                              font=('Times New Roman', 11, 'bold'), padx=6, pady=4)
        sum_f.pack(fill=tk.X, padx=6, pady=4)
        tk.Label(sum_f, text="Avg. Specific Gravity:", bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(
            row=0, column=0, sticky='w', padx=4, pady=2)
        self.sg_avg_sg = calc_entry(sum_f, w=12)
        self.sg_avg_sg.grid(row=0, column=1, padx=4, pady=2)
        tk.Label(sum_f, text="Avg. Water Absorption (%):", bg='#f0f0f0', font=('Times New Roman', 11, 'bold')).grid(
            row=0, column=2, sticky='w', padx=4, pady=2)
        self.sg_avg_wa = calc_entry(sum_f, w=12)
        self.sg_avg_wa.grid(row=0, column=3, padx=4, pady=2)

        bf = tk.Frame(inner, bg='#f0f0f0')
        bf.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc_specific_gravity, style='Primary.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save to Log", command=self._save_sg_to_log, style='Success.TButton').pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear", command=self._clear_specific_gravity).pack(side=tk.LEFT, padx=4)

    def _calc_specific_gravity(self):
        sg_vals = []
        wa_vals = []
        for row in self.sg_cells.values():
            try:
                dry = get_float(row['dry_wt'])
                under = get_float(row['under_wt'])
                sat = get_float(row['sat_wt'])
                if None in (dry, under, sat) or dry <= 0:
                    continue
                vol = sat - under
                if vol <= 0:
                    continue
                sg = dry / vol
                wa = ((sat - dry) / dry) * 100
                set_val(row['vol'], f"{vol:.1f}")
                set_val(row['sg'], f"{sg:.3f}")
                set_val(row['wa'], f"{wa:.2f}")
                sg_vals.append(sg)
                wa_vals.append(wa)
            except Exception:
                pass
        if sg_vals:
            set_val(self.sg_avg_sg, f"{sum(sg_vals)/len(sg_vals):.3f}")
        if wa_vals:
            set_val(self.sg_avg_wa, f"{sum(wa_vals)/len(wa_vals):.2f}")

    def _save_sg_to_log(self):
        data = {}
        for ri, row in self.sg_cells.items():
            data[f'row_{ri}'] = {k: row[k].get() for k in row}
        data['sg_avg'] = self.sg_avg_sg.get()
        data['wa_avg'] = self.sg_avg_wa.get()
        data['material'] = self.sg_info['sg_material'].get()
        data['project'] = self.sg_info['sg_project'].get()
        ts = self.save_to_log(self.log_category, self.sg_info['sg_project'].get() or 'Sp.Gr.', data)
        messagebox.showinfo("Saved", f"Specific gravity data stored at {ts}")

    def _clear_specific_gravity(self):
        for row in self.sg_cells.values():
            for e in row.values():
                e.config(state='normal')
                e.delete(0, tk.END)
                if e.cget('bg') == CALC_BG:
                    e.config(state='readonly')
        for e in [self.sg_avg_sg, self.sg_avg_wa]:
            e.config(state='normal')
            e.delete(0, tk.END)
            e.config(state='readonly')
