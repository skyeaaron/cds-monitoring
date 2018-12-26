# -*- coding: utf-8 -*-
"""
Takes the output of two day’s results from the queries in the buildmon_queries folder,
compares the files, and sends three emails.

Two config files are required:
    one to setup the file paths and dates.
    one to specify all the input files and how they fit together.

Send three build monitor emails: concepts, groupers, patient data
The primary output of the file comparison is SectionDict which gets fed to the html templates
After the html is rendered, it is saved and emailed
"""

"""
Import modules
"""

import sys
from jinja2 import Environment, FileSystemLoader
import yaml

#Custom modules
import processfiles as pf
from processfiles import print_and_log
import datefunctions as df
import sendemails as se
import buildmonclasses as bc

#import importlib
#importlib.reload(bc)
#importlib.reload(se)
#importlib.reload(pf)


"""
Load config_file
"""
#Take command line argument for config file, exit if none specified
if len(sys.argv) == 2:
    config_file = sys.argv[1]
else:
    sys.exit('incorrect number of arguments passed. please specify config_file and sections_config_file locations')

with open(config_file, 'r') as f:
    config_dict = yaml.load(f)

#Make sure config file contains all expected keys
input_dir = pf.string_to_os_path(config_dict['input_dir'])
output_dir = pf.string_to_os_path(config_dict['output_dir'])
templates_dir = pf.string_to_os_path(config_dict['templates_dir'])
section_config_file = pf.string_to_os_path(config_dict['section_config_file'])
concept_email_list = pf.string_to_os_path(config_dict['concept_email_list'])
patient_email_list = pf.string_to_os_path(config_dict['patient_email_list'])
grouper_email_list = pf.string_to_os_path(config_dict['grouper_email_list'])
email_server = config_dict['email_server']
from_address = config_dict['from_address']
filename_format = config_dict['filename_format']

#Set the dates
try:
    #start_date and end_date should be in form 'YYYYMMDD'
    date1 = str(config_dict['start_date'])
    date2 = str(config_dict['end_date'])
except KeyError:
    (date1, date2) = df.generate_datestrings()
    print('start_date or end_date not found in configuration file; using today and yesterday instead')


"""
Initialize log file
"""
logfile = pf.join_paths(output_dir, 'buildmon_pythonlog.txt')

with open(logfile, 'w') as f:
    print('log file created')
    f.write('log file created\n')
 
print_and_log('config file loaded with values:', logfile)
for key in config_dict:
    print_and_log('\t' + key + ': ' + str(config_dict[key]), logfile)
print_and_log('dates used: ' + date1 + ', ' + date2, logfile)


"""
Load sections_config_file
Initialize buildmon Section objects
Find and summarize changes
Output to a dictionary called SectionDict for input to the html templates.
"""
with open(section_config_file, 'r') as f:
    section_config_dict = yaml.load(f)

ConceptOrder = section_config_dict.pop('Concept Order')
GrouperOrder = section_config_dict.pop('Grouper Order')
PatientOrder = section_config_dict.pop('Patient Order')

#Based on the section_config_dict, create a dictionary fi of file info subclass instances
#The simple sections are SimpleSection and the mapping sections are MappingSection
fi = {}   
typesdict = {'int':int, 'str':str}
for section in section_config_dict:
    print_and_log('initializing ' + section + ' section.', logfile)
    if section_config_dict[section]['type'] == 'simple':
        #initialize simple section with the file info
        fi[section] = bc.SimpleSection(name = section,
                          file_descriptor = section_config_dict[section]['file_descriptor'], 
                          datatypes = [typesdict[x] for x in section_config_dict[section]['datatypes']],
                          header = section_config_dict[section]['header'])
    elif section_config_dict[section]['type'] == 'map':
        #initialize mapping section with the file info
        fi[section] = bc.MappingSection(name = section,
                          file_descriptor = section_config_dict[section]['file_descriptor'], 
                          datatypes = [typesdict[x] for x in section_config_dict[section]['datatypes']],
                          header = section_config_dict[section]['header'])
    else:
        print(section + ' section has unexpected type: ' + section_config_dict[section]['type'])
    if 'id_col' in section_config_dict[section]:
        #add id_col if it exists
        fi[section].id_col = section_config_dict[section]['id_col']
    if 'name_col' in section_config_dict[section]:
        #add name_col if it exists
        fi[section].name_col = section_config_dict[section]['name_col']
    #generate filenames in the file object
    fi[section].generate_filenames(date1, date2, filename_format, input_dir)
    #create infile1only and infile2only in the file object
    try:
        fi[section].find_edits()
    except FileNotFoundError as notfound:
        #if file1 isnt found, try decreasing the date of file1 until it is found
        #then if file2 isn't found, do the same thing.
        print(section + ' WARNING: file not found')
        print(notfound.filename)
        raise
        #if notfound.filename == fi[section].file2:
        #    fi[section].generate_filenames(date1-1, date2-1, filename_format, input_dir)
        #elif notfound.filename == fi[section].file1:
        #     fi[section].generate_filenames(date1-1, date2, filename_format, input_dir)

