# -*- coding: utf-8 -*-
"""
Module with functions for handling audit logs and comparing them
Used in compare_base.py
"""
def populate_nested_map(item, lookup_dict, depth = 0):
    """
    recursively look up item in the lookup_dict
    and see if it contains any subitems that are in the lookup_dict
    """
    depth += 1
    if item not in lookup_dict:
        return {}
        depth -= 1
    else:
        output = {}
        for subitem in lookup_dict[item]:
            output[subitem] = populate_nested_map(subitem, lookup_dict)
        return output
    
    
    
def delete_unwanted_nodes(key, input_dict, keep_list, depth = 0):
    """
    Recursive
    Relies on the fact that the value for each key is either empty set
    or a dictionary of criteria
    Delete any nodes where none of the children are on the keep list
    """
    #If the input_dict[key] contains anything:
    if input_dict[key]:
        #Loop through all the items it contains.
        #If any of the items it contains returns a value greater than 0,
        #then we need to keep the key itself, so return 1.
        #Otherwise, delete the entire key and return 0.
        #There is a depth counter in here right now but it is non-functional
        #could add a depth cap if needed
        depth += 1
        subtotal = 0
        #need a static sublist of keys because we will be recursively deleting keys as we go
        sublist = list(input_dict[key].keys())
        for subkey in sublist:
            subtotal += delete_unwanted_nodes(subkey, input_dict[key], keep_list, depth)
        if subtotal == 0:
            input_dict.pop(key)
            return 0
        else:
            return 1
        depth -=1
    #If the input_dict[key] is empty set:
    #Return 1 if the key is on the keep_list.
    #Otherwise delete the entire key and return 0.
    else:
        if key not in keep_list:
            input_dict.pop(key)
            return 0
        else:
            return 1