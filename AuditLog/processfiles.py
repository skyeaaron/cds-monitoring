# -*- coding: utf-8 -*-
"""
Module with functions for processing files
Used in compare_base.py
"""

import os
import sys
import shutil
import csv


def create_log(logfilename):
    """
    overwrite or create logfile
    """
    with open(logfilename, 'w+') as f:
        f.write('log file created' + os.linesep)

def log(message, logfilename):
    """
    write message to log file
    """
    with open(logfilename, 'a') as f:
        f.write(message + os.linesep)
    return None

def print_and_log(message, logfilename):
    """
    print message, and
    write message to log file
    """
    print(message)
    log(message, logfilename)
    return None

def get_path_delimiter():
    return os.sep

def get_env_var(env_var):
    return os.environ.get(env_var)

def join_paths(path, *paths):
    return os.path.join(path, *paths)

def string_to_os_path(filepath):
    return os.path.normpath(filepath)

def replace_None(input_text):
    """
    replace None with ""
    """
    return "" if input_text is None else input_text

def preview_file(filename1, read_mode = 'rt', read_encoding = 'utf-8'):
    """
    prints first 4 lines of file, parsed using csv reader
    """
    with open(filename1, mode = read_mode, encoding = read_encoding) as f1:
        #f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
        print(next(f1))
        print(next(f1))
        print(next(f1))
        print(next(f1))
    return None

def csv_to_list(filename, header = True, delimit_char = ",", encod = 'utf-8', quote = csv.QUOTE_MINIMAL):
    """
    read csv file
    if header is True then returns first row as header
    delimit_char defaults to ","
    """
    with open(filename, 'r', encoding = encod) as f:
        csv_f = csv.reader(f, delimiter = delimit_char, quoting = quote)
        if header:
            output_header = next(csv_f)
            output_data = [row for row in csv_f]
            return output_data, output_header
        else:
            output_header = None
            output_data= [row for row in csv_f]
            return output_data

def write_list_to_csv(filename, output, delimit_char = ','):
    """
    Save output list to csv
    """
    with open(filename, 'w+') as f:
        csv_f = csv.writer(f, delimiter = delimit_char, lineterminator='\n')
        for row in output:
            csv_f.writerow(row)
    return None

def format_null(datatype):
    """
    return '' if str or 0 if int
    """
    if datatype == int:
        return 0
    elif datatype == str:
        return ''

def format_readline(line, datatypes):
    """
    this takes datatypes = None
    or datatypes = [int, int, str] (for example)
    list of conversion arguments
    this has no except clauses and will BREAK if anything is wrong
    if there are any '' entries in the line,
    return '' if str or 0 if int
    """
    if datatypes:
        if len(datatypes) != len(line):
            if len(datatypes) == 1 and line == []:
                #in the case where it is a single-column file
                #and there is an empty line, return [0] or ['NULL']
                output_line = [format_null(datatypes[0])]
            else:
                sys.exit('line in file has different number of columns than specified datatypes' + str(line) + str(datatypes))
        else:
            output_line = [datatypes[i](line[i]) if line[i] is not '' else format_null(datatypes[i]) for i in range(len(datatypes))]
    else:
        output_line = line
    return output_line

def remove_dir(filepath):
    """
    remove directory at the specified filepath
    """
    shutil.rmtree(filepath, ignore_errors = True)
    return 'removed directory ' + filepath

def delete_html_files(targetdir):
    """
    delete all html files within the specified directory
    """    
    filelist = os.listdir(targetdir)
    for item in filelist:
        if item.endswith(".html"):
            os.remove(os.path.join(targetdir, item))
    return 'Deleted html files from ' + targetdir

def create_dir(filepath):
    """
    create directory at specified filepath if it does not already exist
    """
    os.makedirs(filepath, exist_ok = True)
    return None

def save_html_to_file(outputhtml, filename):
    with open(filename, 'w') as f:
        f.write(outputhtml)
    return None

