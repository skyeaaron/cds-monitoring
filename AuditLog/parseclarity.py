# -*- coding: utf-8 -*-
"""
Functions to support parsing the clarity audit log csv files
!!! is a row
||| is a column
"""

import re



def parse_linked_criteria(field_data, regex_string = r'\[(\d*)\]'):
    """
    Given a string, looks for numbers in square brackets
    returns all matching numbers as a set
    #test = '1 - CL PHS CDS ED LABS ABNORMAL TROPONIN [1601000029]!!!2 - CL PHS CDS EXCLUDE OUTSIDE CONSULTING PHYSICIANS [3528]!!!3 - CL PHS CDS ED INCLUDE ONLY ED LOGIN DEPARTMENT USERS [1601000119]!!!4 - CL PHS CDS ED INCLUDE ONLY UCC LOGIN DEPARTMENT USERS [6906]!!!5 - CL PHS CDS ED EXCLUDE RULE CHECK ED DEPART EVENT EXISTS [1601000122]!!!6 - CL PHS CDS ED EXCLUDE DISCHARGE DISPOSITION [1601100020]'
    parse_linked_criteria(test)
    {'1601000029', '3528', '1601000119', '6906', '1601000122', '1601100020'}
    """
    criteria = re.findall(regex_string, field_data)
    return set(criteria)

def identify_table_fields(header):
    """
    given a header list,
    returns those indexes where the field is really a table
    these are identified by presence of a colon in the field name
    """
    return [i for i,field in enumerate(header) if ':' in field]

def parse_field(field):
    """
    given string with rows delimited by !!!
    return a list of the rows
    """
    return field.split('!!!')

def parse_row(row):
    """
    given string with columns delimited by !!!
    return a list of the columns
    """
    return row.split('|||')

def extract_table_info(header_field):
    """
    get the name of the table 
    and the table header
    from the info in a string
    header_field = 'Inclusion Restrictions: SA - Loc - Loc Grouper - Specialty - Dep - Dep Grouper - Enc Type - Prov Type'
    """
    #table name is string up to the colon
    table_name, columns = header_field.split(': ')
    #colnames are string after the colon, then parsed on ' - '
    col_names = columns.split(' - ')
    return table_name, col_names

def format_multi_column_field(field):
    """
    Occasionally there are non-table fields with multiple columns, such as:
    Linked BPA Trigger - Lookback Hours.
    Exclude Procedures - Lookback - Applies To parsing
    We want to display these in the final html file as a single field separated with ' - '.
    For these we need to after-the-fact replace '|||' with ' - '.
    """
    return field.replace('|||',' - ')



