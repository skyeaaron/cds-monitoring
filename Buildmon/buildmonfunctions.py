 # -*- coding: utf-8 -*-
"""
Module with support functions for buildmon.py, buildmonclasses.py
"""

def sorted_ids(input_list, index):
    """
    extract specified column from list of lists
    return unique values sorted
    meant for use with a list of lists of new or deleted grouper mappings
    returns a sorted list of unique items in one of the columns
    sorted_ids(infile2only, 0)
    """
    output_list = list(set([row[index] for row in input_list]))
    output_list.sort()
    return output_list


def label_changes(changes_table, lookup_index, label_dict):
    """
    given a list of lists and an index you would like to label
    plus a dict containing the lookup values and labels
    insert the labels in column after the lookup index
    This modifies the list in place and returns None
    """
    for row in changes_table:
        row.insert(lookup_index + 1, label_dict[row[lookup_index]])
    return None

def label_changes_multi(changes_table, lookup_index, label_dict):
    """
    Currently not in use.
    For labelling with multiple columns
    given a list of lists and an index you would like to label
    plus a dict containing the lookup values and labels
    insert the labels in column after the lookup index
    This modifies the list in place and returns None
    """
    for row in changes_table:
        row[lookup_index + 1: lookup_index + 1] = label_dict[row[lookup_index]]
    return None

def changes_to_diff(infile1only, infile2only):
    """
    Given two lists of lists, one for records in the old file only
    and one for records in the new file only,
    combine them, adding a column with - or +
    and then sort by column 1 in the new list
    (column 1 since column 0 contains the diff symbol)
    """
    changes = [['- '] + row for row in infile1only]
    changes.extend([['+ '] + row for row in infile2only])
    changes.sort(key=lambda x: x[1])
    return changes

