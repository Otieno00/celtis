"""Single entry point for all report exports."""
from .soil_report_pdf  import export_soil_report_pdf
from .soil_report_docx import export_soil_report_docx
from .concrete_report  import export_concrete_cube_report
from .concrete_pdf     import export_concrete_cube_report_pdf

# test_type -> { format -> function }
REPORTS = {
    "soil": {
        "docx": export_soil_report_docx,
        "pdf":  export_soil_report_pdf,
    },
    "concrete_cube": {
        "docx": export_concrete_cube_report,
        "pdf":  export_concrete_cube_report_pdf,
    },
}


def export_report(test_type, fmt, path, header, rows):
    """Dispatch to the right exporter.

    test_type: 'soil' or 'concrete_cube'
    fmt:       'docx' or 'pdf'
    """
    try:
        fn = REPORTS[test_type][fmt]
    except KeyError:
        available = {k: sorted(v) for k, v in REPORTS.items()}
        raise ValueError(
            f"No {fmt!r} report for test type {test_type!r}. "
            f"Available: {available}"
        )
    return fn(path, header, rows)