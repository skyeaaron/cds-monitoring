# -*- coding: utf-8 -*-
"""
Module with functions for sending emails
Used in compare_base.py
"""

import smtplib
from email.mime.text import MIMEText

def send_failure(fail_message, email_server, from_address, to_address):
    """
    sends an email
    containing supplied failure message
    recipient must be manually specified within this function
    """
    msg = MIMEText(fail_message, 'html')
    msg['Subject'] = 'BPA Audit Log Failed'
    msg['From'] = from_address
    msg['To'] = to_address
    s = smtplib.SMTP(email_server)
    s.send_message(msg, from_addr = from_address)
    s.quit()
    return None


def get_email_list(filename):
    """
    get email list from text file
    """
    with open(filename) as f:
        email_list = f.read().replace('\n', ',')
    return email_list

    
def send_email(success_message, subject, email_list_file, email_server, from_address):
    """
    Emails success_message with subject heading to email list
    If you want to use different lists for test, specify that outside
    Emails success_message with subject heading to email list
    Can input email server and from address
    """
    msg = MIMEText(success_message, 'html')
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = get_email_list(email_list_file)
    s = smtplib.SMTP(email_server)
    s.send_message(msg, from_addr = from_address)
    s.quit()