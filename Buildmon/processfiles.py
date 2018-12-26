# -*- coding: utf-8 -*-
"""
@author: sa325

Module with functions for processing files
Used in buildmon.py, compare_base.py, overridecomments.py,
audit_metadata.py
"""

import os
import sys
import shutil
import gzip
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

def preview_file(filename1, lines = 4, read_mode = 'rt', read_encoding = 'utf-8'):
    """
    prints first 4 lines of file, parsed using csv reader
    """
    with open(filename1, mode = read_mode, encoding = read_encoding) as f1:
        for i in range(lines):
        #f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
            print(next(f1))
    return None
 
def preview_zipped_file(filename1, read_mode = 'rt', read_encoding = 'utf-8'):
    """
    prints first 4 lines of gz zipped file, parsed using csv reader
    """
    with gzip.open(filename1, mode = read_mode, encoding=read_encoding) as fn1:
        f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
        print(next(f1))
        print(next(f1))
        print(next(f1))
        print(next(f1))
    return None

def gzip_to_list(filename1, delimit = '\t', read_mode = 'rt', read_encoding = 'utf-8'):
    """
    import gz zipped file as list of lists of strings using csv reader
    """
    output = []
    with gzip.open(filename1, mode = read_mode, encoding = read_encoding) as fn1:
        f1 = csv.reader(fn1, delimiter = delimit, quoting=csv.QUOTE_NONE)
        for line in f1:
            output.append(line)
    return output

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


def write_list_to_zipped_file(filename, output):
    """
    write list to gz file
    """
    with gzip.open(filename, 'wb') as f:
        for line in output:
            f.write((line + '\n').encode('utf-8'))

def search_zipped_file(filename1, search_text, col):
    """
    given filename, text to search as string, and column to search
    prints line where text is found if found
    """
    with gzip.open(filename1, mode = 'rt', encoding='utf-8') as fn1:
        f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
        for line in f1:
            if line == []:
                pass
            elif line[col] == search_text:
                print(line)
                return line
    return None

def lower_str(x):
    return str(x).lower()

def format_null(datatype):
    """
    return '' if str or 0 if int
    """
    if datatype == int:
        return 0
    elif datatype == lower_str:
        return ''
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


def list_search_zipped_file(search_list, filename, search_col, return_col, datatypes, header = False):
    """
    given filename, search_list is a sorted list of terms to find, 
    column to search, and column to be returned
    returns a dictionary mapping search_list to text if found
    this will fail if file or list is not sorted the same way
    date1 = '20180426'
    date2 = '20180427'
    findterms = [904104, 907314]
    filename = '\\\\rfawin\\bwh-wrightdata\\buildmon\\' + date2 + 'medt.txt.gz'
    list_search_zipped_file(findterms, filename, 0, slice(1,3), [int, str])
    """
    #initialize dict so all search items say they were not found
    outputdict = dict.fromkeys(search_list, 'buildmon error: code was not found')
    if not outputdict:
        #if there are no search terms, we don't need to open the file
        return outputdict
    else:
        with gzip.open(filename, mode = 'rt', encoding='utf-8') as fn1:
            f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
            if header:
                next(f1)
            line = format_readline(next(f1), datatypes)
            i = 0
            #loop through until there are no more lines or no more search items
            while line and i < len(search_list):
                search_item = search_list[i]
                if line[search_col] < search_item:
                    try:
                        line = format_readline(next(f1), datatypes)
                    except StopIteration:
                        line= None
                elif line[search_col] > search_item:
                    i += 1
                    #print('line ', line)
                    #print('search item', search_item)
                elif line[search_col] == search_item:
                    outputdict[search_item] = line[return_col]
                    #print('line ', line)
                    #print('search item', search_item)
                    try:
                        line = format_readline(next(f1), datatypes)
                    except StopIteration:
                        line= None
                    i += 1
                else:
                    print('error')
                    line = None
        return outputdict

def list_search_zipped_file2(search_list, filename, search_col, return_cols, datatypes):
    """
    just like list_search_zipped_file but returns a list of columns
    given filename, search_list is a sorted list of terms to find, 
    column to search, and list of columns to be returned
    returns a dictionary mapping search_list to text if found
    this will fail if file or list is not sorted the same way
    date1 = '20180426'
    date2 = '20180427'
    findterms = [904104, 907314]
    filename = '\\\\rfawin\\bwh-wrightdata\\buildmon\\' + date2 + 'medt.txt.gz'
    list_search_zipped_file(findterms, filename, 0, slice(1,3), [int, str])
    """
    #initialize dict so all search items say they were not found
    outputdict = dict.fromkeys(search_list, 'buildmon error: code was not found')
    if not outputdict:
        #if there are no search terms, we don't need to open the file
        return outputdict
    else:
        with gzip.open(filename, mode = 'rt', encoding='utf-8') as fn1:
            f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
            line = format_readline(next(f1), datatypes)
            i = 0
            #loop through until there are no more lines or no more search items
            while line and i < len(search_list):
                search_item = search_list[i]
                if line[search_col] < search_item:
                    try:
                        line = format_readline(next(f1), datatypes)
                    except StopIteration:
                        line= None
                elif line[search_col] > search_item:
                    i += 1
                    #print('line ', line)
                    #print('search item', search_item)
                elif line[search_col] == search_item:
                    outputdict[search_item] = [line[i] for i in return_cols]
                    #print('line ', line)
                    #print('search item', search_item)
                    try:
                        line = format_readline(next(f1), datatypes)
                    except StopIteration:
                        line= None
                    i += 1
                else:
                    print('error')
                    line = None
        return outputdict

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

