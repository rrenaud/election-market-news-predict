import datetime

def day_difference(cur, direction):
    encoded = datetime.datetime.strptime(cur, '%Y%m%d')
    prev = encoded - datetime.timedelta(days = 1)
    prev_formatted = prev.strftime('%Y%m%d')
    return prev_formatted

def prev_day(cur):
    return day_difference(cur, -1)
    
    
