def days_hours_minutes(td):
    """Gets hours and minutes from timedelta"""
    return td.days, td.seconds // 3600, (td.seconds // 60) % 60
