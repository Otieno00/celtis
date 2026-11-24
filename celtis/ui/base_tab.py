import json
import tkinter as tk
from tkinter import ttk, messagebox

from ..config import FONT


class BaseTab(ttk.Frame):
    tab_label = "Tab"
    log_category = None
    log_columns = ()

    def __init__(self, notebook, app):
        super().__init__(notebook)
        self.app = app
        self.db = app.db
        self.log_store = app.log_store
        self.notebook = notebook
        notebook.add(self, text=self.tab_label)
        self.build()

    def build(self):
        raise NotImplementedError

    # ---------- log panel helpers ----------
    def save_to_log(self, label, data):
        return self.log_store.save(self.log_category, label, data)

    def make_stored_panel(self, parent, columns=None, load_cb=None):
        columns = columns or self.log_columns
        f = tk.Frame(parent, bg="#f0f0f0")
        f.pack(fill=tk.BOTH, expand=True)
        btn_row = tk.Frame(f, bg="#f0f0f0")
        btn_row.pack(fill=tk.X, pady=2)
        count = tk.Label(btn_row, text="", bg="#f0f0f0",
                         font=(FONT, 12, "italic"), fg="#555")
        count.pack(side=tk.RIGHT, padx=8)

        keys = [c[0] for c in columns]
        heads = [c[1] for c in columns]
        widths = [c[2] for c in columns]

        tree = ttk.Treeview(f, columns=keys, show="headings",
                            selectmode="extended")
        for i, key in enumerate(keys):
            tree.heading(key, text=heads[i])
            tree.column(key, width=widths[i] if i < len(widths) else 100)
        vsb = ttk.Scrollbar(f, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        def _refresh(_=None):
            n = len(tree.get_children())
            count.config(text=f"{n} record{'s' if n != 1 else ''}")
        tree._refresh_count = _refresh
        tree.bind("<<TreeviewSelect>>", _refresh)
        if load_cb:
            tree.bind("<Double-Button-1>", load_cb)

        self.reload_log(tree)
        _refresh()
        return f, tree

    def reload_log(self, tree):
        for iid in tree.get_children():
            tree.delete(iid)
        keys = [c[0] for c in self.log_columns]
        for rid, ts, label, js in self.log_store.load(self.log_category):
            data = json.loads(js) if js else {}
            tree.insert("", "end", iid=str(rid),
                        values=[ts, label or ""]
                               + [str(data.get(k, "")) for k in keys])

    def add_delete_bar(self, parent, tree):
        bf = tk.Frame(parent, bg="#f8f8f8")
        bf.pack(fill=tk.X, pady=(0, 2))
        ttk.Button(bf, text="🗑 Delete Selected",
                   command=lambda: self._del(tree, "selected")
                   ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="⚠️ Delete All",
                   command=lambda: self._del(tree, "all")
                   ).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="🔄 Refresh",
                   command=lambda: (self.reload_log(tree),
                                    tree._refresh_count())
                   ).pack(side=tk.LEFT, padx=4)

    def _del(self, tree, mode):
        if mode == "selected":
            sel = tree.selection()
            if not sel:
                return messagebox.showwarning("Select", "Select rows first.")
            label = f"{len(sel)} selected row(s)"
            ids = [int(iid) for iid in sel]
        else:
            children = tree.get_children()
            if not children:
                return messagebox.showinfo("Empty", "Nothing to delete.")
            label = f"ALL {len(children)} record(s)"
            ids = None
        if not messagebox.askyesno("Confirm", f"Delete {label}?"):
            return
        if ids is None:
            self.log_store.delete_all(self.log_category)
        else:
            for rid in ids:
                self.log_store.delete(rid)
        self.reload_log(tree)
        tree._refresh_count()

    @staticmethod
    def bind_enter_down(entries, calc_func=None):
        """Enter key moves focus to the next entry in the list, or fires calc."""
        if not entries:
            return

        def _next(event, i):
            n = len(entries)
            j = (i + 1) % n
            for _ in range(n):
                e = entries[j]
                try:
                    if e["state"] not in ("readonly", "disabled"):
                        e.focus_set()
                        e.select_range(0, "end")
                        break
                except Exception:
                    pass
                j = (j + 1) % n
            if calc_func:
                entries[0].after_idle(calc_func)
            return "break"

        for i, e in enumerate(entries):
            e.bind("<Return>", lambda ev, idx=i: _next(ev, idx))