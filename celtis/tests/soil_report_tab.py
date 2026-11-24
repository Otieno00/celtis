"""The Lab Test Report tab. Delegates PDF/DOCX export to reports/."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from ..ui.base_tab import BaseTab
from ..ui.widgets import entry, calc_entry, scrolled_frame, get_float
from ..reports import export_soil_report_pdf, export_soil_report_docx


class SoilReportTab(BaseTab):
    tab_label = "📋 Lab Test Report"
    log_category = "soil_report"

    COL_DEFS = [("SAMPLE\nREFERENCE", "ref", 20),
                ("% Pass\n20mm", "p20", 10), ("% Pass\n10mm", "p10", 10),
                ("% Pass\n5mm", "p5", 10), ("% Pass\n2mm", "p2", 10),
                ("% Pass\n0.425mm", "p0425", 10),
                ("% Pass\n0.075mm", "p0075", 10),
                ("LL\n%", "ll", 10), ("PL\n%", "pl", 10), ("PI\n%", "pi", 10),
                ("LS\n%", "ls", 10), ("PM\n%", "pm", 10),
                ("MDD\nKg/m³", "mdd", 10), ("OMC\n%", "omc", 10),
                ("CBR\n4-day\nSoak%", "cbr", 10), ("Swell\n %", "swell", 6)]
    NUM_SAMPLES = 10

    def build(self):
        self._build_banner()
        self._build_actions()
        self._build_header()
        self._build_preview()
        self._build_rows()

    def _build_banner(self):
        b = tk.Frame(self, bg="#2c3e50", pady=4)
        b.pack(fill=tk.X)
        tk.Label(b,
                 text="⚡  All fields are auto-filled from the other test tabs. "
                      "Press 🔄 Refresh after each test.",
                 bg="#2c3e50", fg="#ecf0f1",
                 font=("Times New Roman", 12, "bold")).pack(side=tk.LEFT, padx=10)

    def _build_actions(self):
        f = tk.Frame(self, bg="#ecf0f1", pady=5)
        f.pack(fill=tk.X, padx=6, pady=2)
        ttk.Button(f, text="🔄 Refresh All Fields",
                   command=self.autofill,
                   style="Primary.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(f, text="➕ Snapshot → Add Row",
                   command=self.snapshot).pack(side=tk.LEFT, padx=6)
        ttk.Button(f, text="🗑 Clear All Rows",
                   command=self.clear_rows).pack(side=tk.LEFT, padx=6)
        ttk.Button(f, text="📄 Export (PDF)",
                   command=self.export_pdf,
                   style="Success.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(f, text="📄 Export (Word)",
                   command=self.export_docx,
                   style="Success.TButton").pack(side=tk.LEFT, padx=6)

    def _build_header(self):
        f = tk.LabelFrame(self, text="Report Header", bg="#f0f0f0", font=("Times New Roman", 12, "bold"), padx=6, pady=5)
        f.pack(fill=tk.X, padx=8, pady=4)
        fields = [("Project / Description:", "rpt_project", 32),
                  ("Location / Chainage:", "rpt_location", 32),
                  ("Client:", "rpt_client", 24), ("Date:", "rpt_date", 16),
                  ("Project Technologist:", "rpt_tech", 24),
                  ("Resident Engineer:", "rpt_engineer", 24),
                  ("NB – Topsoil (m):", "rpt_topsoil", 10),
                  ("NB – Proposed Depth (m):", "rpt_depth", 10)]
        self.hdr = {}
        for ri, (lt, key, w) in enumerate(fields):
            r, c = divmod(ri, 2)
            tk.Label(f, text=lt, bg="#f0f0f0",
                     font=("Times New Roman", 12, "bold")).grid(
                row=r, column=c * 2, sticky="w", padx=6, pady=2)
            e = entry(f, w=w)
            e.grid(row=r, column=c * 2 + 1, padx=4, pady=2, sticky="w")
            self.hdr[key] = e
        self.hdr["rpt_date"].insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.hdr["rpt_topsoil"].insert(0, "0.3")
        self.hdr["rpt_depth"].insert(0, "1.8")

    def _build_preview(self):
        f = tk.LabelFrame(self, text="Current Test Preview", bg="#e8f5e9",
                          font=("Times New Roman", 12, "bold"),
                          padx=4, pady=4)
        f.pack(fill=tk.X, padx=8, pady=2)
        for ci, (h, _, w) in enumerate(self.COL_DEFS):
            tk.Label(f, text=h, bg="#cce5ff",
                     font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=w, wraplength=55, justify="center",
                     anchor="center").grid(row=0, column=ci, padx=1, pady=1,
                                           sticky="ew")
        self.preview = {}
        for ci, (_, key, w) in enumerate(self.COL_DEFS):
            e = calc_entry(f, w=w)
            e.config(state="normal")
            e.grid(row=1, column=ci, padx=1, pady=1, sticky="ew")
            self.preview[key] = e
        self.prev_comp = tk.StringVar()
        tk.Entry(f, textvariable=self.prev_comp,
                 font=("Times New Roman", 12, "italic"), bg="#fffde7",
                 relief=tk.FLAT).grid(row=2, column=0, columnspan=len(self.COL_DEFS), padx=1, pady=1, sticky="ew")

    def _build_rows(self):
        outer, inner, _ = scrolled_frame(self)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        f = tk.LabelFrame(inner, text="Accumulated Sample Rows", bg="#f0f0f0",
                          font=("Times New Roman", 12, "bold"), padx=4, pady=4)
        f.pack(fill=tk.X, padx=4, pady=4)
        for ci, (h, _, w) in enumerate(self.COL_DEFS):
            tk.Label(f, text=h, bg="#cce5ff", font=("Times New Roman", 12, "bold"), relief=tk.RIDGE,
                     width=w, wraplength=55, justify="center",
                     anchor="center").grid(row=0, column=ci, padx=1, pady=1, sticky="ew")
        self.rows = []
        for ri in range(self.NUM_SAMPLES):
            rd = {}
            for ci, (_, key, w) in enumerate(self.COL_DEFS):
                e = entry(f, w=w)
                e.grid(row=ri * 2 + 1, column=ci, padx=1, pady=1, sticky="ew")
                rd[key] = e
            comp_var = tk.StringVar()
            tk.Entry(f, textvariable=comp_var,
                     font=("Times New Roman", 12, "italic"), bg="#fffde7",
                     relief=tk.FLAT).grid(row=ri * 2 + 2, column=0, columnspan=len(self.COL_DEFS), padx=1, pady=0, sticky="ew")
            rd["comp_var"] = comp_var
            self.rows.append(rd)
        self._next_row = 0

    def _set(self, key, val):
        e = self.preview.get(key)
        if e is None:
            return
        e.config(state="normal")
        e.delete(0, tk.END)
        if val not in (None, ""):
            e.insert(0, str(val).strip())

    def _pp(self, sv):
        psd = getattr(self.app, "tabs", {}).get("psd")
        if psd is None:
            return ""
        e = psd.psd_cells.get((sv, "pass"))
        v = e.get() if e else ""
        try:
            return f"{float(v):.0f}" if "." in v else v
        except Exception:
            return v

    def autofill(self):
        self._set("p20", self._pp("20"))
        self._set("p10", self._pp("10"))
        self._set("p5", self._pp("5"))
        self._set("p2", self._pp("2"))
        self._set("p0425", self._pp("0.425"))
        self._set("p0075", self._pp("0.075"))

        att = self.app.tabs.get("atterberg")
        ll_v = pl_v = ls_v = None
        if att is not None:
            ll_v = get_float(att.sum_ll)
            pl_v = get_float(att.sum_pl)
            ls_v = get_float(att.ls_result)
        self._set("ll", f"{ll_v:.0f}" if ll_v is not None else "")
        self._set("pl", f"{pl_v:.0f}" if pl_v is not None else "")
        if ll_v is not None and pl_v is not None:
            self._set("pi", f"{ll_v - pl_v:.0f}")
        self._set("ls", f"{ls_v:.1f}" if ls_v is not None else "")

        try:
            p0425_v = float(self._pp("0.425") or 0)
        except ValueError:
            p0425_v = 0
        if ll_v is not None and pl_v is not None and p0425_v:
            self._set("pm", f"{(ll_v - pl_v) * p0425_v:.1f}")

        comp = self.app.tabs.get("compaction")
        mdd = getattr(comp, "_proctor_mdd", None) if comp else None
        omc = getattr(comp, "_proctor_omc", None) if comp else None
        self._set("mdd", f"{mdd:.0f}" if mdd is not None else "")
        self._set("omc", f"{omc:.1f}" if omc is not None else "")

        cbr_t = self.app.tabs.get("cbr")
        cbr_best = None
        if cbr_t is not None:
            for blows in [62, 30, 10]:
                for pk in (f"cbr_val25_{blows}", f"cbr_val50_{blows}"):
                    v = get_float(cbr_t.cbr_sum.get(pk))
                    if v is not None and (cbr_best is None or v > cbr_best):
                        cbr_best = v
        self._set("cbr", f"{cbr_best:.0f}" if cbr_best is not None else "")

        # reference
        psd = self.app.tabs.get("psd")
        ref = ""
        if psd and getattr(psd, "psd_info", None):
            ref = psd.psd_info["psd_sno"].get()
        self._set("ref", ref)
        self.prev_comp.set(getattr(psd, "_psd_comp_str", "") if psd else "")

    def snapshot(self):
        if self._next_row >= len(self.rows):
            return messagebox.showwarning("Full", "All rows used.")
        row = self.rows[self._next_row]
        for key in self.preview:
            row[key].delete(0, tk.END)
            row[key].insert(0, self.preview[key].get())
        row["comp_var"].set(self.prev_comp.get())
        self._next_row += 1
        messagebox.showinfo("Added", f"Row {self._next_row} saved.")

    def clear_rows(self):
        for row in self.rows:
            for k, w in row.items():
                if k == "comp_var":
                    w.set("")
                else:
                    w.delete(0, tk.END)
        self._next_row = 0
        for e in self.preview.values():
            e.config(state="normal"); e.delete(0, tk.END)

    def _collect_rows(self):
        out = []
        for r in self.rows:
            ref = r["ref"].get().strip()
            if not ref:
                continue
            d = {k: r[k].get().strip() for k in
                 ("ref", "p20", "p10", "p5", "p2", "p0425", "p0075", "ll", "pl", "pi", "ls", "pm", "mdd", "omc", "cbr", "swell")}
            d["comp"] = r["comp_var"].get().strip()
            out.append(d)
        return out

    def _collect_header(self):
        return {k: e.get().strip() for k, e in self.hdr.items()}

    def export_pdf(self):
        fn = filedialog.asksaveasfilename( defaultextension=".pdf", filetypes=[("PDF", "*.pdf")], initialfile="Laboratory_Test_Report.pdf")
        if not fn:
            return
        export_soil_report_pdf(fn, header=self._collect_header(), rows=self._collect_rows())
        messagebox.showinfo("Saved", f"Report saved:\n{fn}")

    def export_docx(self):
        fn = filedialog.asksaveasfilename( defaultextension=".docx",  filetypes=[("Word Document", "*.docx")], initialfile="Laboratory_Test_Report.docx")
        if not fn:
            return
        export_soil_report_docx(fn, header=self._collect_header(), rows=self._collect_rows())
        messagebox.showinfo("Saved", f"Report saved:\n{fn}")