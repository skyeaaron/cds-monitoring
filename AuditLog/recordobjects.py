# -*- coding: utf-8 -*-
"""
Module with classes for the auditlog compare_base.py
"""
import parseclarity as pc


class audit_record:
    """ audit_record class represents and manipulates records for the audit log project. """

    def __init__(self, record_id, kind, classification = None):
        """ Create a new audit_record """
        self.id = record_id
        self.kind = kind
        #might want classification to be a property instead
        self.classification = classification
        self.old_data = []
        self.new_data = []
        self.edits = []
        self.old_linked_criteria = set()
        self.new_linked_criteria = set()
        self.old_rules = set()
        self.new_rules = set()
    def initialize_old_data(self, data):
        """
        Populate old_data with data.
        If the record already contains data in old_data and it is different
        from the data being saved, the record is classified as 'Duped'
        and old_data is not overwritten.
        """
        if self.old_data:
            if self.old_data == data:
                pass
            else:
                self.classification = 'Duped'
        else:
            self.old_data = data
        return None
    def initialize_new_data(self, data):
        """
        Populate new_data with data.
        If the record already contains data in new_data and it is different
        from the data being saved, the record is classified as 'Duped'
        and new_data is not overwritten.
        """
        if self.new_data:
            if self.new_data == data:
                pass
            else:
                self.classification = 'Duped'
        else:
            self.new_data = data
        return None
    def classify(self):
        """ 
        Based on old_data and new_data, classify the record.
        Does not reclassify if the record is already classified as Duped 
        """
        if self.classification == 'Duped':
            print('Classification is set to Duped and must be changed manually.')
        elif not self.old_data and not self.new_data:
            self.classification = None
            print('no data found. classification removed.')
        elif self.old_data and not self.new_data:
            self.classification = 'Deleted'
        elif not self.old_data and self.new_data:
            self.classification = 'Added'
        elif self.old_data and self.new_data:
            if self.old_data == self.new_data:
                self.classification = 'Unchanged'
            elif len(self.old_data) != len(self.new_data):
                self.classification = 'Error'
            else:
                self.classification = 'Edited'
        else:
            self.classification = None
            print('no classification found')
        return None
    def find_edits(self):
        """
        For any records that have old_data and new_data
        update self.edits if old and new data differ
        """
        if self.old_data and self.new_data and self.old_data != self.new_data:
            if len(self.old_data) != len(self.new_data):
                print("Length of old and new data is different. Cannot find edits.")
            else:
                self.edits = [i for i, x in enumerate(self.old_data) if self.old_data[i]!=self.new_data[i]]
        return None
    def find_linked_criteria(self, old_index, new_index):
        """ 
        look in old_data and new_data for linked criteria 
        at the indexes specified 
        """
        if self.old_data:
            self.old_linked_criteria = pc.parse_linked_criteria(self.old_data[old_index])
        if self.new_data:
            self.new_linked_criteria = pc.parse_linked_criteria(self.new_data[new_index])
        return None
    def find_rules(self, old_indexes, new_indexes):
        """ 
        look in old_data and new_data for rules
        at the indexes specified 
        each indexes list must contain an index for the Include Rules
        AND an index for the Exclude Rules. Union all rules found.
        """
        if self.old_data:
            self.old_rules = pc.parse_linked_criteria(self.old_data[old_indexes[0]]) | pc.parse_linked_criteria(self.old_data[old_indexes[1]])
        if self.new_data:
            self.new_rules = pc.parse_linked_criteria(self.new_data[old_indexes[0]]) | pc.parse_linked_criteria(self.new_data[old_indexes[1]])
        return None
    def find_name(self):
        if self.new_data:
            return self.new_data[0]
        elif self.old_data:
            return self.old_data[0]
        else:
            return 'Error, record name not found'




         
def initialize_records_dict(data1, data2, kind, restrict_to = None):
    """
    return dictionary of audit_record objects
    initialized with data and classifications
    """
    if restrict_to:
        #print(len(restrict_to))
        base_ids1 = {row[0] for row in data1 if row[0] in restrict_to}
        #print(len(base_ids1))
        base_ids2 = {row[0] for row in data2 if row[0] in restrict_to}
        #print(len(base_ids2))
        #print(len(restrict_to))
    else:
        base_ids1 = {row[0] for row in data1}
        base_ids2 = {row[0] for row in data2}
        
    records_dict = {record_id: audit_record(record_id, 'base') for record_id in base_ids1 | base_ids2}    
    #print(len(records_dict))
    
    for row in data1:
        if row[0] in base_ids1:
            records_dict[row[0]].initialize_old_data(row[1:])
        
    for row in data2:
        if row[0] in base_ids2:
            records_dict[row[0]].initialize_new_data(row[1:])
        
    for base in records_dict:
        records_dict[base].find_edits()
        records_dict[base].classify()
        
    return records_dict



def set_union(set_list):
    """
    for example:
       set_union([crit_records_dict[crit].new_rules for crit in crit_records_dict]) 
    """
    return set().union(*set_list)



