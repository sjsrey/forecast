#!/usr/bin/python

""" TODO.TXT Forecast
USAGE:  
    forecast.py [todo.txt] 
    
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


import sys
import datetime


__version__ = "0.3"
__date__ = "2012-05-29"
__updated__ = "2014-03-23"
__author__ = "Serge Rey  (sjsrey@gmail.com)"
__copyright__ = "Copyright 2011-2014,  Sergio Rey"
__license__ = "GPL"
__history__ = """
0.1 - Dev.
"""

NOW = datetime.date.today()
DOW = "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"

# Bash coloring from:
# https://github.com/emilerl/emilerl/blob/master/pybash/bash/__init__.py

RESET = '\033[0m'
CCODES = {
    'black'           :'\033[0;30m',
    'blue'            :'\033[0;34m',
    'green'           :'\033[0;32m',
    'cyan'            :'\033[0;36m',
    'red'             :'\033[0;31m',
    'purple'          :'\033[0;35m',
    'brown'           :'\033[0;33m',
    'light_gray'      :'\033[0;37m',
    'dark_gray'       :'\033[0;30m',
    'light_blue'      :'\033[0;34m',
    'light_green'     :'\033[0;32m',
    'light_cyan'      :'\033[0;36m',
    'light_red'       :'\033[0;31m',
    'light_purple'    :'\033[0;35m',
    'yellow'          :'\033[0;33m',
    'white'           :'\033[0;37m',
}

class Colors(object):
    """A helper class to colorize strings"""
    def __init__(self, state = False):
        self.disabled = state
    
    def disable(self):
        self.disabled = True
        
    def enable(self):
        self.disabled = False
            
    def __getattr__(self,key):
        if key not in CCODES.keys():
            raise AttributeError, "Colors object has no attribute '%s'" % key
        else:
            if self.disabled:
                return lambda x: x
            else:
                return lambda x: RESET + CCODES[key] + x + RESET
    
    def __dir__(self):
        return self.__class__.__dict__.keys() + CCODES.keys()


def ds2dt(dateString):
    ds = dateString.split(":")[1]
    y,m,d = map(int, ds.split("-"))
    return datetime.date(y,m,d)


DONE = "done.txt"


class Item:
    """
    Individual task item
    """
    def __init__(self, line, id):
        words = line.split()
        taskWords = words[:]
        self.id = id
        self.line = line
        self.line = self.line.strip()
        self.line = str(id) +  " " + self.line
        self.available = False
        self.overdue = False
        self.due = False
        self.color = 'blue'
        for word in words:
            if word[0] == "+":
                self.project = word.split("+")[1]
                line = line
                taskWords.remove(word)
            if word[0:2] == "s:":
                self.startDate = ds2dt(word)
                if self.startDate <= NOW:
                    self.available = True
            if word[0:2] == "t:":
                self.dueDate = ds2dt(word)
                if self.dueDate <= NOW:
                    self.overdue = True
                else:
                    self.due = True
            if word[0] == "(":
                self.priority = word.split("(")[1].split(")")[0]
                taskWords.remove(word)
        self.task = " ".join(taskWords)

    def summary(self):
        print "\nITEM Summary\n"
        print "ID: %02d"% self.id
        print "Line: ", self.line
        print "Task: ", self.task
        attributes = "project", "priority", "startDate", "dueDate", \
                'overdue', 'available'
        for attribute in attributes:
            att = getattr(self, attribute, 'None')
            print "%s: %s"%(attribute, att)

def forecastUpcoming(allItems):
    weekAhead = [ NOW + datetime.timedelta(days=i) for i in range(7)]
    slots = {}
    for itemKey in allItems:
        item = allItems[itemKey]
        dueDate = getattr(item, 'dueDate', None)
        startDate = getattr(item, 'startDate', None)
        if startDate and dueDate:
            for day in weekAhead:
                if startDate <= day and day <= dueDate:
                    slots.setdefault(day, []).append(item)
        elif dueDate:
            for day in weekAhead:
                if dueDate == day:
                    slots.setdefault(day, []).append(item)
        elif startDate:
            for day in weekAhead:
                if startDate <= day:
                    slots.setdefault(day, []).append(item)
    keys = slots.keys()
    keys.sort()
    c = Colors(state=False)
    print "\n"
    print c.yellow('Upcoming Items Report').strip()
    for key in keys:
        dow = DOW[key.isoweekday()-1]
        dfmt = key.strftime("%Y-%m-%d")
        nItems = len(slots[key])
        print c.green("%s %s has %d item(s) available or due"%(dow, dfmt, nItems))
        if nItems > 0:
            items = slots[key]
            for item in items:
                if item.due:
                    print c.purple(item.line).strip()
                elif item.overdue:
                    print c.red(item.line).strip()
                else:
                    print c.blue(item.line).strip()

        print "\n"


def forecastDue(allItems):
    weekAhead = [ NOW + datetime.timedelta(days=i) for i in range(7)]
    slots = {}
    for itemKey in allItems:
        item = allItems[itemKey]
        dueDate = getattr(item, 'dueDate', None)
        if dueDate:
            slots.setdefault(dueDate, []).append(item)
    keys = slots.keys()
    keys.sort()
    c = Colors()
    print "\n"
    print c.yellow('Due Items Report')
    for key in keys:
        dow = DOW[key.isoweekday()-1]
        dfmt = key.strftime("%Y-%m-%d")
        nItems = len(slots[key])
        print c.green("%s %s has %d deadline(s):"%(dow, dfmt, nItems))
        if nItems > 0:
            items = slots[key]
            for item in items:
                if item.due:
                    print c.purple(item.line)
                elif item.overdue:
                    print c.red(item.line)
                else:
                    print item.line
        print "\n"

def usage():
    print "USAGE:  %s [todo.txt]"% (sys.argv[0], )

    
def separator(c):
    sep = ""
    sep = c * 42
    print sep


def main(argv):
    # make sure you have all your args
    if len(argv) < 1:
        usage()
        sys.exit(2)

    # process todo.txt
    try:
        f = open(argv[0], "r")
        lines = f.readlines()
        f.close()
        allItems = {}
        id = 1
        for line in lines:
            item = Item(line, id)
            id += 1
            allItems[item.id] = item
    except IOError:
        print "ERROR:  The file named %s could not be read."% (argv[0], )
        usage()
        sys.exit(2)

    forecastUpcoming(allItems)
    separator("=")
    forecastDue(allItems)
    #separator("=")
    #forecastAvailable(allItems)




if __name__ == "__main__":
    main(sys.argv[1:])
