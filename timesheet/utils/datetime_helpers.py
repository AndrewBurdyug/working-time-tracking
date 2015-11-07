import calendar
from datetime import datetime

from django.utils.timezone import get_current_timezone

tz = get_current_timezone()


def current_year():
    return datetime.now(tz=tz).year


def current_month():
    return datetime.now(tz=tz).month


def current_datetime():
    return datetime.now(tz=tz)


def get_month_abbr(month_number):
    return calendar.month_abbr[month_number]


def get_month_name(month_number):
    return calendar.month_name[month_number]


def get_month_days(year, month_number):
    return calendar.monthrange(year, month_number)
