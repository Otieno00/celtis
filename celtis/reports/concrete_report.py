"""Word export for concrete cube reports. Pure function of data -> file."""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

SECTION = "section"   # label spans the whole row
SPAN    = "span"      # label in col 0, one value spanning the sample cols
DATA    = "data"      # label in col 0, one cell per sample


def _txt(v):
    """None -> '', never the string 'None'."""
    return "" if v is None else str(v)


def export_concrete_cube_report(path, header, samples):
    header = header or {}                 # <-- guard
    samples = list(samples or [])
    n = len(samples)
    cols = n + 1
    first = samples[0] if samples else {}

    def g(s, k):
        return _txt(s.get(k, ""))

    spec = [                                                   # (kind, label, value)
        (SECTION, "Concrete Cube Making",         None),
        (DATA,    "Design Concrete Class*",       [g(s, "design_class") for s in samples]),
        (DATA,    "Date Casted",                  [g(s, "date_cast")    for s in samples]),
        (SECTION, "Material Source",              None),
        (SPAN,    "Cement",                       header.get("cement", "")),
        (SPAN,    "SAND",                         header.get("sand", "")),
        (SPAN,    "Aggregates",                   header.get("aggregates", "")),
        (SECTION, "TEST REQUIREMENTS/RESULTS",    None),
        (DATA,    "Sample No.",                   [g(s, "sample_no")   for s in samples]),
        (DATA,    "Date tested",                  [g(s, "date_tested") for s in samples]),
        (DATA,    "Slump (mm)",                   [g(s, "slump")       for s in samples]),
        (DATA,    "Age at crushing Test (Days)",  [g(s, "age_days")    for s in samples]),
        (SECTION, "Sample Dimensions",            None),
        (SPAN,    "Nominal (mm)",                 first.get("nominal_mm", "")),
        (SPAN,    "Measured (mm)",                first.get("measured_mm", "")),
        (SPAN,    "Saturated Density (Kg/m³)",    first.get("saturated_density", "")),
        (SPAN,    "Loaded Area (mm²)",            first.get("loaded_area", "")),
        (DATA,    "Maximum Load (KN)",            [g(s, "max_load")    for s in samples]),
        (DATA,    "Compressive Strength (N/mm²)", [g(s, "comp_str")    for s in samples]),
        (SPAN,    "Comments",                     header.get("comments", "")),
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

    t = doc.add_table(rows=len(spec), cols=cols)
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False

    # 1) fill first
    for i, (kind, label, value) in enumerate(spec):
        t.cell(i, 0).text = _txt(label)
        if kind == DATA:
            vals = list(value or [])
            vals += [""] * (n - len(vals))
            for j in range(n):
                t.cell(i, j + 1).text = _txt(vals[j])
        elif kind == SPAN and cols > 1:
            t.cell(i, 1).text = _txt(value)

    # 2) then merge, driven by `kind` instead of hardcoded indices
    if cols > 1:
        for i, (kind, _, _) in enumerate(spec):
            if kind == SECTION:
                t.cell(i, 0).merge(t.cell(i, cols - 1))
            elif kind == SPAN:
                t.cell(i, 1).merge(t.cell(i, cols - 1))

    # 3) format — dedupe by underlying <w:tc> so merged cells aren't visited twice
    seen = set()
    for row in t.rows:
        for j, cell in enumerate(row.cells):
            if id(cell._tc) in seen:
                continue
            seen.add(id(cell._tc))
            for p in cell.paragraphs:
                p.alignment = (WD_ALIGN_PARAGRAPH.LEFT if j == 0
                               else WD_ALIGN_PARAGRAPH.CENTER)
                for run in p.runs:
                    run.font.size = Pt(9)
                    if j == 0:
                        run.bold = True

    # label column wide enough to read
    for row in t.rows:
        row.cells[0].width = Cm(6)

    doc.add_paragraph()
    sig = doc.add_table(rows=2, cols=2)
    sig.style = "Table Grid"
    sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    sig.rows[0].cells[0].text = header.get("technologist") or "Project Material Technologist"
    sig.rows[0].cells[1].text = header.get("engineer") or "Resident Engineer"
    for c in (0, 1):
        p0 = sig.rows[0].cells[c].paragraphs[0]
        if p0.runs:
            p0.runs[0].bold = True
        cell = sig.rows[1].cells[c]
        cell.text = "...............................\nDate................."
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.save(path)