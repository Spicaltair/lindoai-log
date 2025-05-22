import tkinter as tk
from tkinter import messagebox
import datetime
import os
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from database import insert_log, get_logs_by_date, save_meta, get_meta, get_top_phrases

log_id_list = []  # 用于保存每条记录的数据库 ID

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
    with open("projects.xml", "r", encoding="utf-8") as f:
        project_options = [line.strip() for line in f if line.strip()]

    # 限定下拉范围为 08:00 到 18:45
    hours = [f"{h:02d}" for h in range(6, 23)]
    minutes = ["00", "15", "30", "45"]

    # 获取当前时间并向上取整到最近的15分钟
    now = datetime.datetime.now()
    rounded_minute = (now.minute // 15 + (1 if now.minute % 15 != 0 else 0)) * 15
    if rounded_minute == 60:
        now += datetime.timedelta(hours=1)
        rounded_minute = 0
    now = now.replace(minute=rounded_minute, second=0, microsecond=0)

    # 默认值：开始时间 = 当前向上取整，结束时间 = +1小时
    start_hour_var.set(f"{now.hour:02d}")
    start_min_var.set(f"{now.minute:02d}")
    end_time = now + datetime.timedelta(hours=1)
    end_hour_var.set(f"{end_time.hour:02d}")
    end_min_var.set(f"{end_time.minute:02d}")


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

    entry = tb.LabelFrame(scrollable_frame, text="编辑记录", padding=10, bootstyle="warning")
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

    def move_up():
        idx = log_list.curselection()
        if idx and idx[0] > 0:
            sel = idx[0]
            log_id_list[sel], log_id_list[sel - 1] = log_id_list[sel - 1], log_id_list[sel]
            log_list.insert(sel - 1, log_list.get(sel))
            log_list.delete(sel + 1)
            log_list.select_set(sel - 1)

    def move_down():
        idx = log_list.curselection()
        if idx and idx[0] < len(log_id_list) - 1:
            sel = idx[0]
            log_id_list[sel], log_id_list[sel + 1] = log_id_list[sel + 1], log_id_list[sel]
            text = log_list.get(sel)
            log_list.delete(sel)
            log_list.insert(sel + 1, text)
            log_list.select_set(sel + 1)

    def delete_selected():
        selection = log_list.curselection()
        if selection:
            idx = selection[0]
            log_id = log_id_list[idx]
            import sqlite3
            conn = sqlite3.connect("log.db")
            c = conn.cursor()
            c.execute("DELETE FROM logs WHERE id = ?", (log_id,))
            conn.commit()
            conn.close()
            refresh_logs()

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
 
    btn_frame = tk.Frame(scrollable_frame)  # ✅ 加在 scrollable_frame 中
    btn_frame.pack(pady=(5, 10))

    tb.Button(btn_frame, text="⬆ 上移", command=move_up, bootstyle="secondary").pack(side="left", padx=8)
    tb.Button(btn_frame, text="⬇ 下移", command=move_down, bootstyle="secondary").pack(side="left", padx=8)
    tb.Button(btn_frame, text="🗑 删除所选记录", command=delete_selected, bootstyle="danger-outline").pack(side="left", padx=8)
    tb.Button(btn_frame, text="➕ 添加记录", command=add_log, bootstyle="success").pack(side="left", padx=8)



    phrase_frame = tb.LabelFrame(scrollable_frame, text="高频内容", padding=10, bootstyle="light")
    phrase_frame.pack(fill=tk.X, padx=10, pady=5)
    phrase_box = tb.Frame(phrase_frame)
    phrase_box.pack(fill=tk.X)

    def refresh_phrases():
        for widget in phrase_box.winfo_children():
            widget.destroy()

        phrases = get_top_phrases()[:12]
        for i, phrase in enumerate(phrases):
            row = i // 5
            col = i % 4
            display_text = phrase[:24] + "..." if len(phrase) > 24 else phrase
            b = tb.Button(phrase_box, text=display_text, width=20, command=lambda p=phrase: content_var.set(p), bootstyle="secondary-outline")
            b.grid(row=row, column=col, padx=4, pady=4, sticky="w")



    display = tb.LabelFrame(scrollable_frame, text="今日记录", padding=10, bootstyle="default")
    display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    log_list = tk.Listbox(display, font=("Consolas", 10), bg="white")
    log_list.pack(fill=tk.BOTH, expand=True)


    def refresh_logs():
        log_list.delete(0, tk.END)
        log_list.delete(0, tk.END)
        log_id_list.clear()
        for row in get_logs_by_date(date_var.get()):
            log_id_list.append(row[0])  # row[0] 是 id
            log_list.insert(tk.END, f"{row[1]} - {row[2]}（{row[4]}）: {row[3]}")



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