def convert_to_gzip(input_filename, output_filename):
    """
    given an input text file
    gzip it
    """
    with open(input_filename, 'rt') as f_in, gzip.open(output_filename, 'wt', encoding = 'utf-8') as f_out:
        f_out.writelines(f_in)
    return None

def compare_sorted_zipped_files(filename1, filename2, datatypes, header = False):
    """
    File1 is checked first and raises exception if it can't be found
    File2 is checked second. So if File2 raises the exception, then File1 was fine.
    Given two zipped files,
    return: list of lines in file 1 not in file 2,
    list of lines in file 2 not in file 1,
    count of the lines that are in both files.
    The files must be sorted in advance.
    The point is to not have to load either file in entirety.
    We unzip and read on the fly and compare lines on the fly.
    The expected behavior is that any NULL values in the first column
    will only appear at the start of the file. This crashes otherwise.
    Thus the comparisons will be incorrect if the files are not pre-sorted.
    format=[int,str]
    """
    infile1only = []
    infile2only = []
    inboth = 0  
    try:
        with gzip.open(filename1, mode = 'rt', encoding='utf-8-sig') as fn1:
            f1 = csv.reader(fn1, delimiter = '\t', quoting=csv.QUOTE_NONE)
            try:
                with gzip.open(filename2, mode = 'rt', encoding='utf-8-sig') as fn2:
                    f2 = csv.reader(fn2, delimiter = '\t', quoting=csv.QUOTE_NONE)
                    if header:
                        next(f1)
                        next(f2)
                    try:
                        #print(next(f1))
                        line1 = format_readline(next(f1), datatypes)
                    #this is bad. we should raise the error unless it's because
                    #the line is empty or there are no lines. what errors indicate that?
                    except StopIteration:
                        line1 = None
                    try:
                        line2 = format_readline(next(f2), datatypes)
                    except StopIteration:
                        line2 = None      
                    while line1 or line2:
                        #if you run out of lines from first file, append line from 2nd file to result
                        if line1 is None:
                            infile2only.append(line2)
                            try:
                                line2 = format_readline(next(f2), datatypes)
                            except StopIteration:
                                line2 = None
                        #if you run out of lines from second file, append line from 1st file to result
                        elif line2 is None:
                            infile1only.append(line1)
                            try:
                                line1 = format_readline(next(f1), datatypes)
                            except StopIteration:
                                line1 = None
                        #if line1 < line2, append line1 and iterate it but do not advance line2
                        elif line1 < line2:
                            print(line1, line2)
                            infile1only.append(line1)
                            try:
                                line1 = format_readline(next(f1), datatypes)
                            except StopIteration:
                                line1 = None
                        #if line1 > line2, append line2 and iterate it but do not advance line1
                        elif line1 > line2:
                            print(line1, line2)
                            infile2only.append(line2)
                            try:
                                line2 = format_readline(next(f2), datatypes)
                            except StopIteration:
                                line2 = None
                        #if line1 == line2, advance both lines
                        elif line1 == line2:
                            inboth += 1
                            try:
                                line1 = format_readline(next(f1), datatypes)
                            except StopIteration:
                                line1 = None
                            try:
                                line2 = format_readline(next(f2), datatypes)
                            except StopIteration:
                                line2 = None
                        #any other situation is unexpected behavior
                        else:
                            print('error')
                            print(line1)
                            print(line2)
                            inboth = 'error'
                            line1 = None
                            line2 = None
                return(infile1only, infile2only, inboth)
            except FileNotFoundError:
                raise
    except FileNotFoundError:
        raise
        
def remove_header_gzip(input_filename, output_filename):
    """
    copy gzip file to new gzip file
    leave out first line
    """
    with gzip.open(input_filename, 'rt', encoding = 'utf-8') as f_in, gzip.open(output_filename, 'wt', encoding = 'utf-8') as f_out:
        next(f_in)
        f_out.writelines(f_in)
    return None
        