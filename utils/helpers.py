from datetime import datetime


def format_date(date_obj):
    """Format date object to readable string"""
    if not date_obj:
        return ""

    today = datetime.now().date()
    if date_obj == today:
        return "Today"
    elif date_obj == today.replace(day=today.day + 1):
        return "Tomorrow"
    else:
        return date_obj.strftime("%b %d, %Y")


def parse_date(date_string):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except:
        return None