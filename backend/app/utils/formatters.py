from datetime import datetime, date, timedelta


def format_date(date_obj, format_type='long'):
    d = datetime.fromisoformat(date_obj) if isinstance(date_obj, str) else date_obj
    if format_type == 'short':
        return d.strftime("%d %b")
    if format_type == 'long':
        return d.strftime("%d %B %Y")
    if format_type == 'relative':
        now = datetime.now()
        diff_days = (now - d).days
        if diff_days == 0:
            return "Today"
        if diff_days == 1:
            return "Yesterday"
        if diff_days < 7:
            return f"{diff_days} days ago"
        return d.strftime("%d %b")
    return d.strftime("%Y-%m-%d")


def format_time(date_obj):
    d = datetime.fromisoformat(date_obj) if isinstance(date_obj, str) else date_obj
    return d.strftime("%I:%M %p").lstrip("0")


def format_score(score):
    return f"{min(100, max(0, score)):.0f}%"


def get_score_color(score):
    if score >= 80:
        return "text-green-500"
    if score >= 60:
        return "text-yellow-500"
    if score >= 40:
        return "text-orange-500"
    return "text-red-500"


def truncate_text(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def generate_certificate_id():
    import random
    import string
    return "VANI-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))