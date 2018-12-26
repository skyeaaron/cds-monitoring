# -*- coding: utf-8 -*-
"""
Module with functions for handling dates in:
overridecomments.py
"""
from datetime import datetime, timedelta

def datetime_to_str(date2 = datetime.now(), output_format = '%Y%m%d'):
    """
    given datetime object and string representing output format
    return string for the date in specified format
    """
    return date2.strftime(output_format)

def str_to_datetime(date2, input_format = '%Y%m%d'):
    """
    given a string representing a date and an input format
    return a datetime representation of the date
    """
    return datetime.strptime(date2, input_format)

def today_datetime():
    """
    return today as datetime
    """
    return datetime.now()

def today_str(output_format = '%Y%m%d'):
    """
    return today as str
    """
    return datetime.now().strftime(output_format)
    
def datetime_plus_days(date2 = datetime.now(), days = 1):
    """
    return yesterday as datetime object
    """
    return date2 + timedelta(days = days)

def prettify_datestring(datestring, output_format = '%m-%d-%Y'):
    """
    given YYYYMMDD returns MM-DD-YYYY
    """
    datetime_object = datetime.strptime(datestring, '%Y%m%d')
    return datetime_object.strftime(output_format)

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
    returns 1st of the month last month and 1st of the month this month
    as strings formatted %YYYYMMDD
    if date2 is supplied, must be in datetime format
    default date2 is now
    """
    #date1 = date2 - timedelta(weeks = 4)
    date2 = today - timedelta(days=today.day) #end of last month
    date1 = date2.replace(day = 1)
    date2 = date2 + timedelta(days=1)
    return (date1.strftime('%Y%m%d'), date2.strftime('%Y%m%d'))

def calc_start_and_end(datestr2, frequency):
    """
    given date2 string %Y%m%d and frequency =daily or monthly,
    return starting date as string %Y%m%d and end date datestr2 as string
    """
    datetime2 = datetime.strptime(datestr2, '%Y%m%d')
    if frequency == "daily":
        datetime1 = datetime_plus_days(datetime2, -1)
        return datetime_to_str(datetime1), datestr2
    elif frequency == "monthly":
        return prior_month(datetime2)
    else:
        raise ValueError("Incorrect frequency passed to config: " + frequency + ". Expected daily or monthly.")
        
