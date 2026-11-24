"""Excel / CSV import-export and backup/restore helpers."""
import csv
import os
import shutil
from tkinter import filedialog, messagebox

import pandas as pd

from ..config import DB_FILENAME


def export_excel(db):
    fn = filedialog.asksaveasfilename(
        defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
        initialfile="lab_data_export.xlsx")
    if not fn:
        return
    try:
        with pd.ExcelWriter(fn, engine="openpyxl") as w:
            for t in ["concrete_tests", "soil_tests",
                      "asphalt_tests", "aggregate_tests"]:
                pd.read_sql_query(f"SELECT * FROM {t}", db.conn).to_excel(
                    w, sheet_name=t, index=False)
        messagebox.showinfo("Success", f"Exported: {fn}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def import_excel(db):
    fn = filedialog.askopenfilename(
        filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")])
    if not fn:
        return
    try:
        if fn.endswith(".xlsx"):
            for t in ["concrete_tests", "soil_tests",
                      "asphalt_tests", "aggregate_tests"]:
                try:
                    pd.read_excel(fn, sheet_name=t).to_sql(
                        t, db.conn, if_exists="append", index=False)
                except Exception:
                    pass
            db.commit()
        messagebox.showinfo("Success", "Data imported!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def backup_db():
    fn = filedialog.asksaveasfilename(
        defaultextension=".db", filetypes=[("DB", "*.db")],
        initialfile="lab_backup.db")
    if not fn:
        return
    try:
        shutil.copy2(DB_FILENAME, fn)
        messagebox.showinfo("OK", "Backed up.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def restore_db(db):
    fn = filedialog.askopenfilename(filetypes=[("DB", "*.db")])
    if not fn:
        return
    try:
        db.close()
        shutil.copy2(fn, DB_FILENAME)
        db.reopen()
        messagebox.showinfo("OK", "Database restored.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def import_csv_preview():
    fn = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("All", "*.*")])
    if not fn:
        return
    try:
        with open(fn, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            messagebox.showinfo("Empty", "No data found in file.")
            return
        messagebox.showinfo(
            "Import Preview",
            f"File: {os.path.basename(fn)}\nRows: {len(rows)}\n"
            f"Columns: {', '.join(rows[0].keys())}")
    except Exception as e:
        messagebox.showerror("Import Error", str(e))


def export_csv_report(db):
    fn = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV", "*.csv")],
        initialfile="lab_export.csv")
    if not fn:
        return
    try:
        rows = []
        for tbl in ["concrete_tests", "soil_tests",
                    "asphalt_tests", "aggregate_tests"]:
            cur = db.execute(f"SELECT * FROM {tbl}")
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                d = dict(zip(cols, row))
                d["_table"] = tbl
                rows.append(d)
        if not rows:
            messagebox.showinfo("Empty", "No data to export.")
            return
        with open(fn, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        messagebox.showinfo("Exported", f"{len(rows)} records exported.")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))