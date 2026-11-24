"""Word export for concrete cube reports. Pure function of data -> file."""
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


_SECTION_ROWS = {0, 3, 7, 12, 19}
_VALUE_SPAN_ROWS = {4, 5, 6, 14, 16}


def export_concrete_cube_report(path, header, samples):
    header = header or {}
    samples = list(samples or [])
    n = len(samples)
    cols = n + 1

    def g(s, k, default=""):
        return s.get(k, default) if s else default

    def row(label, values=None):
        if values is None:
            values = [""] * n
        values = (list(values) + [""] * n)[:n]
        return [label] + values

    first = samples[0] if samples else {}

    rows = [
        row("Concrete Cube Making"),
        row("Design Concrete Class*", [g(s, "design_class") for s in samples]),
        row("Date Casted",            [g(s, "date_cast")    for s in samples]),
        row("Material Source"),
        row(f"Cement; {header.get('cement','')}"),
        row(f"SAND: {header.get('sand','')}"),
        row(f"Aggregates: {header.get('aggregates','')}"),
        row("TEST REQUIREMENTS/RESULTS"),
        row("Sample No.",              [g(s, "sample_no")   for s in samples]),
        row("Date tested",             [g(s, "date_tested") for s in samples]),
        row("Slump (mm)",              [g(s, "slump")       for s in samples]),
        row("Age at crushing Test (Days)", [g(s, "age_days") for s in samples]),
        row("Sample Dimensions"),
        row("Nominal (mm)",            [first.get("nominal_mm", "")]),
        row("Measured (mm)",           [first.get("measured_mm", "")]),
        row("Saturated Density (Kg/m³)"),
        row("Loaded Area (mm²)",       [first.get("loaded_area", "")]),
        row("Maximum Load (KN)",       [g(s, "max_load")    for s in samples]),
        row("Compressive Strength (N/mm²)", [g(s, "comp_str") for s in samples]),
        row("Comments"),
    ]

    doc = Document()
    title = doc.add_paragraph("LABORATORY TEST REPORT")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(16)

    sub = doc.add_paragraph(header.get("test_for") or "CONCRETE CUBE TEST RESULTS")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.runs[0].bold = True
    sub.runs[0].font.size = Pt(12)
    doc.add_paragraph()

    t = doc.add_table(rows=len(rows), cols=cols)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, r in enumerate(rows):
        for j, val in enumerate(r):
            c = t.cell(i, j)
            c.text = "" if val is None else str(val)
            c.paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.LEFT if j == 0
                else WD_ALIGN_PARAGRAPH.CENTER)

    if cols > 1:
        for i in _SECTION_ROWS:
            if i >= len(rows):
                continue
            a, b = t.cell(i, 0), t.cell(i, cols - 1)
            if a._tc is not b._tc:
                a.merge(b)
        for i in _VALUE_SPAN_ROWS:
            if i >= len(rows):
                continue
            a, b = t.cell(i, 1), t.cell(i, cols - 1)
            if a._tc is not b._tc:
                a.merge(b)

    for i in range(len(rows)):
        for j in range(cols):
            cell = t.cell(i, j)
            for p in cell.paragraphs:
                for run in p.runs:
                    run.font.size = Pt(9)
                    if j == 0:
                        run.bold = True

    doc.add_paragraph()
    sig = doc.add_table(rows=2, cols=2)
    sig.style = "Table Grid"
    sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig.rows[0].cells[0].text = header.get("technologist") or "Project Material Technologist"
    sig.rows[0].cells[1].text = header.get("engineer") or "Resident Engineer"
    for c in (0, 1):
        if sig.rows[0].cells[c].paragraphs[0].runs:
            sig.rows[0].cells[c].paragraphs[0].runs[0].bold = True
        sig.rows[1].cells[c].text = "...............................\nDate................."
        sig.rows[1].cells[c].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.save(path)