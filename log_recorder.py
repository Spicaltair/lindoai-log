import datetime

def validate_time_range(start_str, end_str):
    fmt = "%Y-%m-%d %H:%M"
    try:
        start = datetime.datetime.strptime(start_str, fmt)
        end = datetime.datetime.strptime(end_str, fmt)
        return start < end
    except ValueError:
        return False

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")