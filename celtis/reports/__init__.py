"""Report exporters.

Each `export_*` function takes plain data (a header dict + a list of
row dicts) and a destination path, and writes a PDF or DOCX file.
No tkinter, no database access — so they are trivially testable and
can be reused from a CLI, a web service, or a batch job.
"""

from .soil_report_pdf  import export_soil_report_pdf
from .soil_report_docx import export_soil_report_docx
from .concrete_report  import export_concrete_cube_report
from .concrete_pdf     import export_concrete_cube_report_pdf
from .export_report    import REPORTS, export_report


__all__ = [
    "export_soil_report_pdf",
    "export_soil_report_docx",
    "export_concrete_cube_report",
    "export_concrete_cube_report_pdf",
    "REPORTS",
    "export_report",
]