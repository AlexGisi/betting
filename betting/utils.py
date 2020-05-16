import datetime


def string_to_date(string):
    return datetime.date(int(string.split('/')[2]), int(string.split('/')[1]), int(string.split('/')[0]))
