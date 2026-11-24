"""The main application — pure wiring, no test logic."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")

from .config import APP_TITLE, WINDOW_SIZE, C, FONT
from .data.database import Database
from .data.log_store import LogStore
from .ui.styles import install_styles

# ---- Real tabs -------------------------------------------------------------
from .tests.dashboard_tab import DashboardTab
from .tests.concrete_tab import ConcreteTab
from .tests.soil_tabs import (AtterbergTab, CompactionTab, PsdTab,
                              CbrTab, FieldDensityTab, StabilizationTab)
from .tests.soil_report_tab import SoilReportTab
from .ui.aggregate_tabs import ( MoistureContentTab, RelativeDensityTab, 
                                 FlakinessTab, ElongationTab, AcvTab, 
                                 TfvTab, AivTab, LaaTab, FineAggregateTab, 
                                 AggregateReportTab, CoarsePropertiesTab )
from .tests.asphalt_tabs import (ExtractionTab, MarshallTab, GmmTab,
                                 CoreDensityTab, SprayRateTab, SpecificGravityTab)


class CeltisApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg="#e8e8e8")

        # data layer
        self.db = Database().connect()
        self.log_store = LogStore(self.db)

        # shared state between tabs (Proctor MDD/OMC, etc.)
        self.session = {}
        # registry: log_category -> tab instance
        self.tabs = {}

        install_styles()
        self._build_header()
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self._install_tabs()
        self._build_status_bar()
        self._bind_nav()
        
        # 👇 ADDED: Bind the tab change event to refresh the dashboard
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    # ---------- chrome ----------
    def _build_header(self):
        h = tk.Frame(self.root, bg=C.PRIMARY, pady=8)
        h.pack(fill=tk.X)
        tk.Label(h, text=f"🏗️  {APP_TITLE}",
                 bg=C.PRIMARY, fg="white",
                 font=(FONT, 18, "bold")).pack(side=tk.LEFT, padx=12)
        self.clock = tk.Label(h, bg=C.PRIMARY, fg="#ecf0f1",
                              font=(FONT, 12))
        self.clock.pack(side=tk.RIGHT, padx=12)
        self._tick()

    def _tick(self):
        self.clock.config(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.root.after(1000, self._tick)

    def _build_status_bar(self):
        bf = tk.Frame(self.root, bg="#1a1a2e", height=28)
        bf.pack(side=tk.BOTTOM, fill=tk.X)
        bf.pack_propagate(False)
        self.status = tk.Label(bf, text="Civil Engineering Laboratory System",
                               bg="#1a1a2e", fg="#a0aec0",
                               font=(FONT, 11), anchor="w")
        self.status.pack(side=tk.LEFT, padx=10)
        tk.Label(bf, text=f"© 2025 {APP_TITLE}",
                 bg="#1a1a2e", fg="#718096",
                 font=(FONT, 10)).pack(side=tk.LEFT, expand=True)
        tk.Label(bf, text="✅ Database Connected", bg="#212137", fg="#4a5568",
                 font=(FONT, 10)).pack(side=tk.RIGHT, padx=10)

    def _bind_nav(self):
        nb = self.notebook

        def _nav(delta):
            nb.select((nb.index(nb.select()) + delta) % nb.index("end"))
            return "break"

        self.root.bind_all("<Control-Tab>",       lambda e: _nav(1))
        self.root.bind_all("<Control-Shift-Tab>", lambda e: _nav(-1))
        self.root.bind_all("<Alt-Right>",         lambda e: _nav(1))
        self.root.bind_all("<Alt-Left>",          lambda e: _nav(-1))
        for i in range(1, 10):
            self.root.bind_all(
                f"<Control-Key-{i}>",
                lambda e, n=i: nb.select(n - 1) if n <= nb.index("end") else None)

    # 👇 ADDED: This method triggers the dashboard refresh
    def _on_tab_changed(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        # When the user clicks the Dashboard tab, refresh it
        if "Dashboard" in tab_text:
            dashboard = self.tabs.get("dashboard")
            if dashboard and hasattr(dashboard, "refresh"):
                dashboard.refresh()

    # ---------- tabs ----------
    def _install_tabs(self):
        # ---- top level ----
        self._register(DashboardTab(self.notebook, self), "dashboard")
        self._register(ConcreteTab(self.notebook, self), "concrete")

        # ---- soil group ----
        soil_nb = self._group(" Soil Tests")
        self._register(AtterbergTab(soil_nb, self), "atterberg")
        self._register(CompactionTab(soil_nb, self), "compaction")
        self._register(PsdTab(soil_nb, self), "psd")
        self._register(CbrTab(soil_nb, self), "cbr")
        self._register(FieldDensityTab(soil_nb, self), "field_density")
        self._register(StabilizationTab(soil_nb, self), "stabilization")

        #  Asphalt group 
        asph_nb = self._group("🛣️ Asphalt Tests")
        self._register(ExtractionTab(asph_nb, self), "asphalt_extraction")
        self._register(MarshallTab(asph_nb, self), "asphalt_marshall")
        self._register(GmmTab(asph_nb, self), "asphalt_gmm")
        self._register(CoreDensityTab(asph_nb, self), "core_density")
        self._register(SprayRateTab(asph_nb, self), "spray_rate")
        self._register(SpecificGravityTab(asph_nb, self), "specific_gravity")

        #Aggregate 
        agg_nb = self._group("🪨 Aggregate Tests")
        self._register(MoistureContentTab(agg_nb, self), "agg_moisture")
        self._register(RelativeDensityTab(agg_nb, self), "agg_rd")
        self._register(FlakinessTab(agg_nb, self), "agg_fi")
        self._register(ElongationTab(agg_nb, self), "agg_ei")
        self._register(AcvTab(agg_nb, self), "agg_acv")
        self._register(TfvTab(agg_nb, self), "agg_tfv")
        self._register(AivTab(agg_nb, self), "agg_aiv")
        self._register(LaaTab(agg_nb, self), "agg_laa")
        self._register(FineAggregateTab(agg_nb, self), "fine_aggregate")
        self._register(AggregateReportTab(agg_nb, self), "agg_report")
        self._register(CoarsePropertiesTab(agg_nb, self), "coarse_properties")

        # ---- report tab ----
        self._register(SoilReportTab(self.notebook, self), "soil_report")

    # ---------- helpers ----------
    def _register(self, tab, category):
        cat = getattr(tab, "log_category", None) or category
        self.tabs[cat] = tab
        return tab

    def _group(self, label):
        outer = ttk.Frame(self.notebook)
        self.notebook.add(outer, text=label)
        nb = ttk.Notebook(outer)
        nb.pack(fill=tk.BOTH, expand=True)
        return nb

    def _placeholder_group(self, group_nb, labels):
        for label, category in labels:
            f = ttk.Frame(group_nb, padding=20)
            group_nb.add(f, text=label)
            ttk.Label(f, text=f"⚙️  '{label}' — to be migrated",
                      font=(FONT, 14, "bold")).pack(pady=20)
            ttk.Label(
                f,
                text=("Copy the original _build_* method body into a\n"
                      "BaseTab subclass in celtis/tests/ — see the\n"
                      "ConcreteTab and AtterbergTab pattern."),
                font=(FONT, 11), justify="center",
            ).pack()
            self.tabs[category] = f