from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from tkinter import messagebox
import sqlite3
import os


def generate_logs_pdf(start_date=None, end_date=None, name_filter=None):
    """
    Generate PDF of library logs with optional filters:
    - start_date, end_date: strings in 'YYYY-MM-DD' format to filter Time In
    - name_filter: string to filter by student name
    Saves the generated PDF to the Desktop.
    """
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    query = "SELECT name, timein, timeout, purpose FROM logs WHERE 1=1"
    params = []

    # Filter by name
    if name_filter:
        query += " AND name LIKE ?"
        params.append(f"%{name_filter}%")

    # Filter by start_date
    if start_date:
        query += " AND DATE(timein) >= ?"
        params.append(start_date)

    # Filter by end_date
    if end_date:
        query += " AND DATE(timein) <= ?"
        params.append(end_date)

    query += " ORDER BY timein ASC"
    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()

    if not logs:
        messagebox.showinfo("No Logs", "There are no logs matching the criteria.")
        return

    # Save PDF to Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    filename = os.path.join(desktop_path, f"Library_Logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Library Logs Report", styles['Title']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Spacer

    # Table headers
    data = [["Name", "Time In", "Time Out", "Purpose"]]
    for log in logs:
        # Format TimeIn (must match your DB format)
        try:
            timein = datetime.strptime(log[1], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") if log[1] else ""
        except:
            timein = log[1] or ""

        # Format TimeOut (must match your DB format)
        try:
            timeout = datetime.strptime(log[2], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") if log[2] else ""
        except:
            try:
                timeout = datetime.strptime(log[2], "%B %d, %Y %I:%M %p").strftime("%Y-%m-%d %H:%M:%S") if log[2] else ""
            except:
                timeout = log[2] or ""

        data.append([log[0], timein, timeout, log[3]])

    table = Table(data, colWidths=[150, 120, 120, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    messagebox.showinfo("PDF Generated", f"Logs PDF saved to Desktop as:\n\n{filename}")
