"""One module per notebook tab.

Each tab subclasses `celtis.ui.base_tab.BaseTab` and lives in its own
module so it can be developed, reviewed, and (if it ever grows) split
further without touching unrelated tabs.
"""

# Concrete
from .dashboard_tab import DashboardTab
from .concrete_tab import ConcreteTab

# Soil
from .soil_tabs import (AtterbergTab, CompactionTab, PsdTab, CbrTab, FieldDensityTab, StabilizationTab)

# Reports / dashboard-style tabs
from .soil_report_tab import SoilReportTab

__all__ = [
    "DashboardTab",
    "ConcreteTab",
    "AtterbergTab",
    "CompactionTab",
    "PsdTab",
    "CbrTab",
    "FieldDensityTab",
    "StabilizationTab",
    "SoilReportTab",
]