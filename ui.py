import tkinter as tk
from tkinter import messagebox
import datetime
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from database import insert_log, get_logs_by_date, save_meta, get_meta, get_top_phrases

def export_markdown_to_file(date, filepath):
    logs = get_logs_by_date(date)
    location, recorder, weather, temperature = get_meta(date)

    lines = []
    lines.append(f"# 🗓️ {date} 工程日志\n")
    lines.append(f"- 地点：{location or '-'}")
    lines.append(f"- 记录人：{recorder or '-'}")
    lines.append(f"- 天气：{weather or '-'}，{temperature or '-'}℃\n")
    lines.append("---\n")
    lines.append("## ⏱ 日志记录\n")

    if not logs:
        lines.append("_暂无记录_\n")
    else:
        for start, end, content, project in logs:
            lines.append(f"- {start} - {end}（{project or '-'}）：{content}")

    content = "\n".join(lines)
    os.makedirs("log", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def run_ui():
    root = tb.Window(themename="cosmo")
    root.title("LindoAI Log Recorder")
    root.geometry("880x720")
    root.iconbitmap("lindoai.ico")

    # Scrollable canvas
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Mouse wheel support
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    today = datetime.date.today().strftime("%Y-%m-%d")

    logo_img = Image.open("logo.png").resize((48, 48))
    logo = ImageTk.PhotoImage(logo_img)
    top_frame = tk.Frame(scrollable_frame, bg="#f9fafb")
    top_frame.pack(pady=(5, 0))
    tk.Label(top_frame, image=logo, bg="#f9fafb").pack(side=tk.LEFT, padx=(10, 8))
    tk.Label(top_frame, text="LindoAI 施工日志记录器", font=("Segoe UI", 18, "bold"), bg="#f9fafb").pack(side=tk.LEFT)

    date_var = tk.StringVar(value=today)
    location_var = tk.StringVar()
    recorder_var = tk.StringVar()
    weather_var = tk.StringVar()
    temperature_var = tk.StringVar()
    content_var = tk.StringVar()
    project_var = tk.StringVar()
    start_hour_var = tk.StringVar()
    start_min_var = tk.StringVar()
    end_hour_var = tk.StringVar()
    end_min_var = tk.StringVar()

    weather_options = ["晴", "多云", "阴", "小雨", "中雨", "大雨", "雾", "雪", "风", "雷阵雨"]
    project_options = ["项目A", "项目B", "项目C", "临时项目"]
    hours = [f"{h:02d}" for h in range(24)]
    minutes = ["00", "15", "30", "45"]

    meta = tb.LabelFrame(scrollable_frame, text="基础信息", padding=10, bootstyle="info")
    meta.pack(fill=tk.X, padx=10, pady=5)

    tb.Label(meta, text="日期").grid(row=0, column=0)
    tb.Entry(meta, textvariable=date_var, width=12).grid(row=0, column=1, padx=5)
    tb.Label(meta, text="地点").grid(row=0, column=2)
    tb.Entry(meta, textvariable=location_var, width=15).grid(row=0, column=3, padx=5)
    tb.Label(meta, text="记录人").grid(row=0, column=4)
    tb.Entry(meta, textvariable=recorder_var, width=10).grid(row=0, column=5, padx=5)
    tb.Label(meta, text="天气").grid(row=1, column=0)
    tb.Combobox(meta, textvariable=weather_var, values=weather_options, width=10).grid(row=1, column=1, padx=5)
    tb.Label(meta, text="气温℃").grid(row=1, column=2)
    tb.Entry(meta, textvariable=temperature_var, width=10).grid(row=1, column=3, padx=5)
    tb.Button(meta, text="保存", command=lambda: save_meta(date_var.get(), location_var.get(), recorder_var.get(), weather_var.get(), temperature_var.get()), bootstyle="primary").grid(row=1, column=5, padx=5)

    entry = tb.LabelFrame(scrollable_frame, text="添加记录", padding=10, bootstyle="warning")
    entry.pack(fill=tk.X, padx=10, pady=5)

    tb.Label(entry, text="开始").grid(row=0, column=0)
    tb.Combobox(entry, textvariable=start_hour_var, values=hours, width=4).grid(row=0, column=1)
    tb.Combobox(entry, textvariable=start_min_var, values=minutes, width=4).grid(row=0, column=2)
    tb.Label(entry, text="结束").grid(row=0, column=3)
    tb.Combobox(entry, textvariable=end_hour_var, values=hours, width=4).grid(row=0, column=4)
    tb.Combobox(entry, textvariable=end_min_var, values=minutes, width=4).grid(row=0, column=5)
    tb.Label(entry, text="项目").grid(row=1, column=0)
    tb.Combobox(entry, textvariable=project_var, values=project_options, width=18).grid(row=1, column=1, columnspan=2, padx=5, sticky="w")
    tb.Label(entry, text="内容").grid(row=2, column=0)
    tb.Entry(entry, textvariable=content_var, width=60).grid(row=2, column=1, columnspan=5, padx=5, pady=4)

    def add_log():
        date = date_var.get()
        start = f"{start_hour_var.get()}:{start_min_var.get()}"
        end = f"{end_hour_var.get()}:{end_min_var.get()}"
        content = content_var.get()
        project = project_var.get()
        if not all([start_hour_var.get(), start_min_var.get(), end_hour_var.get(), end_min_var.get(), content, project]):
            messagebox.showerror("输入错误", "请填写完整时间段、项目和内容")
            return
        insert_log(date, start, end, content, project)
        start_hour_var.set("")
        start_min_var.set("")
        end_hour_var.set("")
        end_min_var.set("")
        content_var.set("")
        project_var.set("")
        refresh_logs()
        refresh_phrases()

    tb.Button(entry, text="添加记录", command=add_log, bootstyle="success").grid(row=3, column=5, pady=5)

    phrase_frame = tb.LabelFrame(scrollable_frame, text="高频内容", padding=10, bootstyle="light")
    phrase_frame.pack(fill=tk.X, padx=10, pady=5)
    phrase_box = tb.Frame(phrase_frame)
    phrase_box.pack(fill=tk.X)

    def refresh_phrases():
        for w in phrase_box.winfo_children():
            w.destroy()
        for phrase in get_top_phrases():
            b = tb.Button(phrase_box, text=phrase, width=12, command=lambda p=phrase: content_var.set(p), bootstyle="secondary-outline")
            b.pack(side=tk.LEFT, padx=4, pady=2)

    display = tb.LabelFrame(scrollable_frame, text="今日记录", padding=10, bootstyle="default")
    display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    log_list = tk.Listbox(display, font=("Consolas", 10), bg="white")
    log_list.pack(fill=tk.BOTH, expand=True)

    def refresh_logs():
        log_list.delete(0, tk.END)
        for row in get_logs_by_date(date_var.get()):
            log_list.insert(tk.END, f"{row[0]} - {row[1]}（{row[3] or '-'}）: {row[2]}")

    def export_logs():
        date = date_var.get()
        os.makedirs("log", exist_ok=True)
        filepath = os.path.join("log", f"log-{date}.md")
        export_markdown_to_file(date, filepath)
        messagebox.showinfo("导出成功", f"日志已保存到：\n{filepath}")

    tb.Button(scrollable_frame, text="📤 导出为 Markdown", command=export_logs, bootstyle="info").pack(pady=10)

    loc, rec, wea, temp = get_meta(today)
    location_var.set(loc)
    recorder_var.set(rec)
    weather_var.set(wea)
    temperature_var.set(temp)

    refresh_logs()
    refresh_phrases()
    root.mainloop()