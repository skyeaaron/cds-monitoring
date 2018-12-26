# -*- coding: utf-8 -*-
"""
Compares .csv extracts of daily bpa logic
Outputs email and html files reporting changes and current logic
"""

"""
import modules
"""
#third-party modules
import sys
from jinja2 import Environment, FileSystemLoader
import yaml
from collections import Counter
import csv

#custom modules
import processfiles as pf
from processfiles import log, print_and_log
import nesteddicts as nd
import parseclarity as pc
import sendemails as se
import difffunctions as dff
import datefunctions as df
import parsecer as pcer
import recordobjects as ro

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

"""
Get values from config_dict
Initialize log file
"""
logfile = 'audit_log_python_log.txt'
pf.create_log(logfile)

changes_paths = config_dict['changes_dirs']
current_dirs = config_dict['current_dirs']
audit_dir = config_dict['audit_dir']
templates_dir = config_dict['templates_dir']
success_email_list = config_dict['success_email_list']
failure_email_list = config_dict['failure_email_list']
email_server = config_dict['email_server']
from_address = config_dict['from_address']

#Literally require include_cer to be True or False to avoid 
#eval-ing to True on strings such as 'No'
if config_dict['include_cer'] == True:
    include_cer = True
    cer_dir = config_dict['cer_dir']
    print_and_log('include CER rules', logfile)
elif config_dict['include_cer'] == False:
    include_cer = False
    print_and_log('do  not include CER rules', logfile)
else:
    print_and_log('did not correctly specify include_CER action: use True or False in config file', logfile)
    sys.exit('did not correctly specify include_CER action: use True or False in config file')

if 'start_date' in config_dict and 'end_date' in config_dict:
    start_date = str(config_dict['start_date'])
    end_date = str(config_dict['end_date'])
    print_and_log('comparing ' + start_date + ' to ' + end_date, logfile)
else:
    print_and_log('start_date or end_date not specified. using today and yesterday.', logfile)
    (start_date, end_date) = df.generate_datestrings()

print_and_log('config file loaded with values:', logfile)
for key in config_dict:
    print_and_log('\t' + key + ': ' + str(config_dict[key]), logfile)

#Generate the folder paths where HTML files will be saved based on output_dirs list
base_current_paths = [pf.join_paths(path, 'base') for path in current_dirs]
crit_current_paths = [pf.join_paths(path, 'crit') for path in current_dirs]

"""
Parse base and criteria audit log files
Import them into dictionaries of record objects
"""
#create variables with description for summary section to allow us to easily change these
#these are hard-coded into record objects so if you want to edit them,
#need to update record objects module
added_text = "Added"
deleted_text = "Deleted"
edited_text = "Edited"
duped_text = "Duped"
unchanged_text = "Unchanged"
error_text = "Error"

#Create input filepaths for the audit logs
base_filename1 = pf.join_paths(audit_dir, 'BPA_Base_Daily_' + start_date + '.txt')
base_filename2 = pf.join_paths(audit_dir, 'BPA_Base_Daily_' + end_date + '.txt')
crit_filename1 = pf.join_paths(audit_dir, 'BPA_Criteria_Daily_' + start_date + '.txt')
crit_filename2 = pf.join_paths(audit_dir, 'BPA_Criteria_Daily_' + end_date + '.txt')

#Import the base and criteria audit logs
base_data1, base_header1 = pf.csv_to_list(base_filename1, header=True, delimit_char = '\t', encod = 'utf-16', quote = csv.QUOTE_NONE)
base_data2, base_header2 = pf.csv_to_list(base_filename2, header=True, delimit_char = '\t', encod = 'utf-16', quote = csv.QUOTE_NONE)
crit_data1, crit_header1 = pf.csv_to_list(crit_filename1, header=True, delimit_char = '\t', encod = 'utf-16', quote = csv.QUOTE_NONE)
crit_data2, crit_header2 = pf.csv_to_list(crit_filename2, header=True, delimit_char = '\t', encod = 'utf-16', quote = csv.QUOTE_NONE)

#Trim the headers
base_header1 = base_header1[1:]
base_header2 = base_header2[1:]
crit_header1 = crit_header1[1:]
crit_header2 = crit_header2[1:]

#Transform the inputs into record dictionaries of record objects
base_records_dict = ro.initialize_records_dict(base_data1, base_data2, 'base')
crit_records_dict = ro.initialize_records_dict(crit_data1, crit_data2, 'crit')