#Format the edits by doing any labeling or mapping required.
#In SimpleSection, changes is a list of diffs.
#In MappingSection, changes is a dictionary describing the diffs.
for section in section_config_dict:
#    if 'Medi' not in section:
 #       continue
    print_and_log('formatting changes in ' + section + ' section.', logfile)
    if section_config_dict[section]['type'] == 'simple':
        if 'labels' in section_config_dict[section]:
            fi[section].label_edits(fi[section].id_col, fi[section_config_dict[section]['labels']])
        else:
            pass
        fi[section].format_changes_as_diff()
    elif section_config_dict[section]['type'] == 'map':
        fi[section].container = fi[section_config_dict[section]['container']]
        fi[section].content = fi[section_config_dict[section]['content']]
        fi[section].create_changes_dict()

#Create a final SectionDict that will be passed to the html templates.
#For the SimpleSection, we need header, changes, inboth, truncated, type
#For the MappingSection, we need changes, inboth, truncated, type
SectionDict = {}
for section in fi:
    SectionDict[section] = fi[section].template_dict()
   
print_and_log('SectionDict created for html templates', logfile)
   
"""
Load templates
Save html files
"""
#Load the html template and environment
file_loader = FileSystemLoader(pf.join_paths(templates_dir))
env = Environment(loader=file_loader)

#Concepts
template = env.get_template("buildmon_concept.txt")
buildmon_concept_html = template.render(title = 'Build Monitor: Concepts', startdate = df.prettify_datestring(date1), enddate = df.prettify_datestring(date2), sections = SectionDict, sectionorder = ConceptOrder)
pf.save_html_to_file(buildmon_concept_html, pf.join_paths(output_dir, "buildmonitor_concept_" + date1 + "_" + date2 + ".html"))
print_and_log('Buildmon concepts html file saved', logfile)

#Groupers
template = env.get_template("buildmon_grouper.txt")
buildmon_grouper_html = template.render(title = 'Build Monitor: Groupers', startdate = df.prettify_datestring(date1), enddate = df.prettify_datestring(date2), sections = SectionDict, sectionorder = GrouperOrder)
pf.save_html_to_file(buildmon_grouper_html, pf.join_paths(output_dir, "buildmonitor_grouper_" + date1 + "_" + date2 + ".html"))
print_and_log('Buildmon groupers html file saved', logfile)

#Patients
template = env.get_template("buildmon_concept.txt")
buildmon_patient_html = template.render(title = 'Build Monitor: Patient Data', startdate = df.prettify_datestring(date1), enddate = df.prettify_datestring(date2), sections = SectionDict, sectionorder = PatientOrder)
pf.save_html_to_file(buildmon_patient_html, pf.join_paths(output_dir, "buildmonitor_patient_" + date1 + "_" + date2 + ".html"))
print_and_log('Patient data html file saved', logfile)



"""
Send emails
"""
se.send_email(buildmon_concept_html, 'Build Monitor: Concepts', concept_email_list, email_server, from_address)

se.send_email(buildmon_grouper_html, 'Build Monitor: Groupers', grouper_email_list, email_server, from_address)

se.send_email(buildmon_patient_html, 'Build Monitor: Patient Data', patient_email_list, email_server, from_address)

print_and_log('Buildmon emails sent', logfile)
print_and_log('Buildmon complete', logfile)