# -*- coding: utf-8 -*-
"""
Functions to support parsing CER base and property files

To match clarity format for audit logs:
    !!! is a row
    ||| is a column
Treat each CER property as a row rather than a table
"""

def combine_property_fields(row, char = ';'):
    """
    given a list of property fields, 
    remove whitespace and
    concatenate them with a semicolon
    """
    row = [x.strip() for x in row]
    return '; '.join(row)

def cer_property_dict(cer_prop, header):
    """
    given a list of lists with cer properties
    return a dictionary, with the cer rule ids as keys
    and all associated properties in string delimited with the row and column
    delimiters !!! and |||
    basically, for each rule, we turn the list of properties into just another 
    field that can be diffed
    trim the header to delete column 1
    """
    outputdict = {}
    for row in cer_prop:
        #for each row, the first column is the key
        #make a list of rows associated with each key
        try:
            outputdict[row[0]].append(combine_property_fields(row[1:]))
        except KeyError:
            outputdict[row[0]] = [combine_property_fields(row[1:])]
    #now turn each list into a string using !!! as the delimiter
    for rule in outputdict:
        outputdict[rule] = '!!!'.join(outputdict[rule])
    return outputdict, '; '.join(header[1:])

def append_properties_to_base(cer_base_data, cer_property_dict, cer_base_header, cer_property_fieldname):
    """
    given a list of lists called cer_base_data
    add a column with the property data
    also add a column to the base_header
    """
    #cer_base_header.append(cer_property_fieldname)
    cer_base_header.append('Rule Properties')
    for row in cer_base_data:
        if row[0] in cer_property_dict:
            row.append(cer_property_dict[row[0]])
        else:
            row.append('')
    return None