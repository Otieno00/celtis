"""CELTIS — Civil Engineering Laboratory Tests Information System.

Package layout
--------------
celtis.config          Constants, colours, DB schema
celtis.core            Pure calculation functions (no tkinter)
celtis.data            Persistence: DB, log store, Excel/CSV I/O
celtis.ui              Reusable tkinter widgets, styles, BaseTab
celtis.tests           One module per notebook tab
celtis.reports         PDF / DOCX exporters
"""

__version__ = "1.0.0"
__app_name__ = "Civil Engineering Laboratory Tests Information System"
__app_title__ = f"{__app_name__} v {__version__}"
__author__ = "CELTIS"

__all__ = ["__version__", "__app_name__", "__app_title__", "__author__"]