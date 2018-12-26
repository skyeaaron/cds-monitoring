# -*- coding: utf-8 -*-
"""
module with functions to support diffing the logic
used in compare_base.py
"""

import parseclarity as pc
import difflib

#import importlib
#importlib.reload(pc)

def diff_lists(list1, list2):
    """
    Given two lists, find the change in items.
    Example:
    field1 = '1 - CL EXCLUDE MRSA AND MRSA/MSSA LAB ORDER WITHIN LAST 7 DAYS [5257]!!!2 - CL PHS CDS HAS ACTIVE MRSA INFECTION [3040001402]!!!3 - CL IP BWH NICU DEPARTMENTS [5209]!!!4 - CL PHS CDS IP EXCLUDE HOD DEPARTMENTS [3128]!!!5 - CL PHS CDS EXCLUDE OUTSIDE CONSULTING PHYSICIANS [3528]!!!6 - CL PHS CDS IS PATIENT DISCHARGED [5216]!!!7 - CL PHS CDS ANES PROVIDER LOGIN DEPT [5949]'
    field2 = '1 - CL PHS CDS DUE FOR WEEKLY MRSA SCREENING BUNDLE [7002000155]'
    list1 = pc.parse_field(field1)
    list2 = pc.parse_field(field2)
    diff_lists(list1, list2)
    Out[44]: 
    [['+ ', '1 - CL PHS CDS DUE FOR WEEKLY MRSA SCREENING BUNDLE [7002000155]'],
     ['- ',
      '1 - CL EXCLUDE MRSA AND MRSA/MSSA LAB ORDER WITHIN LAST 7 DAYS [5257]'],
     ['- ', '2 - CL PHS CDS HAS ACTIVE MRSA INFECTION [3040001402]'],
     ['- ', '3 - CL IP BWH NICU DEPARTMENTS [5209]'],
     ['- ', '4 - CL PHS CDS IP EXCLUDE HOD DEPARTMENTS [3128]'],
     ['- ', '5 - CL PHS CDS EXCLUDE OUTSIDE CONSULTING PHYSICIANS [3528]'],
     ['- ', '6 - CL PHS CDS IS PATIENT DISCHARGED [5216]'],
     ['- ', '7 - CL PHS CDS ANES PROVIDER LOGIN DEPT [5949]']]
    """
    d = difflib.Differ()
    result = list(d.compare(list1, list2))
    result = [[row[0:2], row[2:]] for row in result if row[0]!='?']
    return result

def diff_field(field1, field2):
    """
    parse the fields and diff them
    """
    return diff_lists(pc.parse_field(field1), pc.parse_field(field2))


def pad_list(mylist, number, fill_item = ''):
    """
    if provided list is shorter than length specified,
    pad with fill_item. default is empty strings ''
    pad_list([1,2,3], 6)
    > [1, 2, 3, '', '', '']
    pad_list([1,2,3], 6, ['cabbage'])
    > [1, 2, 3, ['cabbage'], ['cabbage'], ['cabbage']]
    """
    if len(mylist) < number:
        mylist.extend( [fill_item]*(number - len(mylist)) )
    return mylist

def diff_table(field1, field2):
    """
    first diff the fields as if they were normal fields
    (this will automatically separate the rows and diff each one)
    then split on the columns in the resulting list of changes
    Sometimes one of the fields is blank. Pad with empty strings.
    Example:
        field1 = '|||||||||||||||||||||Physician [1]!!!|||||||||||||||||||||Midwife [5]!!!|||||||||||||||||||||Physician Assistant [6]!!!|||||||||||||||||||||Nurse Practitioner [9]!!!|||||||||||||||||||||Resident [113]!!!|||||||||||||||||||||Fellow [116]!!!|||||||||||||||||||||Anesthesiologist [4]!!!|||||||||||||||||||||Nurse Anesthetist [2]'
        field2 = '|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Physician [1]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Midwife [5]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Physician Assistant [6]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Nurse Practitioner [9]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Resident [113]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Fellow [116]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Anesthesiologist [4]!!!|||||||||||||||DEP PHS CDS BWH NICU MRSA SCREENING [101873]||||||Nurse Anesthetist [2]'
    diff_table(field1, field2)
    """
    row_diffs = diff_field(field1, field2)
    output = [[row[0]] + pc.parse_row(row[1]) for row in row_diffs]
    max_cols = max([len(row) for row in output])
    output = [pad_list(row, max_cols, '') for row in output]     
    return output

def report_table_changes(header_field, field1, field2):
    """
    given the table header field
    and the two table fields
    return a dictionary summarizing the changes
    """
    table_name, col_names = pc.extract_table_info(header_field)
    edits = diff_table(field1, field2)
    #for row in edits:
    #    if len(col_names) == len(row):
    #        print ("HOORAY")
    return table_name, {'table header': col_names, 'diff': edits}

