#!/usr/bin/python

""" TODO.TXT postpone
USAGE:  
    postpone.py [todo.txt] 
    
USAGE NOTES:
    Expects one text files as parameter,  formatted as follows:
    - One todo per line, ie, "call Mom"
    - with an optional project association indicated as such: "+projectname"
    - with the context in which the tasks should be completed, indicated as such: "@context"
    - with the task priority optionally listed at the front of the line, in parens, ie, "(A)"
    - with start date optionally listed as "s:2011-06-10"
    - with due date optionally listed as "t:2011-07-10"
    
    For example, 4 lines of todo.txt might look like this:

    +garagesale @phone schedule Goodwill pickup s:2011-06-10 t:2011-07-10
    (A) @phone Tell Mom I love her t:2011-06-12
    +writing draft Great American Novel
    (B) smell the roses
    
    See more on todo.txt here:
    http://todotxt.com
    
    
OUTPUT:
    Two reports
     
      - Upcoming Items Report
        - list by the next seven days of 
            - items with start dates on or before date
            - items with due dates on date
      - Due Items Report
        - sorted list of days with due items
    

CHANGELOG:

    Based on birdseye.py by Gina Trapani
"""


import sys, getopt
import datetime
import re
__version__ = "0.3"
__date__ = "2012-05-29"
__updated__ = "2014-05-31"
__author__ = "Serge Rey  (sjsrey@gmail.com)"
__copyright__ = "Copyright 2011-2014,  Sergio Rey"
__license__ = "GPL"
__history__ = """
0.1 - Dev.
"""

NOW = datetime.date.today()
DOW = "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"

freqs = {"W":7, "M": 31, "D": 1, "Y": 365}
dow = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3,
       "FRI": 4, "SAT": 5, "SUN": 6}



# parse todo.txt

# change hardcode later
#f = "/home/serge/Dropbox/t/todo/todo.txt"

#with open(f, 'r') as input_file:
#    input_lines = input_file.readlines()

def ds2dt(dateString):
    lead, ds = dateString.split(":")
    # check if in iso format already
    dc = ds.count("-")
    if dc == 2:
        y,m,d = map(int, ds.split("-"))
        return datetime.date(y,m,d)
    else:
        # have to translate shortcuts
        today = datetime.date.today()
        try:
            # numeric argument
            num = re.findall(r'\d+',ds)[0]
            freq = ds.replace(num,'').upper()
            num = int(num)
            future = today + datetime.timedelta(days=num * freqs[freq])
            return future
        except:
            try:
                weekday = today.weekday()
                dsupper = ds.upper()
                if dsupper == 'TOD':
                    fwkd = weekday
                else:
                    fwkd = dow[ds.upper()]
                if weekday > fwkd:
                    future = today + datetime.timedelta(days = 7 + fwkd - weekday)
                else:
                    future = today + datetime.timedelta(days = fwkd - weekday)
                return future
            except:
                print 'bad shortcut: ', dateString


def bump_date(dateString, bumpnl="1d"):
    
    dt = ds2dt(dateString)
    bumpnl = bumpnl.upper()
    lead = dateString.split(":")[0]

    if bumpnl == "TOD":
        print 'TODAY'
        new_string = lead+":"+NOW.strftime("%Y-%m-%d")
        print new_string

    elif bumpnl == "TOM":
        print "TOMORROW"
        future = NOW + datetime.timedelta(days=1)
        new_string = lead+":"+future.strftime("%Y-%m-%d")
        print new_string
    elif bumpnl.count("-") == 2:
        new_string = lead+":"+bumpnl
        print new_string
    else:
        frequency = freqs[bumpnl[-1].upper()]
        increment = int(bumpnl[:-1])
        future = NOW + datetime.timedelta(increment * frequency)
        new_string = lead+":"+future.strftime("%Y-%m-%d")
        print new_string

        

        print frequency, increment






# build database
class Item(object):
    """ """
    def __init__(self, line, number=None):
        self.project = 'singleton'
        self.start_date = None
        self.due_date = None
        self.task = None
        self.context = None
        self.created_date = None
        self.line_number = number
        self.due = False
        self.overdue = False
        self.available = False
        words = line.split()

        task_words = []
        for word in words:
            if word[0] == "+":
                self.project = word
            elif word[0] == "s" and word[1] == ":":
                self.start_date = word
                start_date = ds2dt(word)
                if start_date <= NOW:
                    self.available = True
            elif word[0] == "t" and word[1] == ":":
                self.due_date = word
                due_date = ds2dt(word)
                if due_date < NOW:
                    self.overdue = True
                if due_date == NOW:
                    self.due = True
            elif word[0] == "@":
                self.context = word[1:]
            else:
                task_words.append(word)
        self.task = " ".join(task_words)


    def __str__(self):
        return '%s %d %s' % (self.project, self.line_number, self.task)


def build(file_name):
    print file_name
    with open(file_name, 'r') as input_file:
        input_lines = input_file.readlines()

    print input_lines
    items = {}
    for line_id, line in enumerate(input_lines):
        item = Item(line, number=line_id)
        items[line_id] = item

    #return items
    return DB(items)


class DB(object):
    """ """
    def __init__(self, items):
        projects = {}
        due_dates = {}
        start_dates = {}
        contexts = {}
        overdue = {}
        available = {}
        due = {}
        for item in items:
            it = items[item]
            projects.setdefault(it.project, []).append(it.line_number)
            if it.overdue:
                overdue.setdefault(it.due_date, []).append(it.line_number)

        self.projects = projects
        self.overdue = overdue



# handle cl options

def main(argv):
    # make sure you have all your args
    if len(argv) < 2:
        #usage()
        print 'update usage()'
        sys.exit(2)

    # process todo.txt
    try:
        print argv
        items = build(argv[0])
        args = argv[1:]
        print items.projects
        print items.overdue




        
    except IOError:
        print "ERROR:  The file named %s could not be read."% (argv[0], )
        usage()
        sys.exit(2)

    #tmp = argv[0]
    #tmp = open(tmp, 'w')
    #new_lines = []

    #print 'done'
    return items


# find target actions in database

# apply postponements

# write out new file

if __name__ == '__main__':
    print sys.argv
    main(sys.argv[1:])