for base in base_records_dict:
    base_records_dict[base].find_linked_criteria(base_header1.index('Linked Criteria'), base_header2.index('Linked Criteria'))

for crit in crit_records_dict:
    crit_records_dict[crit].find_linked_criteria(crit_header1.index('Linked Criteria'), crit_header2.index('Linked Criteria'))
    crit_records_dict[crit].find_rules([crit_header1.index('Include Rule'), crit_header1.index('Exclude Rule')],
                                        [crit_header2.index('Include Rule'), crit_header2.index('Exclude Rule')])

#find all linked rules so we can limit the rule import later
relevant_rules = set()
for crit in crit_records_dict:
    #relevant_rules = relevant_rules | crit_records_dict[crit].old_rules
    relevant_rules = relevant_rules | crit_records_dict[crit].new_rules


#If any of the input files had multiple non-identical rows for a single record, report it
[print_and_log('multiple rows for base record: ' + base_id, logfile) for base_id in  base_records_dict if  base_records_dict[base].classification == duped_text]
[print_and_log('multiple rows for crit record: ' + crit_id, logfile) for crit_id in  crit_records_dict if  crit_records_dict[crit].classification == duped_text]

print_and_log('base and criteria files imported successfully', logfile)

"""
If include_cer is set to True,
Parse the CER base and property files
Import them into a dictionary of cerbase record objects
The properties are turned into a field in the cerbase objects
"""

def set_up_cer(cer_dir, restrict_to = None):    
    #Create input filepaths for the cerbase and cerproperty files
    cerbase_filename1 = pf.join_paths(cer_dir, "-CERBase-" + start_date + ".txt")
    cerbase_filename2 = pf.join_paths(cer_dir, "-CERBase-" + end_date + ".txt")
    cerprop_filename1 = pf.join_paths(cer_dir, "-CERProperty-" + start_date + ".txt")
    cerprop_filename2 = pf.join_paths(cer_dir, "-CERProperty-" + end_date + ".txt")
    #import data
    #if we have memory issues, could be smarter and only import data for rules
    #that are linked to criteria. For now, import all cer data.
    cerbase_data1, cerbase_header1 = pf.csv_to_list(cerbase_filename1, encod = 'cp1252', delimit_char = '\t', quote = csv.QUOTE_NONE)
    cerbase_data2, cerbase_header2 = pf.csv_to_list(cerbase_filename2, encod = 'cp1252', delimit_char = '\t', quote = csv.QUOTE_NONE)
    cerprop_data1, cerprop_header1 = pf.csv_to_list(cerprop_filename1, encod = 'cp1252', delimit_char = '\t', quote = csv.QUOTE_NONE)
    cerprop_data2, cerprop_header2 = pf.csv_to_list(cerprop_filename2, encod = 'cp1252', delimit_char = '\t', quote = csv.QUOTE_NONE)
    #Trim the headers and create a dictionary mapping the base to the properties
    cerbase_header1 = cerbase_header1[1:]
    cerbase_header2 = cerbase_header2[1:]
    cerprop_dict1, cerprop_header1 = pcer.cer_property_dict(cerprop_data1, cerprop_header1)
    cerprop_dict2, cerprop_header2 = pcer.cer_property_dict(cerprop_data2, cerprop_header2)
    #Append the properties to the cer base data
    pcer.append_properties_to_base(cerbase_data1, cerprop_dict1, cerbase_header1, cerprop_header1)
    pcer.append_properties_to_base(cerbase_data2, cerprop_dict2, cerbase_header2, cerprop_header2)
    #Create a dictionary of record objects
    rule_records_dict = ro.initialize_records_dict(cerbase_data1, cerbase_data2, 'cerbase', restrict_to)
    return rule_records_dict, cerbase_header1, cerbase_header2

#if CER, import the cer data
#need to explicitly require include_cer to be True rather than require it to exist
if include_cer == True:
    rule_records_dict, rule_header1, rule_header2 = set_up_cer(cer_dir, restrict_to = relevant_rules)
    rule_edited = set(rule for rule in rule_records_dict if rule_records_dict[rule].classification == edited_text)
    print_and_log('CER base and property files imported successfully', logfile)

