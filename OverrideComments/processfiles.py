# -*- coding: utf-8 -*-
"""
Module with functions for processing files
Used in overridecomments.py
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

def import_zipped_file(filename1, delimit = '\t'):
    """
    import gz zipped file as list of lists of strings using csv reader
    """
    output = []
    with gzip.open(filename1, mode = 'rt', encoding='utf-8') as fn1:
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
                break
    return line


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

def write_tree_to_file(element_tree, filename):
    element_tree.write(filename)
    return None