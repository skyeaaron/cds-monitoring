# -*- coding: utf-8 -*-
"""
@author: sa325

Finds and summarizes metadata about BPAs by scanning bpa audit directory
Outputs date of:
    Release
    First Change (besides first release or last unrelease)
    Last Change (besides first release or last unrelease)
    Unrelease (if BPA is unreleased, None if BPA is current)
"""

"""
Import modules
"""
import os
import re
import csv
import sys
import yaml
#Custom modules
import processfiles as pf
import datefunctions as df

"""
Load config_file
"""
#Take command line argument for config file, exit if none specified
if len(sys.argv) == 2:
    config_file = sys.argv[1]
else:
    sys.exit('incorrect number of arguments passed. please specify config file location')


with open(config_file, 'r') as f:
    config_dict = yaml.load(f)

print("config file loaded")

"""
Get values from config_dict
Set up filepaths
"""
audit_dir= config_dict['audit_dir']

changelog_dir = pf.join_paths(audit_dir, 'changes')
current_dir = pf.join_paths(audit_dir, 'current', 'base')
original_bpa_filename= pf.join_paths(audit_dir, 'Original_BPA_List_12082017.txt')
metadata_output_filename = pf.join_paths(audit_dir, 'bpa_metadata.txt')

print("filepaths set up")
  
"""
Get list of original bpas, current bpas, bpas with at least one changefile
all bpas is union of original and bpas with changes
"""
#Original BPAs come from file listing starting BPAs
original_bpas = pf.csv_to_list(original_bpa_filename)[0]
original_bpas = set([row[0] for row in original_bpas])

#scan change folder to find bpas with changefiles
bpas_with_change = set([f.name for f in os.scandir(changelog_dir) if f.is_dir()])

#scan current folder to find current bpas
current_filenames = [f.name for f in os.scandir(current_dir)]
regex_string = r'\d*_base.html'
current_bpas = set([fname.strip('_base.html') for fname in current_filenames if re.fullmatch(regex_string, fname)])

#All bpas is original plus any with a changefile
all_bpas = set(original_bpas).union(bpas_with_change)

#Make sure all current bpas are included in the union of starting bpas and bpas with change
if current_bpas - all_bpas:
    print('something is wrong: current bpa list is not properly accounted for')
    sys.exit('something is wrong: current bpa list is not properly accounted for')
 
print("BPAs classified: original, current, change")
 
"""
Populate dictionary of BPAs with relevant dates
Save dates as strings correctly formatted
"""
#Initialize bpa_metadata dict
bpa_metadata = {bpa:{} for bpa in all_bpas}

#Save output date format odf we will use for all date string outputs
odf = '%Y-%m-%d 00:00:00.000'

#For BPAs that have at least one change file, 
#save all change dates sorted in ascending order
for bpa in bpas_with_change:
    change_dates = [f.name.strip('.html') for f in os.scandir(pf.join_paths(changelog_dir, bpa))]
    sorted_dates = sorted([df.return_datetime_object(x) for x in change_dates])
    bpa_metadata[bpa]['all changes'] = [df.generate_datestring(x, odf) for x in sorted_dates]

#For BPAs with no changes, populate with an empty list
for bpa in all_bpas - bpas_with_change:
    bpa_metadata[bpa]['all changes'] = []

#For Original BPAs, first release is 12/7/2018
for bpa in original_bpas:
    bpa_metadata[bpa]['released'] = '2017-12-07 00:00:00.000'

#For non-original BPAs, first release is the same as first changefile
for bpa in all_bpas - set(original_bpas):
    bpa_metadata[bpa]['released'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'], 0)

#For non-current BPAs, unreleased is the same as last changefile
for bpa in all_bpas - set(current_bpas):
    bpa_metadata[bpa]['unreleased'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'], -1)
    
#For current BPAs, unreleased is blank
for bpa in set(current_bpas):
    bpa_metadata[bpa]['unreleased'] = None

print("dates collected")

"""
Derive first and last change based on original and current
original, current => first change = first change, last change = last change
original, unreleased => first change = first change, last change = last change EXCLUDING FINAL DATE
non-original, current => first change = first change, last change = last change EXCLUDING FIRST DATE
non-original, unreleased => first change = first change, last change = last change EXCLUDING FIRST AND LAST DATE
Return None any time the list with exclusions applied is empty
"""
for bpa in bpa_metadata:
    if bpa in original_bpas:
        if bpa in current_bpas:
            bpa_metadata[bpa]['first change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'], 0)
            bpa_metadata[bpa]['last change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'], -1)
        else:
            bpa_metadata[bpa]['first change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'][:-1], 0)
            bpa_metadata[bpa]['last change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'][:-1], -1)
    else:
        if bpa in current_bpas:
            bpa_metadata[bpa]['first change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'][1:], 0)
            bpa_metadata[bpa]['last change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'][1:], -1)
        else:
            bpa_metadata[bpa]['first change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'][1:-1], 0)
            bpa_metadata[bpa]['last change'] = df.query_list_if_exists(bpa_metadata[bpa]['all changes'][1:-1], -1)
        pass


print("first and last change dates calculated")

"""
Save output
to file specified in metadata_output_filename
"""
with open(metadata_output_filename, 'w') as f:
    csv_f = csv.writer(f, delimiter = '\t')
    csv_f.writerow(['BPA', 'Released', 'First Change', 'Last Change', 'Unreleased'])
    for bpa in bpa_metadata:
        csv_f.writerow([bpa, bpa_metadata[bpa]['released'], bpa_metadata[bpa]['first change'], bpa_metadata[bpa]['last change'], bpa_metadata[bpa]['unreleased']])

print("output saved")
print("audit metadata complete")