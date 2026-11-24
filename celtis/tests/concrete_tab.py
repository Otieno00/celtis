import tkinter as tk
import os
import json
from tkinter import filedialog
from ..reports.concrete_docx import export_concrete_cube_report
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from ..config import C, FONT, ENTRY_FONT, SMALL_FONT, SMALL_BOLD
from ..core import concrete as calc
from ..ui.base_tab import BaseTab
from ..ui.widgets import (entry, calc_entry, hdr, lbl, section, section_pack, scrolled_frame, set_val, get_float)


class ConcreteTab(BaseTab):
    tab_label = " Concrete Tests "
    log_category = "concrete_cubes"
    log_columns = (("sample_no", "Sample No.", 100), ("design_class", "Class", 55),
                   ("date_cast", "Cast", 95), ("age_days", "Age", 60), ("max_load", "Load kN", 80), ("comp_str", "Str N/mm2", 95))

    _PARAM_SETS = {
        "Compressive Strength Test": [("Cube Dim (mm):", "cube_dim", 150),
                                      ("Load at Failure (kN):", "load_failure", None),
                                      ("Age (days):", "age", 28)],
        "Slump Test":                [("Initial Height (mm):", "initial_h", 300),
                                      ("Final Height (mm):", "final_h", None)],
        "Flexural Strength Test":    [("Width (mm):", "width", 150),
                                      ("Depth (mm):", "depth", 150),
                                      ("Span (mm):", "span", 500),
                                      ("Load (kN):", "load", None)],
        "Split Tensile Test":        [("Diameter (mm):", "diameter", 150),
                                      ("Length (mm):", "length", 300),
                                      ("Load at Failure (kN):", "load_failure", None)],
    }

    def build(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)
        self._build_single(nb)
        self._build_cube(nb)
        self._load_history()

    def _build_single(self, nb):
        outer = ttk.Frame(nb)
        #nb.add(outer, text="Single Specimen Tests")   
        left = ttk.Frame(outer, width=380)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        ttk.Label(left, text="Select Test:",
                  font=(FONT, 12, "bold")).pack(anchor=tk.W, pady=4)
        self.test_var = tk.StringVar()
        cb = ttk.Combobox(left, textvariable=self.test_var, values=list(self._PARAM_SETS.keys()), state="readonly", width=38)
        cb.pack(fill=tk.X, pady=4)
        cb.bind("<<ComboboxSelected>>", self._on_test)

        self.params_frame = ttk.LabelFrame(left, text="Parameters", padding=8)
        self.params_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        self.inputs = {}
        for ri, (txt, key) in enumerate([("Sample ID:", "sample_id"), ("Technician:", "technician")]):
            ttk.Label(self.params_frame, text=txt).grid(
                row=ri, column=0, sticky="w", pady=4)
            e = ttk.Entry(self.params_frame, width=28)
            e.grid(row=ri, column=1, pady=4, padx=4)
            self.inputs[key] = e

        bf = ttk.Frame(left)
        bf.pack(fill=tk.X, pady=6)
        ttk.Button(bf, text="Calculate", command=self._calc_single,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Save", command=self._save_single,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear",
                   command=self._clear_single).pack(side=tk.LEFT, padx=4)

        right = ttk.Frame(outer)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=6, pady=6)
        rf = ttk.LabelFrame(right, text="Results", padding=8)
        rf.pack(fill=tk.BOTH, expand=True, pady=4)
        self.result_text = tk.Text(rf, height=12, wrap=tk.WORD,
                                   font=(FONT, 12), bg="#fafafa")
        self.result_text.pack(fill=tk.BOTH, expand=True)

        hf = ttk.LabelFrame(right, text="Recent Tests", padding=6)
        hf.pack(fill=tk.BOTH, expand=True, pady=4)
        cols = ("ID", "Sample ID", "Test", "Result", "Date")
        self.history_tree = ttk.Treeview(hf, columns=cols, show="headings",
                                         height=7, selectmode="extended")
        for c in cols:
            self.history_tree.heading(c, text=c)
            self.history_tree.column(c, width=110)
        sb = ttk.Scrollbar(hf, orient=tk.VERTICAL,
                           command=self.history_tree.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.configure(yscrollcommand=sb.set)
        self.history_tree.pack(fill=tk.BOTH, expand=True)
        self.history_tree.bind("<Double-Button-1>", self._details)

    def _on_test(self, _=None):
        for w in self.params_frame.winfo_children():
            info = w.grid_info()
            if info and int(info.get("row", 0)) > 1:
                w.destroy()
        for ri, (lt, key, dv) in enumerate(self._PARAM_SETS[self.test_var.get()]):
            ttk.Label(self.params_frame, text=lt).grid(
                row=ri + 2, column=0, sticky="w", pady=3)
            e = ttk.Entry(self.params_frame, width=20)
            e.grid(row=ri + 2, column=1, pady=3, padx=4)
            if dv is not None:
                e.insert(0, str(dv))
            self.inputs[key] = e

    def _calc_single(self):
        test = self.test_var.get()
        if not test:
            return messagebox.showwarning("Warning", "Select a test first")
        try:
            if test == "Compressive Strength Test":
                dim = float(self.inputs["cube_dim"].get())
                load = float(self.inputs["load_failure"].get())
                age = int(self.inputs["age"].get())
                mpa = calc.compressive_mpa(dim, load)
                st = "PASS" if mpa >= 20 else "FAIL"
                txt = (f"\n{'='*44}\nCOMPRESSIVE STRENGTH TEST\n{'='*44}\n"
                       f"Cube Dimension : {dim} mm\nLoad at Failure: {load} kN\n"
                       f"Age: {age} days\nCross-section  : {dim} = {dim*dim:.0f} mm\n"
                       f"Compressive Strength = {mpa:.2f} MPa\n"
                       f"Grade : M{int(mpa)}   Status: {st}\n{'='*44}")
                self.current = {"test": test, "result": mpa, "status": st,
                                "dimension": dim, "load": load, "age": age}
            elif test == "Slump Test":
                ih = float(self.inputs["initial_h"].get())
                fh = float(self.inputs["final_h"].get())
                sl = calc.slump_mm(ih, fh)
                wb = calc.slump_class(sl)
                txt = (f"\n{'='*44}\nSLUMP TEST\n{'='*44}\n"
                       f"Initial Height : {ih} mm\nFinal Height : {fh} mm\n"
                       f"Slump : {sl:.1f} mm\nWorkability : {wb}\n{'='*44}")
                self.current = {"test": test, "result": sl, "status": wb,
                                "initial": ih, "final": fh}
            elif test == "Flexural Strength Test":
                b = float(self.inputs["width"].get())
                d = float(self.inputs["depth"].get())
                L = float(self.inputs["span"].get())
                P = float(self.inputs["load"].get())
                fr = calc.flexural_mpa(b, d, L, P)
                st = "PASS" if fr >= 3.5 else "FAIL"
                txt = (f"\n{'='*44}\nFLEXURAL STRENGTH TEST\n{'='*44}\n"
                       f"Width  : {b:.0f} mm   Depth: {d:.0f} mm\n"
                       f"Span   : {L:.0f} mm   Load : {P:.2f} kN\n"
                       f"Flexural Strength = {fr:.3f} MPa   {st}\n{'='*44}")
                self.current = {"test": test, "result": fr, "status": st,
                                "width": b, "depth": d, "span": L, "load": P}
            elif test == "Split Tensile Test":
                dia = float(self.inputs["diameter"].get())
                ln = float(self.inputs["length"].get())
                load = float(self.inputs["load_failure"].get())
                ft = calc.split_tensile_mpa(dia, ln, load)
                st = "PASS" if ft >= 2.0 else "FAIL"
                txt = (f"\n{'='*44}\nSPLIT TENSILE TEST\n{'='*44}\n"
                       f"Diameter : {dia} mm\nLength : {ln} mm\n"
                       f"Load : {load} kN\n"
                       f"Split Tensile Strength = {ft:.3f} N/mm2   {st}\n{'='*44}")
                self.current = {"test": test, "result": ft, "status": st,
                                "diameter": dia, "length": ln, "load": load}
            else:
                return
        except (ValueError, KeyError) as e:
            return messagebox.showerror("Error", str(e))
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, txt)

    def _save_single(self):
        if not hasattr(self, "current"):
            return messagebox.showwarning("Warning", "Calculate first!")
        c = self.current
        self.db.execute(
            """INSERT INTO concrete_tests (test_name, sample_id, date,
               cube_dimension, load_failure, age_days, compressive_strength,
               result_status, technician, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (c["test"], self.inputs["sample_id"].get(),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             c.get("dimension", c.get("diameter", 0)),
             c.get("load", 0), c.get("age", 0),
             c["result"] if "Compressive" in c["test"] else 0,
             c["status"], self.inputs["technician"].get(),
             f"{c['test']} = {c['result']:.2f} {c['status']}"))
        self.db.commit()
        messagebox.showinfo("Saved", f"{c['test']} saved.")
        self._load_history()

    def _clear_single(self):
        for k, e in self.inputs.items():
            if k not in ("sample_id", "technician"):
                e.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        if hasattr(self, "current"):
            del self.current

    def _load_history(self):
        for i in self.history_tree.get_children():
            self.history_tree.delete(i)
        self.db.execute(
            "SELECT id, sample_id, test_name, compressive_strength, notes, date "
            "FROM concrete_tests ORDER BY date DESC LIMIT 40")
        for rid, sid, tn, cs, notes, dt in self.db.fetchall():
            tn = tn or ""
            if "Compressive" in tn and cs:
                try:
                    disp = f"{float(cs):.2f} MPa"
                except (TypeError, ValueError):
                    disp = ""
            else:
                disp = (notes or "")[:30]
            self.history_tree.insert("", "end", values=(rid, sid or "", tn, disp, dt or ""))

    def _details(self, _=None):
        sel = self.history_tree.selection()
        if not sel:
            return
        tid = self.history_tree.item(sel[0])["values"][0]
        self.db.execute("SELECT * FROM concrete_tests WHERE id=?", (tid,))
        d = self.db.fetchone()
        if not d:
            return
        tn = d[1] or ""
        notes = d[10] or ""
        if "Slump" in tn or "Flexural" in tn or "Split" in tn:
            detail = f"Test   : {tn}\nSample : {d[2]}\nDate   : {d[3]}\n{notes}"
        else:
            detail = (f"Test   : {tn}\nSample : {d[2]}\nDate   : {d[3]}\n"
                      f"Strength: {d[7]} MPa\nStatus : {d[8]}")
        messagebox.showinfo("Test Details", detail)

    # ---------- cube subtab ----------
    NUM_CUBES = 8
    GROUP_A = [("#", None, 3), ("Design\nClass", "design_class", 6),
               ("Sample No.", "sample_no", 8), ("Date Cast", "date_cast", 9),
               ("Date Tested", "date_tested", 9), ("Age\n(Days)", "age_days", 5),
               ("Slump\n(mm)", "slump", 5), ("Nominal\n(mm)", "nominal_mm", 8)]
    GROUP_B = [("#", None, 3), ("Measured\n(mm)", "measured_mm", 12),
               ("Loaded\nArea mm2", "loaded_area", 10),
               ("Max Load\n(kN)", "max_load", 7),
               ("Comp. Str\nN/mm2", "comp_str", 10),
               ("Comments", "comments", 20)]
               
    def _export_cube_report(self):
        # collect only rows that have a Sample No.
        samples = []
        for r in self.cu_cells:
            s = {k: r[k].get().strip() for k in r}
            if not s.get("loaded_area"):
                s["loaded_area"] = "22500"
            if s.get("sample_no"):
                samples.append(s)

        if not samples:
            return messagebox.showwarning(
                "Export", "Fill in at least one specimen row (Sample No.) first.")

        header = {
            "project":      self.cu_hdr["cu_project"].get().strip(),
            "date":         self.cu_hdr["cu_date"].get().strip(),
            "test_for":     self.cu_hdr["cu_testfor"].get().strip(),
            "technologist": self.cu_hdr["cu_tech"].get().strip(),
            "cement":       self.cu_hdr["cu_cement"].get().strip(),
            "engineer":     self.cu_hdr["cu_eng"].get().strip(),
            "sand":         self.cu_hdr["cu_sand"].get().strip(),
            "aggregates":   self.cu_hdr["cu_agg"].get().strip(),
            "comments":     samples[0].get("comments", ""),
        }

        path = filedialog.asksaveasfilename(
            title="Save Concrete Cube Report",
            defaultextension=".docx",
            filetypes=[("Word document", "*.docx")],
            initialfile=f"Concrete_Cube_Report_{datetime.now():%Y%m%d_%H%M}.docx",
        )
        if not path:
            return

        try:
            export_concrete_cube_report(path, header, samples)
        except Exception as e:
            return messagebox.showerror("Export failed", str(e))

        messagebox.showinfo("Export", f"Report saved:\n{path}")

    def _build_cube(self, nb):
        outer = ttk.Frame(nb)
        nb.add(outer, text=" Cube Tests")
        banner = tk.Frame(outer, bg="#1f3864", pady=3)
        banner.pack(fill=tk.X)
        tk.Label(banner,
                 text="  Concrete Cube Compressive Strength Test  kN“  BS/EN 12390",
                 bg="#1f3864", fg="white",
                 font=(FONT, 11, "bold")).pack(side=tk.LEFT, padx=10)

        pane = tk.PanedWindow(outer, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED, bg="#aaa")
        pane.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(pane, bg="#f0f0f0")
        pane.add(left, minsize=300, width=700)
        _, inner, _ = scrolled_frame(left)

        right = tk.Frame(pane, bg="#f0f0f0")
        pane.add(right, minsize=300)
        tk.Label(right, text="Stored Cube Test Results", bg="#1f3864",
                 fg="white", font=(FONT, 12, "bold"), pady=6).pack(fill=tk.X)
        _, self.cu_log_tree = self.make_stored_panel(right)
        self.add_delete_bar(right, self.cu_log_tree)
        self.cu_summary = tk.Label(right, text="", bg="#d5f5e3",  font=(FONT, 11, "bold"), anchor="w", padx=8, pady=3)
        self.cu_summary.pack(fill=tk.X)

        self._build_cube_header(inner)
        self._build_cube_table(inner)
        self._build_cube_buttons(inner)
        
        # Load the correct data on startup
        self._refresh_cu_tree()

    def _build_cube_header(self, inner):
        ph = tk.LabelFrame(inner, text="Project Information", font=(FONT, 11, "bold"), bg="#f0f0f0", padx=6, pady=4)
        ph.grid(row=0, column=0, sticky="ew", padx=6, pady=4)
        inner.columnconfigure(0, weight=1)
        fields = [("Project / Location:", "cu_project", 26),
                  ("Date:", "cu_date", 12),
                  ("Test Results For:", "cu_testfor", 26),
                  ("Technologist:", "cu_tech", 18),
                  ("Cement Type:", "cu_cement", 20),
                  ("Resident Engineer:", "cu_eng", 18),
                  ("Sand:", "cu_sand", 18),
                  ("Aggregates:", "cu_agg", 18)]
        self.cu_hdr = {}
        for ri, (lt, key, w) in enumerate(fields):
            r, c = divmod(ri, 2)
            tk.Label(ph, text=lt, bg="#f0f0f0",
                     font=(FONT, 11, "bold")).grid(
                row=r, column=c * 2, sticky="w", padx=4, pady=2)
            e = tk.Entry(ph, width=w, font=(FONT, 11), relief=tk.SUNKEN)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="ew")
            self.cu_hdr[key] = e
        self.cu_hdr["cu_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))

    def _build_cube_table(self, inner):
        cd = tk.LabelFrame(inner, text="Cube Specimen Data", font=(FONT, 11, "bold"), bg="#f0f0f0", padx=4, pady=4)
        cd.grid(row=1, column=0, sticky="ew", padx=6, pady=4)
        CF = (FONT, 10)
        CHDR = (FONT, 10, "bold")

        tk.Label(cd, text="” Specimen Identity ”", bg="#dce6f1",
                 font=(FONT, 10, "italic"), anchor="w").grid(
            row=0, column=0, columnspan=len(self.GROUP_A),
            sticky="ew", padx=1, pady=(0, 1))
        for ci, (h, _, w) in enumerate(self.GROUP_A):
            tk.Label(cd, text=h, bg=C.HDR, font=CHDR, relief=tk.RIDGE,
                     width=w, wraplength=70, justify="center", anchor="center").grid(row=1, column=ci, padx=1, pady=1, sticky="ew")
        COL_OFF = len(self.GROUP_A) + 1
        tk.Label(cd, text="", bg="#f0f0f0", width=1).grid(
            row=0, column=len(self.GROUP_A),
            rowspan=2 + self.NUM_CUBES + 1)
        tk.Label(cd, text="” Measurements & Results ”", bg="#e2efda",
                 font=(FONT, 10, "italic"), anchor="w").grid(
            row=0, column=COL_OFF, columnspan=len(self.GROUP_B),
            sticky="ew", padx=1, pady=(0, 1))
        for ci, (h, _, w) in enumerate(self.GROUP_B):
            tk.Label(cd, text=h, bg="#e2efda", font=CHDR, relief=tk.RIDGE,
                     width=w, wraplength=70, justify="center",
                     anchor="center").grid(row=1, column=COL_OFF + ci,
                                           padx=1, pady=1, sticky="ew")

        self.cu_cells = []
        all_entries = []
        for ri in range(self.NUM_CUBES):
            row_data = {}
            row_entries = []
            tk.Label(cd, text=str(ri + 1), bg="#f8f8f8", font=CF,
                     relief=tk.RIDGE, width=3, anchor="center").grid(
                row=ri + 2, column=0, padx=1, pady=1, sticky="ew")
            for ci, (_, key, w) in enumerate(self.GROUP_A[1:], start=1):
                e = tk.Entry(cd, width=w, font=CF, relief=tk.SUNKEN)
                e.grid(row=ri + 2, column=ci, padx=1, pady=1, sticky="ew")
                row_data[key] = e
                row_entries.append(e)
            tk.Label(cd, text=str(ri + 1), bg="#f8f8f8", font=CF,
                     relief=tk.RIDGE, width=3, anchor="center").grid(
                row=ri + 2, column=COL_OFF, padx=1, pady=1, sticky="ew")
            for ci, (_, key, w) in enumerate(self.GROUP_B[1:], start=1):
                is_calc = key == "comp_str"
                e = tk.Entry(cd, width=w, font=CF,
                             bg=C.CALC if is_calc else "white",
                             relief=tk.SUNKEN, state="normal")
                e.grid(row=ri + 2, column=COL_OFF + ci,
                       padx=1, pady=1, sticky="ew")
                row_data[key] = e
                row_entries.append(e)
            self.cu_cells.append(row_data)
            all_entries.extend(row_entries)

            def _auto_date(row=row_data):
                def _cb(*_):
                    cast_s = row["date_cast"].get().strip()
                    age_s = row["age_days"].get().strip()
                    if not cast_s or not age_s:
                        return
                    try:
                        age = int(age_s)
                        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                            try:
                                dt = datetime.strptime(cast_s, fmt)
                                break
                            except ValueError:
                                continue
                        else:
                            return
                        d = dt + timedelta(days=age)
                        e = row["date_tested"]
                        e.delete(0, tk.END)
                        e.insert(0, d.strftime("%d/%m/%Y"))
                    except (ValueError, KeyError):
                        pass
                return _cb
            cb = _auto_date()
            row_data["date_cast"].bind("<KeyRelease>", cb)
            row_data["age_days"].bind("<KeyRelease>", cb)

        for e in all_entries:
            e.bind("<Tab>", self._tab_next(all_entries, e, 1))
            e.bind("<Shift-Tab>", self._tab_next(all_entries, e, -1))
            e.bind("<Return>", self._tab_next(all_entries, e, 1))

    @staticmethod
    def _tab_next(entries, current, direction):
        def _fn(_):
            try:
                i = entries.index(current)
            except ValueError:
                return "break"
            entries[(i + direction) % len(entries)].focus_set()
            return "break"
        return _fn

    def _build_cube_buttons(self, inner):
        pre = tk.Frame(inner, bg="#ecf0f1", pady=3)
        pre.grid(row=2, column=0, sticky="ew", padx=6, pady=2)
        tk.Label(pre, text="Pre-fill:", bg="#ecf0f1",
                 font=(FONT, 11, "bold")).pack(side=tk.LEFT, padx=6)
        self.cu_class_var = tk.StringVar(value="C25")
        ttk.Combobox(pre, textvariable=self.cu_class_var,
                     values=["C15", "C20", "C25", "C30", "C35", "C40"],
                     width=5, state="readonly").pack(side=tk.LEFT, padx=2)
        ttk.Button(pre, text=" Design Class",
                   command=self._fill_class).pack(side=tk.LEFT, padx=4)
        ttk.Button(pre, text=" Loaded Area (22500)",
                   command=lambda: self._fill_col("loaded_area", "22500")
                   ).pack(side=tk.LEFT, padx=4)
        ttk.Button(pre, text=" Measured (150mm*150mm*150mm)",
                   command=lambda: self._fill_col("measured_mm", "150mm*150mm*150mm")
                   ).pack(side=tk.LEFT, padx=4)

        bf = tk.Frame(inner, bg="#f0f0f0")
        bf.grid(row=3, column=0, sticky="w", padx=6, pady=6)
        ttk.Button(bf, text=" Calculate Strengths",
                   command=self._calc_cubes,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=" Save All to Log",
                   command=self._save_cubes,
                   style="Success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Clear",
                   command=self._clear_cubes).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text=" Export Report",command=self._export_cube_report).pack(side=tk.LEFT, padx=4)

    def _fill_class(self):
        for r in self.cu_cells:
            r["design_class"].delete(0, tk.END)
            r["design_class"].insert(0, self.cu_class_var.get())

    def _fill_col(self, key, val):
        for r in self.cu_cells:
            if not r[key].get():
                r[key].delete(0, tk.END)
                r[key].insert(0, val)

    def _calc_cubes(self):
        for r in self.cu_cells:
            try:
                load = get_float(r["max_load"])
                area = float(r["loaded_area"].get().strip() or "22500")
                if load and area > 0:
                    s = calc.cube_strength_mpa(load, area)
                    set_val(r["comp_str"], f"{s:.0f}")
            except Exception:
                pass

    def _save_cubes(self):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        project = self.cu_hdr["cu_project"].get()
        saved = 0
        for r in self.cu_cells:
            sno = r["sample_no"].get().strip()
            if not sno:
                continue
            
            # Get values from the table
            load = get_float(r["max_load"]) or 0
            comp_str = get_float(r["comp_str"]) or 0
            age = get_float(r["age_days"]) or 0
            
            # 1. Save to the actual database table the Dashboard reads
            self.db.execute(
                """INSERT INTO concrete_tests (test_name, sample_id, date,
                   cube_dimension, load_failure, age_days, compressive_strength,
                   result_status, technician, notes)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                ("Cube Test", sno, ts, 150, load, age, comp_str,
                 "PASS" if comp_str >= 20 else "FAIL", 
                 self.cu_hdr.get("cu_tech", tk.Entry()).get() if hasattr(self.cu_hdr.get("cu_tech", None), "get") else "",
                 f"Class: {r['design_class'].get()}")
            )
            # 2. CRITICAL: Commit the data to the DB!
            self.db.commit()
            
            # (Optional) Keep your old log store behavior too
            data = {k: r[k].get() for k in r}
            data["project"] = project
            data["stored_at"] = ts
            self.log_store.save(
                self.log_category,
                f"{sno} | {data.get('design_class','')} | {data.get('date_cast','')}",
                data)
            saved += 1
            
        # Use the custom refresh method to fix the columns
        self._refresh_cu_tree()
        
        if hasattr(self.cu_log_tree, '_refresh_count'):
            self.cu_log_tree._refresh_count()
            
        vals = [get_float(r["comp_str"]) for r in self.cu_cells
                if get_float(r["comp_str"]) is not None]
        if vals:
            self.cu_summary.config(
                text=f"Saved {saved} specimen(s)  |  "
                     f"Avg: {sum(vals)/len(vals):.1f}  Min: {min(vals):.0f}  "
                     f"Max: {max(vals):.0f} N/mm2  [{ts}]")
        messagebox.showinfo("Saved", f"{saved} specimen(s) saved to database.")

    def _refresh_cu_tree(self):
        """Custom refresh function to extract JSON data and prevent column shifting."""
        if not hasattr(self, 'cu_log_tree'):
            return
            
        for item in self.cu_log_tree.get_children():
            self.cu_log_tree.delete(item)
            
        try:
            self.db.execute("SELECT data_json FROM test_log WHERE category=? ORDER BY id DESC", (self.log_category,))
            for row in self.db.fetchall():
                if not row or not row[0]:
                    continue
                try:
                    data = json.loads(row[0])
                    vals = (
                        data.get("sample_no", ""),
                        data.get("design_class", ""),
                        data.get("date_cast", ""),
                        data.get("age_days", ""),
                        data.get("max_load", ""),
                        data.get("comp_str", "")
                    )
                    self.cu_log_tree.insert("", "end", values=vals)
                except Exception:
                    pass
        except Exception:
            pass

    def _clear_cubes(self):
        for r in self.cu_cells:
            for e in r.values():
                e.config(state="normal")
                e.delete(0, tk.END)
                if e.cget("bg") == C.CALC:
                    e.config(state="readonly")