"""
Not in use.
Section to report any CER rules that are linked to criteria
but missing from the rules files
all_old_rules = ro.set_union([crit_records_dict[crit].old_rules for crit in crit_records_dict])
all_new_rules = ro.set_union([crit_records_dict[crit].new_rules for crit in crit_records_dict])
unmapped_rules1 = all_old_rules - rule_records_dict.keys()
unmapped_rules2 = all_new_rules - rule_records_dict.keys()
with open('unmapped_CER_rules_'+start_date+'.txt', 'w') as f:
    for rule in unmapped_rules1:
        f.write(rule+'\n')
with open('unmapped_CER_rules_'+end_date+'.txt', 'w') as f:
    for rule in unmapped_rules2:
        f.write(rule+'\n')
"""

"""
Create nested map
to identify base records that are linked to
edited criteria records or edited rule records
Records may be nested, so map is populated recursively
"""
#determine which records go in which map based on presence of old or new data
#exclude duplicated records which might be inaccurate
base_crit_map2 = {base: base_records_dict[base].new_linked_criteria for base in base_records_dict if base_records_dict[base].new_data and base_records_dict[base].classification != duped_text}
crit_crit_map2 = {crit: crit_records_dict[crit].new_linked_criteria for crit in crit_records_dict if crit_records_dict[crit].new_data and crit_records_dict[crit].classification != duped_text}

#Initialize the nested_map for reporting logic edits
edited_nested_map = {}
#Populate nesting map with any base records that map to some crit in new data
for base in base_crit_map2:
    edited_nested_map[base] = {}
    for crit in base_crit_map2[base]:
        edited_nested_map[base][crit] = nd.populate_nested_map(crit, crit_crit_map2)

#find edited crit (crit directly edited)
#if we are including CER rules,
#add on any criteria that have at least one edited CER rule in the current rules 
crit_edited = set(crit for crit in crit_records_dict if crit_records_dict[crit].classification == edited_text)
if include_cer == True:
    crit_edited = crit_edited | set(crit for crit in crit_records_dict if crit_records_dict[crit].new_rules & rule_edited)

#Only retain branches with at least one ancestor on the edited criteria list               
#Must use static list as iterator because we edit the dictionary within the loop
for base in list(edited_nested_map.keys()):
    nd.delete_unwanted_nodes(base, edited_nested_map, crit_edited)

#update base in the base_records_dict that were unchanged but are linked to an edited criteria
for base in edited_nested_map:
    if base_records_dict[base].classification == unchanged_text:
        base_records_dict[base].classification = edited_text

print_and_log('criteria and base mapped', logfile)

"""
Diff HTML Block
Create dictionaries for each of the sections that will be in the comparison output
DupSection, ErrorSection, DelSection, AddSection, EditSection, SummarySection
Any criteria edits that effect base records are added in the EditSection
(>>>Compare the headers in both files---not currently doing this)
Put everything into a big SectionDict so that change files for each individual 
BPA can be generated appropriately
"""

DupSection = {}
ErrorSection = {}
DelSection = {}
AddSection = {}
EditSection = {}
CritEditSection = {}
HeaderSection = {}

def create_EditSection_entry(record, header2, edited_nested_map, crit_records_dict, crit_header2, rule_records_dict, rule_edited, rule_header2):
    """
    Return a dictionary reporting edits for a record
    Recursively adds criteria edits based on any entries in the nested_dict reporting criteria edits
    Recursively adds rule edits base on presence of rules in record.new_rules attribute
    """
    table_fields = pc.identify_table_fields(header2)
    output = {'name': record.find_name()}
    #initialize field edits, a dictionary with fieldname: fielddiffs for any edits
    output['field edits'] = {}
    #initialize table edits, a dictionary of dictionaries, tablename: {'table header': tableheader, 'diff':diffs}
    output['table edits'] = {}
    #initialize crit edits, a dictionary of any linked/nested criteria with edits
    output['crit edits'] = {}
    #initialize rule edits, a dictionary of any linked/nested CER rules with edits
    output['rule edits'] = {}
    #look through all the edited indexes associated with the record
    if record.classification == edited_text:
        for index in record.edits:
            #for those indexes that are tables, do a table diff
            if index in table_fields:
                table_name, table_dict = dff.report_table_changes(header2[index], record.old_data[index], record.new_data[index])
                output['table edits'][table_name] = table_dict
            #otherwise do a field diff
            else:
                output['field edits'][header2[index]] = dff.diff_field(record.old_data[index], record.new_data[index])
                for row in output['field edits'][header2[index]]:
                    row[1] = pc.format_multi_column_field(row[1])
    else:
        pass
    #find any edited rules linked to the record in the current log
    for rule in record.new_rules & rule_edited:
        output['rule edits'][rule] = create_EditSection_entry(rule_records_dict[rule], rule_header2, edited_nested_map, crit_records_dict, crit_header2, rule_records_dict, rule_edited, rule_header2)
    #see if record is in the nested_dict
    if record.id in edited_nested_map:
        #look through any criteria linked to the record and recursively create
        #EditSection entries for each, stored within the crit edits dict
        for crit in edited_nested_map[record.id]:
            output['crit edits'][crit] = create_EditSection_entry(crit_records_dict[crit], crit_header2, edited_nested_map[record.id], crit_records_dict, crit_header2, rule_records_dict, rule_edited, rule_header2)
    return output


