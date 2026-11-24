"""DOCX export for the soil lab report."""
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def export_soil_report_docx(path, header, rows):
    doc = Document()
    title = doc.add_paragraph("LABORATORY TEST REPORT")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(16)

    if header.get("rpt_project"):
        sub = doc.add_paragraph(
            f"TEST RESULTS FOR {header['rpt_project'].upper()}")
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub.runs[0].bold = True
        sub.runs[0].font.size = Pt(12)

    doc.add_paragraph(f"Date: {header.get('rpt_date','')}")
    if header.get("rpt_location"):
        doc.add_paragraph(f"Location: {header['rpt_location']}")
    if header.get("rpt_client"):
        doc.add_paragraph(f"Client: {header['rpt_client']}")
    doc.add_paragraph()

    num_cols = 16
    table_rows = []
    for r in rows:
        vals = [r.get(k, "") for k in
                ("ref", "% Pass\n20mm,p20", "p10", "p5", "p2", "p0425", "p0075", "ll", "pl", "pi", "ls", "pm", "mdd", "omc", "cbr", "swell")]
        table_rows.append(vals)
        if r.get("comp"):
            comp_row = [""] * num_cols
            comp_row[0] = "SOIL COMPOSITION"
            comp_row[1] = r["comp"]
            table_rows.append(comp_row)

    table = doc.add_table(rows=3 + len(table_rows), cols=num_cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    r0, r1, r2 = table.rows[0], table.rows[1], table.rows[2]
    r0.cells[0].text = "SAMPLE REFERENCE"
    r0.cells[0].paragraphs[0].runs[0].bold = True
    c = r0.cells[1]
    for j in range(2, 7):
        c = c.merge(r0.cells[j])
    c.text = "Grading"; c.paragraphs[0].runs[0].bold = True
    c = r0.cells[7]
    for j in range(8, 12):
        c = c.merge(r0.cells[j])
    c.text = "Atterberg Limits"; c.paragraphs[0].runs[0].bold = True
    c = r0.cells[12].merge(r0.cells[13])
    c.text = "Compaction T 180"; c.paragraphs[0].runs[0].bold = True
    r0.cells[14].text = "CBR"
    r0.cells[14].paragraphs[0].runs[0].bold = True
    r0.cells[15].text = "Swell"
    r0.cells[15].paragraphs[0].runs[0].bold = True

    c = r1.cells[1]
    for j in range(2, 7):
        c = c.merge(r1.cells[j])
    c.text = "% Passing BS Sieve Size (mm)"
    c.paragraphs[0].runs[0].bold = True

    r2.cells[0].text = ""
    for j, txt in enumerate(["20", "10", "5", "2", "0.425", "0.075", "LL", "PL", "PI", "LS", "PM", "MDD", "OMC", "CBR", "Swell"], start=1):
        r2.cells[j].text = txt
        r2.cells[j].paragraphs[0].runs[0].bold = True

    for i, row_vals in enumerate(table_rows):
        row = table.rows[3 + i]
        for j, v in enumerate(row_vals):
            if v:
                row.cells[j].text = v
                if j == 0 and row.cells[j].paragraphs[0].runs:
                    row.cells[j].paragraphs[0].runs[0].bold = True
        if row_vals[0] == "SOIL COMPOSITION":
            c = row.cells[1]
            for j in range(2, 16):
                c = c.merge(row.cells[j])
            c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
            if c.paragraphs[0].runs:
                c.paragraphs[0].runs[0].italic = True

    for row in table.rows:
        for j, cell in enumerate(row.cells):
            cell.paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.LEFT if j == 0
                else WD_ALIGN_PARAGRAPH.CENTER)

    doc.add_paragraph()
    if header.get("rpt_topsoil"):
        doc.add_paragraph(
            f"NB: Average Topsoil/overburden layer = {header['rpt_topsoil']} m")
    if header.get("rpt_depth"):
        doc.add_paragraph(
            f"NB: Average depth of material proposed for use = "
            f"{header['rpt_depth']} m")

    doc.add_paragraph()
    
    # --- 2 CELL SIGNATURE BLOCK (SAMPLE & REFERENCE) ---
    # Create a 1 row, 2 column table (exactly 2 cells)
    sig = doc.add_table(rows=1, cols=2)
    sig.style = "Table Grid"
    sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Hardcoded to exactly "Sample" and "Reference" as requested
    tech_name = "Project Material Technologist"
    eng_name = "Resident Engineer"
    
    # Combine the name, dotted line, and date into a single string per cell
    sig.rows[0].cells[0].text = f"{tech_name}\n...............................\nDate................."
    sig.rows[0].cells[1].text = f"{eng_name}\n...............................\nDate................."
    
    # Apply formatting to the 2 cells
    for c in (0, 1):
        cell = sig.rows[0].cells[c]
        # Center align all text in the cell
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Make sure the first line (the name) is bold
        if cell.paragraphs[0].runs:
            cell.paragraphs[0].runs[0].bold = True

    doc.save(path)