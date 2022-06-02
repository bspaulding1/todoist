#!/usr/bin/env python

import pandas as pd
import sys
import os

# TODO: is there a way to make adjustments to repeats in advance of importing? (e.g. every or every!)

if len(sys.argv) < 2:
    print('')
    print('    Usage: python toodledo_to_todoist.py <xml_filename>')
    print('')
    exit(1)

filename = sys.argv[1]
base_path = '/Users/bryanspa/projects/todoist'
output_path = os.path.join(base_path, 'output')
ref_path = os.path.join(base_path, 'reference')

priority_map = {
	'': 4,
	3.0: 1,
	2.0: 2,
	1.0 : 3
}

repeat_map = {
	'': '', 
	'Yearly': 'every! year', 
	'Every Fri': 'every! friday', 
	'Every Sat': 'every! saturday', 
	'Quarterly': 'every! 3 months', 
	'Every 3 weeks': 'every! 3 weeks',
	'Every 8 weeks': 'every! 8 weeks', 
	'Semiannually': 'every! 6 months', 
	'Monthly': 'every! month', 
	'Every Thu': 'every! thursday', 
	'Biweekly': 'every! 2 weeks',
	'Every 4 weeks': 'every! 4 weeks', 
	'Bimonthly': 'every! 2 months', 
	'The 1st Sat of each month': 'every! 1st friday', 
	'Every 2 days': 'every! 2 days',
	'Every Wed': 'every! wednesday', 
	'Weekly': 'every! week', 
	'Every 30 days': 'every! 30 days', 
	'Daily': 'every! day', 
	'Every 3 days': 'every! 3 days',
	'Every 2 years': 'every! 2 years'
}


def output_files(df):
	folders = df['FOLDER'].unique()
	for folder in folders:
		csv_name = folder.replace(' ', '+').replace('/', '_') + '.csv'
		csv_path = os.path.join(output_path, csv_name)
		df_new = df.copy(deep=True)
		df_new = df_new.loc[df['FOLDER'] == folder]
		df_new.drop(['REPEAT', 'STAR', 'FOLDER'], axis=1, inplace=True)
		df_new.to_csv(csv_path, index=False)


def main():
	df = pd.read_csv(filename)

	# Drop unneeded columns
	df.drop(['LOCATION', 'STARTDATE', 'STARTTIME', 'DUETIME', 'LENGTH', 'TIMER', 'TAG', 'STATUS', 'CONTEXT', 'GOAL'], axis=1, inplace=True)

	# Rename columns
	df.rename(columns={'TASK': 'CONTENT', 'NOTE': 'DESCRIPTION', 'DUEDATE': 'DATE'}, inplace=True)

	# Add missing columns
	df['TYPE'] = 'task'
	df['INDENT'] = 1
	df['AUTHOR'] = ''
	df['RESPONSIBLE'] = ''
	df['DATE_LANG'] = 'en'
	df['TIMEZONE'] = 'US/Pacific'

	# Reorder columns
	df = df[['TYPE', 'CONTENT', 'DESCRIPTION', 'PRIORITY', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE', 'DATE_LANG', 'TIMEZONE', 'REPEAT', 'STAR', 'FOLDER']]

	# Map priorities
	df = df.fillna('')
	df['PRIORITY'] = df['PRIORITY'].map(priority_map)
	df['PRIORITY'] = df['PRIORITY'].astype(int)

	# Convert Dates + Recurring
	df['REPEAT'] = df['REPEAT'].map(repeat_map)
	df['DATE'] = df['DATE'] + ' ' + df['REPEAT']

	# Add star label
	df.loc[df['STAR'] == 'Yes', 'CONTENT'] = df['CONTENT'] + ' @star'

	# Iterate over folders, generating distinct output files
	output_files(df)

	# Save reference
	orig_path = os.path.join(ref_path, 'todoist_import_full.csv')
	df.to_csv(orig_path, index=False)
	df.drop(['DESCRIPTION', 'TYPE', 'INDENT', 'AUTHOR', 'RESPONSIBLE', 'DATE_LANG', 'TIMEZONE'], axis=1, inplace=True)
	df = df.sort_values(by=['FOLDER', 'CONTENT'], ascending=[True, True])
	orig_path = os.path.join(ref_path, 'todoist_import_trunc.csv')
	df.to_csv(orig_path, index=False)


if __name__ == '__main__':
	main()