#Generate each of the sections (each section is a dictionary containing base record ids as keys)
for base in base_records_dict:
    if base_records_dict[base].classification == duped_text:
        DupSection[base] = {'name': base_records_dict[base].find_name()}
        
    elif base_records_dict[base].classification == error_text:
        ErrorSection[base] = {'name': base_records_dict[base].find_name()}
        
    elif base_records_dict[base].classification == deleted_text:
        DelSection[base] = {'name': base_records_dict[base].find_name()}
        
    elif base_records_dict[base].classification == added_text:
        AddSection[base] = {'name': base_records_dict[base].find_name()}
        #add a dictionary with the crit id and crit name for any linked criteria
        #this only displays directly linked criteria
        AddSection[base]['crit'] = {crit: crit_records_dict[crit].find_name() for crit in base_records_dict[base].new_linked_criteria}

    elif base_records_dict[base].classification == edited_text: 
        EditSection[base] = create_EditSection_entry(base_records_dict[base], base_header2, edited_nested_map, crit_records_dict, crit_header2, rule_records_dict, rule_edited, rule_header2)

    else:
        pass

#Create SummarySection
SummarySection = {"Total BPAs": len(base_records_dict)}
SummarySection['Count Sections'] = Counter([base_records_dict[base].classification for base in base_records_dict])
#any keys in 'Count Sections' must also be keys in 'Display Text' or template render will fail
SummarySection['Display Text'] = {deleted_text:"Unreleased since prior log",
              added_text:"Released since prior log",
              edited_text:"Edited since prior log",
              duped_text:"In both logs, with duplications",
              unchanged_text:"Unchanged since prior log",
              error_text:"With unexpected error"}

#Put allthe sections together into one dictionary
SectionDict = {duped_text:DupSection,
              error_text:ErrorSection,
              deleted_text:DelSection,
              added_text:AddSection,
              edited_text:EditSection,
              'HeaderSection':HeaderSection,
              'SummarySection':SummarySection}

print_and_log('html sections created for change reporting', logfile)

"""
OUTPUT
and
EMAILS
Save output files and send emails
HTML is generated using jinja and templates
"""
file_loader = FileSystemLoader(templates_dir)
env = Environment(loader=file_loader)

"""
BPA Audit Log Main Output
Save main comparison file and send email
"""
audit_template = env.get_template("bpa_audit_log.txt")
html_for_file = audit_template.render(title = 'BPA Audit Log: ' + df.prettify_datestring(end_date), 
                                      date1 = df.prettify_datestring(start_date),
                                      date2 = df.prettify_datestring(end_date),
                                      DupSection = DupSection, 
                                      DelSection = DelSection, 
                                      ErrorSection = ErrorSection, 
                                      AddSection = AddSection,
                                      EditSection = EditSection,
                                      HeaderSection = HeaderSection,
                                      SummarySection = SummarySection)

for path in changes_paths:
    try:
        pf.save_html_to_file(html_for_file, pf.join_paths(path, end_date + '.html'))
        log('main html file saved', logfile)
    except:
        se.send_failure("could not save master diff html file in path " + path + "\n" + str(sys.exc_info()), email_server, from_address)
        print_and_log('something went wrong while saving main html file', logfile)
        raise

try:
    se.send_email(html_for_file, 'BPA Audit Log: ' + end_date, success_email_list, email_server, from_address)
    log('email sent', logfile)
