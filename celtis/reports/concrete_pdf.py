"""PDF export for concrete cube reports."""
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def _sty(size=8, bold=False, align=TA_CENTER, color=None):
    return ParagraphStyle("_", fontSize=size,
                          fontName="Times-Bold" if bold else "Times-Roman",
                          alignment=align, textColor=color or rl_colors.black,
                          leading=size + 2.5, spaceAfter=0)


def export_concrete_cube_report_pdf(path, header, samples):
    samples = list(samples or [])
    n = len(samples)

    def g(s, k, default=""):
        return s.get(k, default) if s else default

    def d(t, sz=8, bold=False, align=TA_CENTER):
        return Paragraph(str(t) if t else "", _sty(sz, bold=bold, align=align))

    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm)

    story = [
        Paragraph("LABORATORY TEST REPORT", _sty(14, bold=True)),
        Spacer(1, 2 * mm),
        Paragraph(header.get("test_for") or "CONCRETE CUBE TEST RESULTS",
                  _sty(10, bold=True)),
        Spacer(1, 4 * mm),
    ]

    def section(label):
        return [Paragraph(f"<b>{label}</b>", _sty(8, bold=True))] + [""] * n

    def line(label, values=None):
        if values is None:
            values = [""] * n
        values = (list(values) + [""] * n)[:n]
        return [d(label, bold=True, align=TA_LEFT)] + [d(v) for v in values]

    first = samples[0] if samples else {}
    data = [
        section("Concrete Cube Making"),
        line("Design Concrete Class*", [g(s, "design_class") for s in samples]),
        line("Date Casted",            [g(s, "date_cast")    for s in samples]),
        section("Material Source"),
        section(f"Cement; {header.get('cement','')}"),
        section(f"SAND: {header.get('sand','')}"),
        section(f"Aggregates: {header.get('aggregates','')}"),
        section("TEST REQUIREMENTS/RESULTS"),
        line("Sample No.",   [g(s, "sample_no")   for s in samples]),
        line("Date tested",  [g(s, "date_tested") for s in samples]),
        line("Slump (mm)",   [g(s, "slump")       for s in samples]),
        line("Age at crushing Test (Days)", [g(s, "age_days") for s in samples]),
        section("Sample Dimensions"),
        section("Nominal (mm)"),
        line("Measured (mm)",      [first.get("measured_mm", "")]),
        section("Saturated Density (Kg/m³)"),
        line("Loaded Area (mm²)",  [first.get("loaded_area", "")]),
        line("Maximum Load (KN)",  [g(s, "max_load") for s in samples]),
        line("Compressive Strength (N/mm²)", [g(s, "comp_str") for s in samples]),
        section("Comments"),
    ]

    label_w = 55 * mm
    sample_w = max((160 * mm - label_w) / max(n, 1), 18 * mm)
    col_widths = [label_w] + [sample_w] * n

    t = Table(data, colWidths=col_widths)
    cmds = [
        ("BOX", (0, 0), (-1, -1), 1.0, rl_colors.HexColor("#1f3864")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, rl_colors.HexColor("#999")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), rl_colors.white),
    ]
    for i, row in enumerate(data):
        if row[0] and isinstance(row[0], Paragraph) and \
           getattr(row[0].style, "fontName", "") == "Times-Bold" and \
           len(row) == n + 1 and all(c == "" for c in row[1:]):
            cmds.append(("SPAN", (0, i), (-1, i)))
            cmds.append(("BACKGROUND", (0, i), (-1, i),
                         rl_colors.HexColor("#dce6f1")))
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 8 * mm))

    tech = header.get("technologist") or "Project Material Technologist"
    eng = header.get("engineer") or "Resident Engineer"
    W = A4[0] - 30 * mm
    sig = Table([[d(tech, bold=True, align=TA_LEFT), d(eng, bold=True, align=TA_LEFT)],
                 [d("." * 40, align=TA_LEFT), d("." * 40, align=TA_LEFT)]],
                colWidths=[W / 2, W / 2])
    sig.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                             ("TOPPADDING", (0, 1), (-1, 1), 6)]))
    story.append(sig)
    doc.build(story)