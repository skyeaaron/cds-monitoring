# CDS Monitoring Tools

Sends a suite of daily emails reporting on relevant changes that might effect clinical decision support (CDS) rules.

Find and report changes to all live Best Practice Alerts (BPAs) in Epic every morning.
Find and report changes to codes and groupers from Clarity every morning.
Extract and report daily and monthly lookbacks of override comments provided on all BPAs every morning.

This repository contains the python scripts, sql queries, and html templates used to monitor CDS and report relevant changes.

# Motivation
Many healthcare institutions have errors in their clinical decision support (CDS), but do not have tools to find these errors. 

In particular, we have found there to be a lack of tools for identifying unexpected changes to CDS, for verifying that intentional changes have been made correctly, and for finding downstream and upstream effects of changes (for example when rules reference each other or available medications change).


# Features
1. BPA Audit Logs: Takes a diff of two audit logs. 
  1. Saves a summary of the total diff in an html file.
  2. Emails the master diff to CDS knowledge management personnel.
  3. Saves a diff for each CDS rule that had changes that day in an html file.
  4. Saves a snapshot of all current logic for base rules and criteria rules.
2. EDW Code Changes: Takes a diff of codes and groupers from the EDW.
  1. Sends an email summarizing changes to concepts such as Medications, Departments, Diagnoses, and Labs.
  2. Sends an email summarizing changes to groupers and grouper mappings relevant to the concepts listed above.
  3. Sends an email summarizing changes to concepts used in patient charts.
3. Override Comments Report: Summarizes number of alerts and comments for all BPAs receiving override comments.
  1. Send an email daily with comments written in the last day. Highlights "cranky comments" in yellow.
  2. Send an email once a month with the previous month's comments.
