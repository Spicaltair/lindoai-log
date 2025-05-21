import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from database import insert_log, get_logs_by_date, save_meta, get_meta, get_top_phrases

def export_markdown_to_file(date, filepath):
    from database import get_logs_by_date, get_meta
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
        for start, end, content in logs:
            lines.append(f"- {start} - {end}：{content}")

    content = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

def run_ui():
    root = tb.Window(themename="flatly")
    root.title("LindoAI Log Recorder")
    root.geometry("800x750")
    root.iconbitmap("lindoai.ico")

    today = datetime.date.today().strftime("%Y-%m-%d")

    # Logo
    logo_img = Image.open("logo.png").resize((60, 60))
    logo = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(root, image=logo, bg="#f9fafb")
    logo_label.image = logo
    logo_label.pack(pady=10)

    tb.Label(root, text="LindoAI 施工日志记录器", font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))

    # Metadata Frame
    meta_frame = tb.LabelFrame(root, text="今日基础信息", padding=15, bootstyle="info")
    meta_frame.pack(fill=X, padx=20, pady=10)

    date_var = tk.StringVar(value=today)
    location_var = tk.StringVar()
    recorder_var = tk.StringVar()
    weather_var = tk.StringVar()
    temperature_var = tk.StringVar()
    weather_options = ["晴", "多云", "阴", "小雨", "中雨", "大雨", "雾", "雪", "风", "雷阵雨"]

    tb.Label(meta_frame, text="日期:").grid(row=0, column=0, sticky="w")
    tb.Entry(meta_frame, textvariable=date_var, width=12).grid(row=0, column=1, padx=5)

    tb.Label(meta_frame, text="地点:").grid(row=0, column=2, sticky="w")
    tb.Entry(meta_frame, textvariable=location_var, width=15).grid(row=0, column=3, padx=5)

    tb.Label(meta_frame, text="记录人:").grid(row=0, column=4, sticky="w")
    tb.Entry(meta_frame, textvariable=recorder_var, width=10).grid(row=0, column=5, padx=5)

    tb.Label(meta_frame, text="天气:").grid(row=1, column=0, sticky="w")
    tb.Combobox(meta_frame, textvariable=weather_var, values=weather_options, width=10).grid(row=1, column=1, padx=5)

    tb.Label(meta_frame, text="气温(℃):").grid(row=1, column=2, sticky="w")
    tb.Entry(meta_frame, textvariable=temperature_var, width=10).grid(row=1, column=3, padx=5)

    def save_metadata():
        save_meta(date_var.get(), location_var.get(), recorder_var.get(), weather_var.get(), temperature_var.get())
        messagebox.showinfo("保存成功", "基础信息已保存")

    tb.Button(meta_frame, text="保存基础信息", command=save_metadata, bootstyle="primary").grid(row=1, column=5, padx=5)

    # Log Entry Frame
    entry_frame = tb.LabelFrame(root, text="添加日志记录", padding=15, bootstyle="warning")
    entry_frame.pack(fill=X, padx=20, pady=10)

    hours = [f"{h:02d}" for h in range(24)]
    minutes = ["00", "15", "30", "45"]
    start_hour_var = tk.StringVar()
    start_min_var = tk.StringVar()
    end_hour_var = tk.StringVar()
    end_min_var = tk.StringVar()
    content_var = tk.StringVar()

    tb.Label(entry_frame, text="开始时间:").grid(row=0, column=0, sticky="w")
    tb.Combobox(entry_frame, textvariable=start_hour_var, values=hours, width=4).grid(row=0, column=1, padx=2)
    tb.Combobox(entry_frame, textvariable=start_min_var, values=minutes, width=4).grid(row=0, column=2, padx=2)

    tb.Label(entry_frame, text="结束时间:").grid(row=0, column=3, sticky="w")
    tb.Combobox(entry_frame, textvariable=end_hour_var, values=hours, width=4).grid(row=0, column=4, padx=2)
    tb.Combobox(entry_frame, textvariable=end_min_var, values=minutes, width=4).grid(row=0, column=5, padx=2)

    tb.Label(entry_frame, text="内容:").grid(row=1, column=0, sticky="w")
    tb.Entry(entry_frame, textvariable=content_var, width=60).grid(row=1, column=1, columnspan=5, padx=5, pady=4)

    def add_log():
        date = date_var.get()
        start = f"{start_hour_var.get()}:{start_min_var.get()}"
        end = f"{end_hour_var.get()}:{end_min_var.get()}"
        content = content_var.get()
        if not all([start_hour_var.get(), start_min_var.get(), end_hour_var.get(), end_min_var.get(), content]):
            messagebox.showerror("输入错误", "请填写完整时间段和内容")
            return
        insert_log(date, start, end, content)
        start_hour_var.set("")
        start_min_var.set("")
        end_hour_var.set("")
        end_min_var.set("")
        content_var.set("")
        refresh_logs()
        refresh_phrases()

    tb.Button(entry_frame, text="添加记录", command=add_log, bootstyle="success").grid(row=2, column=5, pady=6)

    # Frequent Phrases Frame
    phrase_frame = tb.LabelFrame(root, text="高频内容", padding=10, bootstyle="light")
    phrase_frame.pack(fill=X, padx=20, pady=5)
    phrase_box = tb.Frame(phrase_frame)
    phrase_box.pack(fill=X)

    def refresh_phrases():
        for widget in phrase_box.winfo_children():
            widget.destroy()
        for phrase in get_top_phrases():
            b = tb.Button(phrase_box, text=phrase, command=lambda p=phrase: content_var.set(p), bootstyle="secondary-outline")
            b.pack(side=LEFT, padx=4, pady=2)

    # Log display
    display_frame = tb.LabelFrame(root, text="今日记录", padding=10, bootstyle="default")
    display_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)

    log_list = tk.Listbox(display_frame, font=("Consolas", 10), bg="white")
    log_list.pack(fill=BOTH, expand=True)

    def refresh_logs():
        log_list.delete(0, tk.END)
        for row in get_logs_by_date(date_var.get()):
            log_list.insert(tk.END, f"{row[0]} - {row[1]}: {row[2]}")

    def export_logs():
        default_name = f"log-{date_var.get()}.md"
        filepath = filedialog.asksaveasfilename(defaultextension=".md", initialfile=default_name, filetypes=[("Markdown 文件", "*.md")])
        if filepath:
            export_markdown_to_file(date_var.get(), filepath)
            messagebox.showinfo("导出成功", f"日志已保存为：\n{filepath}")

    tb.Button(root, text="📤 导出为 Markdown", command=export_logs, bootstyle="info").pack(pady=10)

    loc, rec, wea, temp = get_meta(today)
    location_var.set(loc)
    recorder_var.set(rec)
    weather_var.set(wea)
    temperature_var.set(temp)

    refresh_logs()
    refresh_phrases()

    root.mainloop()