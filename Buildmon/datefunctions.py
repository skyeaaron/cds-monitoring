# -*- coding: utf-8 -*-
"""
Module with functions for handling dates
Used in buildmon.py
"""
from datetime import datetime, timedelta


def generate_datestrings(date2 = datetime.now()):
    """
    returns today's date and yesterday's date
    as strings formatted %YYYYMMDD
    if date2 is supplied, must be in datetime format
    """
    date1 = date2 - timedelta(days = 1)
    return (date1.strftime('%Y%m%d'), date2.strftime('%Y%m%d'))

def generate_datestring(date2 = datetime.now(), output_format = '%Y%m%d'):
    """
    given datetime object and string representing output format
    return string for the date in specified format
    """
    return date2.strftime(output_format)

def return_datetime_object(date2, input_format = '%Y%m%d'):
    """
    given a string representing a date and an input format
    return a datetime representation of the date
    """
    return datetime.strptime(date2, input_format)

def add_days_to_string(date2, days, date_format = '%Y%m%d'):
    """
    given a string represeting a date, number of days to add (could be negative),
    and date_format
    return datestring shifted over by number of days
    """
    datetime_object = datetime.strptime(date2, date_format) + timedelta(days = days)
    return datetime_object.strftime(date_format)

def make_datelist(startdate, enddate, input_format = '%Y%m%d', output_format = '%Y%m%d'):
    """
    given strings representing start and end dates
    output list of all dates from start to end including inputs
    """
    datelist = []
    start = return_datetime_object(startdate, input_format)
    datelist.append(generate_datestring(start, output_format))
    end = return_datetime_object(enddate, input_format)
    step = timedelta(days=1)
    current = start
    while current <= end:
        current += step
        datelist.append(generate_datestring(current, output_format))
    return datelist

def make_dategen(startdate, enddate, input_format = '%Y%m%d', output_format = '%Y%m%d'):
    """
    generator that generates string representing date
    given strings representing start and end dates
    """
    datelist = []
    start = return_datetime_object(startdate, input_format)
    datelist.append(generate_datestring(start, output_format))
    end = return_datetime_object(enddate, input_format)
    step = timedelta(days=1)
    current = start
    while current <= end:
        yield generate_datestring(current, output_format)
        current += step


def one_month_ago(date2 = datetime.now()):
    """
    returns same day of the month 1 month ago
    as string formatted %YYYYMMDD
    if date2 is supplied, must be in datetime format
    default date2 is now
    """
    #date1 = date2 - timedelta(weeks = 4)
    date1 = date2 - timedelta(days=date2.day)
    date1 = date1.replace(day = date2.day)
    return (date1.strftime('%Y%m%d'))

def prior_month(today = datetime.now()):
    """
    returns same day of the month 1 month ago
    as string formatted %YYYYMMDD
    if date2 is supplied, must be in datetime format
    default date2 is now
    """
    #date1 = date2 - timedelta(weeks = 4)
    date2 = today - timedelta(days=today.day) #end of last month
    date1 = date2.replace(day = 1)
    date2 = date2 + timedelta(days=1)
    return (date1.strftime('%Y%m%d'), date2.strftime('%Y%m%d'))

def prettify_datestring(datestring, output_format = '%m-%d-%Y'):
    """
    given YYYYMMDD returns MM-DD-YYYY
    """
    datetime_object = datetime.strptime(datestring, '%Y%m%d')
    return datetime_object.strftime(output_format)

def calc_start_and_end(date2, frequency):
    """
    given date2 string %Y%m%d and frequency =daily or monthly,
    return starting date date1 as string %Y%m%d
    """
    date_object2 = datetime.strptime(date2, '%Y%m%d')
    if frequency == "daily":
        return generate_datestrings(date_object2)
    elif frequency == "monthly":
        return prior_month(date_object2)
    else:
        return("error: incorrect frequency passed")
        
def query_list_if_exists(input_list, index):
    """
    if list exists
    return index value
    else return None
    """
    if input_list:
        return input_list[index]
    else:
        return None