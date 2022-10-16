money.py - simple expense tracking in python
:Author
   Deaddy
:Licence
   Public domain
   
Setup
_____
   mv db.csv.example db.csv

Usage
_____
   money.py add|ls

Examples
________
-  `money.py add @food 20.5` - adds 20.50 with current date and food tag
-  `money.py add @food @pizza 13.37 2011-04-23` - adds 13.37 with food and pizza
   tags for day 2011-04-23 (date must be YYYY-MM-DD)
-  `money.py add` requires at least an amount
-  `money.py` - without arguments, just list all entries
-  `money.py ls` - list all entries, can be filtered with following options:
-  `money.py ls @tag1 @tag2 ...` - list all entries matching all tags
-  `money.py ls since YYYY-MM-DD` - list all entries since date

