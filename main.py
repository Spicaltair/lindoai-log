from ui import run_ui
from database import init_db

def main():
    init_db()
    run_ui()

if __name__ == "__main__":
    main()