#!/usr/bin/python3.1

# script to store expenditures in csv with
#	date, context, amount
# and functions to analyze these.

from sys import argv

import re
import csv
import datetime

DBFILE="./db.csv"

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
	r = csv.DictReader(open(DBFILE), delimiter=';')
	rows = []
	for row in r:
		rows.append(row)
	return rows

# here starts the real programlogic

def add(args):
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
		w = csv.DictWriter(open(DBFILE, 'a'), delimiter=';',
			fieldnames=['date', 'amount', 'context'],
			lineterminator='\n')
		row = { 'date' : date, 'amount' : amount, 'context' : context }
		w.writerow(row)
		print("added:", ';'.join([date,str(amount),context]))

def ls(args):
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
		  
if __name__=="__main__":
	if (len(argv) == 1) or (argv[1] in ["ls", "list"]):
		ls(argv[2:])
	elif argv[1] in ["add", "a"]:
		add(argv[2:])
	else:
		help()
