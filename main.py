# lindoai-log 项目主入口

from ui import run_ui
from database import init_db
from export import export_markdown

filepath = export_markdown("2025-05-21")
print(f"日志已导出至: {filepath}")


def main():
    init_db()
    run_ui()


if __name__ == "__main__":
    main()
