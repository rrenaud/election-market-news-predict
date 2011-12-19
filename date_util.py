import datetime

def day_difference(cur, direction):
    encoded = datetime.datetime.strptime(cur, '%Y%m%d')
    next = encoded + datetime.timedelta(days = direction)
    next_formatted = next.strftime('%Y%m%d')
    return next_formatted

def prev_day(cur):
    return day_difference(cur, -1)
    
    
