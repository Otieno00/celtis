"""PDF export for the soil lab report."""
from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import A4, landscape
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


def export_soil_report_pdf(path, header, rows):
    PAGE = landscape(A4)
    doc = SimpleDocTemplate(path, pagesize=PAGE,
                            leftMargin=12 * mm, rightMargin=12 * mm,
                            topMargin=14 * mm, bottomMargin=14 * mm)

    def h(t, sz=7):   return Paragraph(f"<b>{t}</b>", _sty(sz, bold=True))
    def d(t, sz=8, bold=False, align=TA_CENTER):
        return Paragraph(str(t) if t else "", _sty(sz, bold=bold, align=align))
    def dl(t, sz=8):  return d(t, sz, align=TA_LEFT)

    story = [
        Paragraph(f"<b>Date: {header.get('rpt_date','')}</b>",
                  _sty(9, bold=True)),
        Spacer(1, 4 * mm),
        Paragraph("LABORATORY TEST REPORT", _sty(14, bold=True)),
        Spacer(1, 3 * mm),
    ]
    proj = header.get("rpt_project")
    if proj:
        story.append(Paragraph(f"TEST RESULTS FOR {proj.upper()}",
                               _sty(10, bold=True)))
    story.append(Spacer(1, 4 * mm))

    W = PAGE[0] - 24 * mm
    cw = [30*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm, 10*mm,
          10*mm, 10*mm, 10*mm, 10*mm, 10*mm, 13*mm, 10*mm, 13*mm, 9*mm]
    DARK, LBLUE, LGREEN, LORNG = (rl_colors.HexColor("#edf2f7"),
                                  rl_colors.HexColor("#edf2f7"),
                                  rl_colors.HexColor("#e2efda"),
                                  rl_colors.HexColor("#fff2cc"))
    LRED, WHITE = rl_colors.HexColor("#fce4d6"), rl_colors.white

    H0 = [h("SAMPLE REFERENCE"), h("Grading"), "", "", "", "", "",
          h("Atterberg Limits"), "", "", "", "",
          h("Compaction\nT 180"), "", h("CBR"), h("Swell")]
    H1 = ["", h("% Passing BS Sieve Size (mm)"), "", "", "", "", "",
          "", "", "", "", "", h("MDD"), h("OMC"), "", ""]
    H2 = ["", h("20"), h("10"), h("5"), h("2"), h("0.425"), h("0.075"),
          h("LL"), h("PL"), h("PI"), h("LS"), h("PM"),
          h("Kg/m³"), h("(%)"), h("(%)"), h("(%)")]

    data_rows, comp_rows = [], []
    for i, r in enumerate(rows):
        vals = [d(r.get("ref", ""), bold=True, align=TA_LEFT)]
        for k in ("p20", "p10", "p5", "p2", "p0425", "p0075",
                  "ll", "pl", "pi", "ls", "pm", "mdd", "omc",
                  "cbr", "swell"):
            vals.append(d(r.get(k, "")))
        data_rows.append(vals)
        if r.get("comp"):
            comp_rows.append(3 + len(data_rows) - 1)
            cr = [d("SOIL COMPOSITION", sz=7, bold=True, align=TA_LEFT),
                  Paragraph(r["comp"], _sty(7, align=TA_LEFT))] + [""] * 14
            data_rows.append(cr)

    if not data_rows:
        raise ValueError("No rows to export")

    t = Table([H0, H1, H2] + data_rows, colWidths=cw, repeatRows=3)
    cmds = [("BOX", (0, 0), (-1, -1), 1.2, DARK),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, rl_colors.HexColor("#999")),
            ("BACKGROUND", (0, 0), (-1, 2), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 2), WHITE),
            ("FONTSIZE", (0, 0), (-1, 2), 7),
            ("ALIGN", (0, 0), (-1, 2), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (1, 0), (6, 0)), ("SPAN", (7, 0), (11, 0)),
            ("SPAN", (12, 0), (13, 0)), ("SPAN", (0, 0), (0, 2)),
            ("SPAN", (14, 0), (14, 2)), ("SPAN", (15, 0), (15, 2)),
            ("SPAN", (1, 1), (6, 1)), ("SPAN", (7, 1), (11, 1)),
            ("SPAN", (12, 1), (15, 1)),
            ("BACKGROUND", (1, 3), (6, -1), LBLUE),
            ("BACKGROUND", (7, 3), (11, -1), LGREEN),
            ("BACKGROUND", (12, 3), (13, -1), LORNG),
            ("BACKGROUND", (14, 3), (14, -1), LRED),
            ("FONTSIZE", (0, 3), (-1, -1), 8),
            ("ALIGN", (0, 3), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 3), (0, -1), "Times-Bold"),
            ("ROWBACKGROUNDS", (0, 3), (-1, -1),
             [WHITE, rl_colors.HexColor("#f4f4f4")])]
    for ci in comp_rows:
        cmds += [("SPAN", (1, ci), (-1, ci)),
                 ("BACKGROUND", (0, ci), (-1, ci),
                  rl_colors.HexColor("#fef9e7")),
                 ("FONTNAME", (0, ci), (-1, ci), "Times-Italic"),
                 ("FONTSIZE", (0, ci), (-1, ci), 7),
                 ("ALIGN", (1, ci), (-1, ci), "LEFT")]
    t.setStyle(TableStyle(cmds))
    story.append(t)
    story.append(Spacer(1, 5 * mm))

    for key, label in [("rpt_topsoil", "Average Topsoil/overburden layer"),
                       ("rpt_depth", "Average depth of material proposed for use")]:
        v = header.get(key)
        if v:
            story.append(Paragraph(f"NB: &nbsp;&nbsp;{label} = {v} m",
                                   _sty(8, align=TA_LEFT)))

    story.append(Spacer(1, 8 * mm))
    tech = header.get("rpt_tech") or "Project Material Technologist"
    eng = header.get("rpt_engineer") or "Resident Engineer"
    sig = Table([[d(tech, bold=True, align=TA_LEFT),
                  d(eng, bold=True, align=TA_LEFT)],
                 [d("." * 48, align=TA_LEFT), d("." * 48, align=TA_LEFT)]],
                colWidths=[W / 2, W / 2])
    sig.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                             ("TOPPADDING", (0, 1), (-1, 1), 6)]))
    story.append(sig)
    doc.build(story)