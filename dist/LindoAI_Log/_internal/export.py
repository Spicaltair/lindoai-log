import os
from database import get_logs_by_date, get_meta

def export_markdown(date, export_dir="."):
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
    filename = f"log-{date}.md"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath