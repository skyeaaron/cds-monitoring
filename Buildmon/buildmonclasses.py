# -*- coding: utf-8 -*-
"""
module to support buildmon.py
creates classes for input files
"""

import processfiles as pf
import buildmonfunctions as bf

class FileInfo:
    """ 
    FileInfo class represents meta data about an input file
    for buildmon.
    """

    def __init__(self, name, file_descriptor, header, datatypes):
        """ Create a new FileInfo """
        self.name = name
        self.file_descriptor = file_descriptor
        self.datatypes = datatypes
        self.header = header
        self.id_col = None #which column contains the identifier
        self.name_col = None #which column contains the name of the identifier
        self.file1 = None
        self.file2 = None
        self.infile1only = None
        self.infile2only = None
        self.inboth = None
        self.truncated = False
        self.changes = None
        
    def generate_filenames(self, date1, date2, filename_format, directory = ''):
        """ return two strings: directory\\date1file_suffix, directory\\date2file_suffix
        eventually, will want to check if the files exist and look farther back if not """
        self.file1 = pf.join_paths(directory, (filename_format.replace('descriptor', self.file_descriptor)).replace('date', date1))
        self.file2 = pf.join_paths(directory, (filename_format.replace('descriptor', self.file_descriptor)).replace('date', date2))
        return None
    
    def find_edits(self, truncate_length = 3000):
        #find list of lines in file1 but not in file2 and vice versa
        #count lines in both files
#        try:        
        infile1only, infile2only, inboth = pf.compare_sorted_zipped_files(self.file1, 
                                                                          self.file2,
                                                                          self.datatypes,
                                                                          header = False)            
#        except FileNotFoundError:
#            print('yesy')
        truncated = False
        if truncate_length:
            if len(infile1only) > truncate_length:
                truncated = True
                infile1only = infile1only[0:truncate_length-1]
            if len(infile2only) > truncate_length:
                truncated = True
                infile2only = infile2only[0:truncate_length-1]
        self.infile1only = infile1only
        self.infile2only = infile2only
        self.inboth = inboth
        self.truncated = truncated
        return infile1only, infile2only, inboth, truncated

        
class SimpleSection(FileInfo):
    """
    SimpleSection class is a subclass of FileInfo.
    It represents a one-tiered comparison section.
    May get labels from another FileInfo object.
    Initialize like a FileInfo object.
    """
    
    def __init__(self, name, file_descriptor, header, datatypes):
        FileInfo.__init__(self, name, file_descriptor, header, datatypes)
        
    def label_edits(self, col_index, fi_object):
        """
        Apply the names from another file info object to the col_index specified
        of the infile1only and infile2only attributes.
        The id_col in fi_object must match the column specified.
        Also edit the header using the header from the fi_object.
        """
        file1_ids = bf.sorted_ids(self.infile1only, col_index)
        file2_ids = bf.sorted_ids(self.infile2only, col_index)
        file1_lookupdict = pf.list_search_zipped_file(file1_ids, fi_object.file1, fi_object.id_col, fi_object.name_col, fi_object.datatypes, header = True)
        file2_lookupdict = pf.list_search_zipped_file(file2_ids, fi_object.file2, fi_object.id_col, fi_object.name_col, fi_object.datatypes, header = True)
        bf.label_changes(self.infile1only, col_index, file1_lookupdict)
        bf.label_changes(self.infile2only, col_index, file2_lookupdict)
        #header
        self.header.insert(col_index + 1, fi_object.header[fi_object.name_col])
        return None
    
    def format_changes_as_diff(self):
        """
        Given two lists of lists, one for records in the old file only
        and one for records in the new file only,
        combine them, adding a column with - or +
        and then sort by column 1 in the new list
        (column 1 since column 0 contains the diff symbol)
        """
        self.changes = bf.changes_to_diff(self.infile1only, self.infile2only)
        return None
    
    def template_dict(self):
        """
        return a dictionary summarizing attributes needed for the html templates
        """
        output = {'in both': "{:,}".format(self.inboth),
                  'changes': self.changes,
                  'truncated': self.truncated,
                  'header': self.header,
                  'type': 'simple'}
        return output
    
    
class MappingSection(FileInfo):
    """ 
    MappingSection class is a subclass of FileInfo.
    It represents a two-tiered comparison section.
    The FileInfo is for the mapping itself.
    The section also must reference a container and content.
    """
    
    def __init__(self, name, file_descriptor, header, datatypes):
        FileInfo.__init__(self, name, file_descriptor, header, datatypes)
        self.container = None
        self.content = None
    
    def create_changes_dict(self):
        """
        create a dictionary {grouper lookup:{grouper_id:grouper_name},
                             content lookup:{content_id:content_name},
                             mapping changes:{grouperid:[[+ ,contentid], [- , contentid]]}}
        infile1only and infile2only are assumed to have the container in col 0
        and the content in col 1    
        note that some containers or contents may not have a name. if so
        give a None value instead
        """
        self.changes = {'container lookup': {},
                        'content lookup': {},
                        'mapping changes': {}}
        container_ids1 = bf.sorted_ids(self.infile1only, 0)
        container_ids2 = bf.sorted_ids(self.infile2only, 0)
        content_ids1 = bf.sorted_ids(self.infile1only, 1)
        content_ids2 = bf.sorted_ids(self.infile2only, 1)
        if self.container.name_col:
            #merge map1 and map2, keeping the values in map2 if there is a conflict
            grouper_map1 = pf.list_search_zipped_file(container_ids1, self.container.file1, self.container.id_col, self.container.name_col, self.container.datatypes, header = True)
            grouper_map2 = pf.list_search_zipped_file(container_ids2, self.container.file2, self.container.id_col, self.container.name_col, self.container.datatypes, header = True)
            self.changes['container lookup'] = {**grouper_map1, **grouper_map2}
        else:
            print('container section does not contain names')
        if self.content.name_col:
            content_map1 = pf.list_search_zipped_file(content_ids1, self.content.file1, self.content.id_col, self.content.name_col, self.content.datatypes, header = True)
            content_map2 = pf.list_search_zipped_file(content_ids2, self.content.file2, self.content.id_col, self.content.name_col, self.content.datatypes, header = True)
            #merge map1 and map2, keeping the values in map2 if there is a conflict
            self.changes['content lookup'] = {**content_map1, **content_map2}
        else:
            print('content section does not contain labels')
        #initialize mapping changes 
        self.changes['mapping changes'] = {container_id: [] for container_id in container_ids1 + container_ids2}
        for row in self.infile1only:
            self.changes['mapping changes'][row[0]].append(['- ', row[1]])
        for row in self.infile2only:
            self.changes['mapping changes'][row[0]].append(['+ ', row[1]])
        for container_id in self.changes['mapping changes']:
            self.changes['mapping changes'][container_id].sort(key=lambda x: x[1])
        return None

    def template_dict(self):
        """
        return a dictionary summarizing attributes needed for the html templates
        """
        output = {'in both': "{:,}".format(self.inboth),
                  'changes': self.changes,
                  'truncated': self.truncated,
                  'type': 'map'}
        return output