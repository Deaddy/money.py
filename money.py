#!/usr/bin/env python3

# script to store expenditures in csv with
#	date, context, amount
# and functions to analyze these.

from sys import argv, stderr

import csv
import datetime
import json
import os
import re

CONFIGFILE=os.path.expanduser("~/.moneypyrc")

# the configuration is dictionary based, saved in json format
# one can specify a dbfile in which the data will be logged and add budgets to
# different tags; currently only monthly budgets are supported

DEFAULTCONFIG={
		'dbfile' : '~/.money.csv'
		}

# some classes and datatypes or exceptions

class UnknownAction(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return "Unknown Action: %s"%(self.value)

# first some universal helper functions

def help():
	helptext = """\
Usage: add|rm|ls
Additional options for ls:
	@context1 @context2 ...
		- filters for entries that have one of the listed contexts
	since date
		- filters for entries newer than date
	combinations of these are possible.
"""

	print(helptext)

def _is_in(needle, haystack):
	if needle in haystack: return True
	else: return False

def _is_newer(lh, rh):
	if lh >= rh: return True
	else: return False

def _prettyprint(entries):
	total = 0.00
	for line in entries:
		print(line["date"], line["amount"], line["context"])
		total += float(line["amount"])
	print("Total: ", total)

def read():
	r = csv.DictReader(open(config['dbfile']), delimiter=';')
	rows = []
	for row in r:
		rows.append(row)
	return rows

def parse_arguments(args):
	"""This function parses arguments like argv and returns a dictionary
	with keys
		action
		tags
		date : the date since which the data should be displayed.
	Please note that it supposes the first entry of args to be the action, so if
	you're using argv remember to start the 

	It raises an UnknownAction Exception if it's asked for an action which can't
	be performed.
	"""



def load_config(config=CONFIGFILE):
	"""Try to open the config file - if it does not exist, assume default
	configuration, else exit with an error"""
	try:
		cfg = open(config, 'r').read()
		return sanitize_config(json.loads(cfg))
	except IOError as e:
		(errno, errstr) = e.args
		if errno == 2:
			return DEFAULTCONFIG
		else:
			print("An error occured opening the configuration file '%s':"%(config),
					file=stderr)
			print(errstr, file=stderr)
			exit(1)
	except ValueError as e:
		if e.args[0] == 'No JSON object could be decoded':
			print("An error occured reading the configuration file '%s'; please \
make sure it is correct JSON"%
				(config), file=stderr)
		else:
			print(e)
		exit(1)

def sanitize_config(config):
	"""Check if dbfile is set; else replace with dbfile of default
	config. Further default values might come.
	Also expand tilde in filepaths."""
	if not 'dbfile' in config.keys():
		config['dbfile'] = DEFAULTCONFIG['dbfile']
	for path in ['dbfile']:
		config[path]=os.path.expanduser(config[path])
	return config

		
# here starts the real programlogic

def add(config, args):
	"""requires amount, context and date are optional. If no date is present,
	assume today."""
	if args == []:
		help()
		return
	amount, context, date = 0, "", ""
	for arg in args:
		if re.match("^[0-9]*([\.,][0-9]{0,2}){0,1}$", arg) and not amount:
			amount = float(arg.replace(',', '.'))
		elif arg.startswith("@") and (len(arg) > 1):
			context = ','.join([context, arg[1:]])
		elif not date:
			try:
				date = datetime.datetime.strptime(arg, "%Y-%m-%d")
				date = date.strftime("%Y-%m-%d")
			except(ValueError):
				help()
				return

	context = context.strip(',')
	if not date:
		date = datetime.date.today().isoformat()
	if (amount != 0):
		w = csv.DictWriter(open(config['dbfile'], 'a'), delimiter=';',
			fieldnames=['date', 'amount', 'context'],
			lineterminator='\n')
		row = { 'date' : date, 'amount' : amount, 'context' : context }
		w.writerow(row)
		print("added:", ';'.join([date,str(amount),context]))

def ls(config, args):
	"""lists all entries, displays the total amount and budgets if defined."""
	result = read()
	if args == []:
		_prettyprint(result)
	else:
		for arg in args:
			if "@" == arg[0]:
				result = list(filter(lambda x: _is_in(arg[1:], x["context"]),
					result))
		if "since" in args:
			try:
				date = datetime.datetime.strptime(args[args.index("since")+1],
				"%Y-%m-%d").strftime("%Y-%m-%d")
				result = list(filter(lambda x: _is_newer(x["date"], date), result))
			except(ValueError):
				print("You must use a valid date-format after since (YYYY-MM-DD)")
				help()
				return
		_prettyprint(result)
		  
def budget(config, tag):
	"""returns the budget for the defined tag"""
	if tag in config["budget"].keys():
		print(tag)
	else:
		print(config["budget"].keys())

# 

if __name__=="__main__":
	config = load_config()
	if (len(argv) == 1) or (argv[1] in ["ls", "list"]):
		ls(config, argv[2:])
	elif argv[1] in ["add", "a"]:
		add(config, argv[2:])
	else:
		help()
