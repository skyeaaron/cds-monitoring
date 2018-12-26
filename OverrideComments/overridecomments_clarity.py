# -*- coding: utf-8 -*-
"""
Send an email summarizing override comments for all BPAs
Attach a csv file with override comments and data from start to end date
This version of the script takes the csv file as the input rather than the query
"""

"""
import modules
"""
from jinja2 import Environment, FileSystemLoader
import csv
import pyodbc
import sys
import yaml
#Custom modules
import processfiles as pf
from processfiles import print_and_log
import datefunctions as df
import sendemails as se

"""
Load config_file
and all required keys
"""
#Take command line argument for config file, exit if none specified
if len(sys.argv) == 2:
    config_file = sys.argv[1]
else:
    sys.exit('incorrect number of arguments passed. please specify config_file location.')

with open(config_file, 'r') as f:
    config_dict = yaml.load(f)

#Make sure config file contains all required keys
input_file = pf.string_to_os_path(config_dict['input_file'])
output_dir = pf.string_to_os_path(config_dict['output_dir'])
templates_dir = pf.string_to_os_path(config_dict['templates_dir'])
email_list = pf.string_to_os_path(config_dict['email_list'])
email_server = config_dict['email_server']
from_address = config_dict['from_address']

"""
Initialize log file
"""
logfile = pf.join_paths(output_dir, 'overridecomments_pythonlog.txt')

with open(logfile, 'w') as f:
    print('Log file created')
    f.write('Log file created\n')
 
print_and_log('Config file loaded with values:', logfile)
for key in config_dict:
    print_and_log('\t' + key + ': ' + str(config_dict[key]), logfile)

"""
Set up the dates based on optional keys in config_file.
Defaults to daily with today and yesterday calculated automatically.
If dates are specified then frequency mode is ignored. Dates should be YYYYMMDD.
Start date may be omitted if end date and frequency are specified.
If only frequency is specified, uses today as the end date.
"""
if 'start_date' in config_dict and 'end_date' in config_dict:
    start_date = str(config_dict['start_date'])
    end_date = str(config_dict['end_date'])
    frequency = 'custom'
    print_and_log('Using start_date and end_date specified in config file', logfile)
elif 'end_date' in config_dict and 'freqency' in config_dict:
    start_date, end_date = df.calc_start_and_end(str(config_dict['end_date']), config_dict['frequency'])
    frequency = config_dict['frequency']
    print_and_log('Using end_date and frequency specified in config file.', logfile)
elif 'frequency' in config_dict:
    end_date = df.generate_datestring()
    start_date, end_date = df.calc_start_and_end(end_date, config_dict['frequency'])    
    frequency = config_dict['frequency']
    print_and_log('end_date not specified in config file. Using today with frequency specified in config file.', logfile)
else:
    frequency = "daily"
    start_date, end_date = df.generate_datestrings()
    print_and_log('end_date and frequency not specified in config file. Comparing today to yesterday.', logfile)

print_and_log('Dates used: ' + start_date + ', ' + end_date, logfile)

"""
Generate output filenames
based on frequency and date
"""
#prettify the dates
start_date = df.prettify_datestring(start_date)
end_date = df.prettify_datestring(end_date)
#Generate the output filenames using end_date and frequency
comments_csvfile = frequency + '_comments_data_' + end_date + '.csv'
comments_htmlfile = frequency + '_comments_report_' + end_date + '.html'

"""
SQL block
Query EDW using Override_Comments.sql (input_file) query
"""
#Read sql queries file
with open(input_file) as f:
    sqlquery = f.read()

#populate start_date in the sql queries
sqlquery = sqlquery.replace('{{ STARTDATE }}', "'" + start_date + "'")
sqlquery = sqlquery.replace('{{ ENDDATE }}', "'" + end_date + "'")

#split up sqlquery text into individual queries
sqlCommands = sqlquery.split(';')

#Connect to SQLServer database
print("List of available odbc drivers: \n", pyodbc.drivers())
conn = pyodbc.connect(r"DRIVER={SQL Server Native Client 11.0};"
                      r"SERVER=phssql2178.partners.org;"
                      r"DATABASE=Epic;"
                      r"Trusted_Connection=yes;")

#Generate the cursor
c = conn.cursor()

#Execute the first four commands
#First three build temp tables
#4th query returns the table we actually want
c.execute(sqlCommands[0])
c.execute(sqlCommands[1])
c.execute(sqlCommands[2])
c.execute(sqlCommands[3])

#Add the rows from most recent query to output
output = []
for row in c:
    output.append(row)

#Save the field names to header
header = [column[0] for column in c.description]

#Close cursor and connection
c.close()
conn.close()

print_and_log('SQL done.', logfile)

"""
Save outputs and send email
"""
#Save SQL output to csv file
with open(pf.join_paths(output_dir, comments_csvfile), 'w+', newline = '') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in output:
        writer.writerow(row)
        
print_and_log('.csv file saved.', logfile)
   
#Generate dictionary of field names and their column index from header
index_dict = {}
for i, field in enumerate(header):
    index_dict[field] = i

#Transform output data from sql query into a data dict with the relevant values
#to plug into the html template
#keys in data_dict are bpa ids
data_dict = {}
for line in output:
    if line[0] in data_dict:
        data_dict[line[0]]['comments'].append([line[index_dict['SpecificOverrideCommentTXT']], line[index_dict['Cranky']]])
    else:
        data_dict[line[0]] = {'bpa_id': line[index_dict['BestPracticeAlertLocatorID']],
                 'bpa_name':line[index_dict['AlertDSC']],
                 'comments':[[line[index_dict['SpecificOverrideCommentTXT']], line[index_dict['Cranky']]]],
                 'count_alerts':line[index_dict['CountAlerts']],
                 'count_comments':line[index_dict['CountComments']],
                 'count_cranky':line[index_dict['CountCranky']],
                 #'cranky':line[index_dict['Cranky']],
                }

bpa_order = sorted([bpa for bpa in data_dict])

#Load the html template and environment
file_loader = FileSystemLoader(templates_dir)
env = Environment(loader=file_loader)
template = env.get_template("cranky_comments.txt")

#Render the html
comments_html = template.render(title = frequency.capitalize() + ' Override Comments Report', startdate = start_date, enddate = end_date, bpas = data_dict, bpa_order = bpa_order)

#Save html to file
pf.save_html_to_file(comments_html, pf.join_paths(output_dir, comments_htmlfile))

print_and_log('HTML saved.', logfile)

#Send the email with csv file as attachment
se.send_msg_with_attachment(message_text = comments_html, 
                            subject = frequency.capitalize() + ' Override Comments: ' + start_date + ' to ' + end_date, 
                            email_list_file = email_list,
                            attachment_file = pf.join_paths(output_dir, comments_csvfile), 
                            attachment_abbrev = comments_csvfile, 
                            email_server = email_server, 
                            from_address = from_address)

print_and_log('Email sent.', logfile)
print_and_log('Override comments done.', logfile)
