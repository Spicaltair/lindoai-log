import os
import sqlite3
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from fpdf import FPDF

def get_logs_by_date(date):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("SELECT start_time, end_time, content, project FROM logs WHERE date = ? ORDER BY start_time", (date,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_meta(date):
    conn = sqlite3.connect("log.db")
    c = conn.cursor()
    c.execute("SELECT location, recorder, weather, temperature FROM meta WHERE date = ?", (date,))
    row = c.fetchone()
    conn.close()
    return row if row else ("", "", "", "")

def export_logs_to_pdf(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('zhongs', '', 'fonts/STZHONGS.TTF', uni=True)
    pdf.set_font('zhongs', '', 12)

    date = start_date
    while date <= end_date:
        date_str = date.strftime("%Y-%m-%d")
        logs = get_logs_by_date(date_str)
        location, recorder, weather, temperature = get_meta(date_str)

        if logs:
            pdf.set_font('zhongs', '', 12)
            pdf.cell(0, 10, f"{date_str}", ln=True)

            pdf.set_font('zhongs', '', 11)
            pdf.cell(0, 10, f"地点：{location or '-'}    记录人：{recorder or '-'}", ln=True)
            pdf.cell(0, 10, f"天气：{weather or '-'}    气温：{temperature or '-'}℃", ln=True)
            pdf.ln(3)

            pdf.set_font('zhongs', '', 12)
            for row in logs:
                start, end, content, project = row
                text = f"{start} - {end}（{project}）：{content}"
                pdf.multi_cell(0, 10, text)
            pdf.ln(5)
        date += timedelta(days=1)

    filename = f"{start_date_str}_to_{end_date_str}_logs.pdf"
    output_dir = "导出的日志pdf"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    pdf.output(output_path)
    messagebox.showinfo("导出成功", f"PDF 已保存至：\n{output_path}")

def create_gui():
    root = tk.Tk()
    root.title("导出日志为 PDF")
    root.geometry("380x220")
    root.configure(bg="#f8f9fa")

    label_font = ("Segoe UI", 10)
    button_font = ("Segoe UI", 10, "bold")

    tk.Label(root, text="起始日期:", font=label_font, bg="#f8f9fa").place(x=30, y=40)
    start_cal = DateEntry(root, width=16, date_pattern="yyyy-MM-dd")
    start_cal.place(x=110, y=40)

    tk.Label(root, text="结束日期:", font=label_font, bg="#f8f9fa").place(x=30, y=80)
    end_cal = DateEntry(root, width=16, date_pattern="yyyy-MM-dd")
    end_cal.place(x=110, y=80)

    def on_export():
        start = start_cal.get()
        end = end_cal.get()
        export_logs_to_pdf(start, end)

    export_btn = tk.Button(
        root, text="📤 导出 PDF", command=on_export,
        font=button_font, bg="#007bff", fg="white",
        activebackground="#0056b3", activeforeground="white",
        relief="flat", width=20
    )
    export_btn.place(x=100, y=140)

    root.mainloop()

if __name__ == "__main__":
    create_gui()