except:
    print_and_log('something went wrong while sending success email', logfile)
    raise


"""
BPA-Level Changes
Using the SectionDict already created,
Save an html file for each BPA with any changes
Send an email and raise an exception if any of the saves fail
"""
standalone_change_template = env.get_template("standalone_change.txt")

for base in base_records_dict:
    if base_records_dict[base].classification == unchanged_text:
        pass
    else:
        outputhtml = standalone_change_template.render(base = base, 
                                                       category = base_records_dict[base].classification, 
                                                       base_dict = SectionDict[base_records_dict[base].classification][base], 
                                                       date1 = df.prettify_datestring(start_date), 
                                                       date2 = df.prettify_datestring(end_date))
        for path in changes_paths: 
            try:
                dirname = pf.join_paths(path, str(base))
                filename = pf.join_paths(dirname, end_date + '.html')
                pf.create_dir(dirname)
                pf.save_html_to_file(outputhtml, filename)
            except:
                print_and_log('failure')
                se.send_failure("Something went wrong while saving changes file for " + str(base) + "in path " + path, email_server, from_address)
                raise

print_and_log('base change files saved', logfile)

"""
Daily Logic
Save html files summarizing logic for all current Criteria records
Save html files summarizing logic for all current Base records
Raise an error if the old files cannot be deleted.
Save a warning in the log file if any of the new files can't be saved.
"""
def create_Current_section(record, header, crit_records_dict, crit_header, rule_records_dict, rule_header):
    """
    Function to generate a nested dictionary summarizing the rule logic
    for a record object and all its linked criteria
    Given a record object, generates the current dictionary
    Recursively populates criteria
    so that each criteria in it will also populate their own criteria
    Recursively populates rules
    Outputs a dictionary containing four main keys:
        'fields', 'tables', 'rule', and 'crit'
    note that fields and tables are list of lists and thus ordered
        'fields': [[field1 name, [field, entries]], [field2 name, [field, entries]]]
    each row is the name of the field and then another list containing all lines in the field
    crit and rule are dictionaries, so order is not the same every time
    """
    #print(record.id)
    outputdict = {}
    table_fields = pc.identify_table_fields(header)
    outputdict['fields'] = []
    outputdict['tables'] = []
    outputdict['crit'] = {}
    outputdict['rule'] = {}
    for index, field_data in enumerate(record.new_data):
        if field_data:
            #for any fields that are not tables where the base contains data, add that data to the 'fields' key
            if index not in table_fields:
                outputdict['fields'].append([header[index], pc.parse_field(pc.format_multi_column_field(field_data))])
            #for any fields that are tables where the base contains data, add that data to the 'tables' key
            else:
                rows = pc.parse_field(record.new_data[index])
                table_data = [pc.parse_row(row) for row in rows]
                table_name, table_header = pc.extract_table_info(header[index])
                outputdict['tables'].append([table_name, table_header, table_data])
    #if the record (should be criteria only) is linked to any CER rules, add them to the rule section
    for rule in record.new_rules:
        #print('checking rule')
        if rule not in rule_records_dict:
            outputdict['rule'][rule] = {'fields':[['Error', ['Rule not found in CER base data']]]}
        else:
            outputdict['rule'][rule] = create_Current_section(rule_records_dict[rule], rule_header, crit_records_dict, crit_header, rule_records_dict, rule_header)
    #if the base record is linked to any criteria, generate current_base dictionaries for each of those
    #recursively, and add them to the 'crit' key
    for crit in record.new_linked_criteria:
        #print('checking crit')
        outputdict['crit'][crit] = create_Current_section(crit_records_dict[crit], crit_header, crit_records_dict, crit_header, rule_records_dict, rule_header)
    return outputdict

#Put all the current sections into two dictionaries
base_current_dict = {base: create_Current_section(base_records_dict[base], base_header2, crit_records_dict, crit_header2, rule_records_dict, rule_header2) for base in base_records_dict if base_records_dict[base].new_data}
crit_current_dict = {crit: create_Current_section(crit_records_dict[crit], crit_header2, crit_records_dict, crit_header2, rule_records_dict, rule_header2) for crit in crit_records_dict if crit_records_dict[crit].new_data}

# Make indexes of all the base and criteria record reported
# Generate list of current crit and their names and sort
current_base = [[int(base), base_records_dict[base].find_name()] for base in base_current_dict]
current_base.sort()
current_crit = [[int(crit), crit_records_dict[crit].find_name()] for crit in crit_current_dict]
current_crit.sort()

#Load the Templates
index_template = env.get_template("current_audit_index.txt")
unreleased_template = env.get_template("unreleased_record.txt")
current_logic_template = env.get_template("current_logic_master.txt")

print_and_log("Daily Logic HTML templates loaded", logfile)

#Current Crit Save
    #1. Delete old files. If this fails send an email and raise error.
    #2. Save daily logic. If this fails send an email and raise error.
    #3. Save html index file
    #4. Save generic unreleased html file (so we can have a link for records that no longer exist)
for path in crit_current_paths:
    try:
        print('Deleting current criteria files')
        print_and_log(pf.delete_html_files(path), logfile)
    except:
        se.send_failure("Could not delete current crit files in path " + path, email_server, from_address)
        raise
    else:
        try:
            print('Saving current criteria files')
            for crit in crit_current_dict:
                crit_current_html = current_logic_template.render(id=crit, current_dict = crit_current_dict[crit])
                pf.save_html_to_file(crit_current_html, pf.join_paths(path, crit + '_crit.html'))
        except:
            print_and_log('Current crit logic failed to save', logfile)
            print_and_log(str(sys.exc_info()), logfile)
            se.send_failure("Could not save current crit files. Failed on crit " + crit, email_server, from_address)
            raise
        else:
            print_and_log('Current crit logic files saved', logfile)
    try:
        crit_index_html = index_template.render(title = 'Index of Current Criteria Records', 
                                                asofdate = df.prettify_datestring(end_date), 
                                                recordtype = 'crit', 
                                                records = current_crit)
        pf.save_html_to_file(crit_index_html, pf.join_paths(path, "index.html"))
    except:
        print_and_log('WARNING: Crit index file failed to save', logfile)
    else:
        print_and_log('Crit index.html saved', logfile)
    try:
        unreleased_crit_html = unreleased_template.render(title = 'Unreleased Criteria Record')
        pf.save_html_to_file(unreleased_crit_html, pf.join_paths(path, "unreleased_crit.html"))
    except:
        print_and_log('WARNING: Generic unreleased crit file failed to save.', logfile)
    else:
        print_and_log('Generic unreleased crit file saved.', logfile)

#Current Base Save
for path in base_current_paths:
    try:
        print('Deleting current base files')
        print_and_log(pf.delete_html_files(path), logfile)
    except:
        se.send_failure("Could not delete current base files in path " + path, email_server, from_address)
        raise
    else:
        try:
            print('Saving current base files')
            for base in base_current_dict:
                base_current_html = current_logic_template.render(id=base, current_dict = base_current_dict[base])
                pf.save_html_to_file(base_current_html, pf.join_paths(path, base + '_base.html'))
        except:
            print_and_log('Current base logic failed to save', logfile)
            print_and_log(str(sys.exc_info()), logfile)
            se.send_failure("Could not save current base files. Failed on base " + base, email_server, from_address)
            raise
        else:
            print_and_log('Current base logic files saved', logfile)
    try:
        base_index_html = index_template.render(title = 'Index of Current Base Records', 
                                                asofdate = df.prettify_datestring(end_date), 
                                                recordtype = 'base', 
                                                records = current_base)
        pf.save_html_to_file(base_index_html, pf.join_paths(path, "index.html"))
    except:
        print_and_log('WARNING: Base index file failed to save', logfile)
    else:
        print_and_log('Base index.html saved', logfile)
    try:
        unreleased_base_html = unreleased_template.render(title = 'Unreleased Base Record')
        pf.save_html_to_file(unreleased_base_html, pf.join_paths(path, "unreleased_base.html"))
    except:
        print_and_log('WARNING: Generic unreleased base file failed to save.', logfile)
    else:
        print_and_log('Generic unreleased base file saved.', logfile)

print_and_log("Daily Logic Records Saved", logfile)
print_and_log("Done", logfile)
"""
#Send contents of log file to whomever is on the failure email list
with open(logfile,'r') as f:
    logcontents = f.read()
logcontents = logcontents.replace('\n', '<br>')
se.send_email(logcontents, 'Audit Log Log Contents', failure_email_list, email_server, from_address)
"""