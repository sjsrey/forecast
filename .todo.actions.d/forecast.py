#!/usr/bin/python

""" TODO.TXT Forecast
USAGE:  
    forecast.py [todo.txt] [done.txt]
    
USAGE NOTES:
    Expects two text files as parameters, each of which formatted as follows:
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
    
    The done.txt file is a list of completed todo's from todo.txt.
    
    See more on todo.txt here:
    http://todotxt.com
    
    
OUTPUT:

CHANGELOG:

    Based on birdseye.py by Gina Trapani
"""


import sys
import datetime


__version__ = "0.1"
__date__ = "2011-06-12"
__updated__ = "2011-06-12"
__author__ = "Serge Rey  (sjsrey@gmail.com)"
__copyright__ = "Copyright 2011, Sergio Rey"
__license__ = "GPL"
__history__ = """
0.1 - Dev.
"""

NOW = datetime.datetime.utcnow()
DOW = "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"

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
        for word in words:
            if word[0] == "+":
                self.project = word.split("+")[1]
                line = line
                taskWords.remove(word)
            if word[0:2] == "s:":
                self.startDate = word.split(":")[1]
                taskWords.remove(word)
                dateStr = word.split(":")[1]
                self.startTime = datetime.datetime.strptime(dateStr, "%Y-%m-%d")
                if self.startTime <= NOW:
                    self.available = True
            if word[0:2] == "t:":
                self.dueDate = word.split(":")[1]
                taskWords.remove(word)
                dateStr = word.split(":")[1]
                self.dueTime = datetime.datetime.strptime(dateStr, "%Y-%m-%d")
                if self.dueTime <= NOW:
                    self.overdue = True
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

def forecastDue(allItems):
    weekAhead = [ NOW + datetime.timedelta(days=i) for i in range(7)]
    slots = {}
    for itemKey in allItems:
        item = allItems[itemKey]
        dueTime = getattr(item, 'dueTime', None)
        if dueTime:
            for day in weekAhead:
                if dueTime <= day:
                    slots.setdefault(day, []).append(item)
    keys = slots.keys()
    keys.sort()
    print 'Due Items Report'
    for key in keys:
        dow = DOW[key.isoweekday()-1]
        dfmt = key.strftime("%Y-%m-%d")
        nItems = len(slots[key])
        print "%s %s has %d item(s) due"%(dow, dfmt, nItems)
        if nItems > 0:
            items = slots[key]
            for item in items:
                print "\t",item.line

def forecastAvailable(allItems):
    weekAhead = [ NOW + datetime.timedelta(days=i) for i in range(7)]
    slots = {}
    future = 0 

    for itemKey in allItems:
        item = allItems[itemKey]
        startTime = getattr(item, 'startTime', None)
        if startTime:
            for day in weekAhead:
                if startTime <= day:
                    slots.setdefault(day, []).append(item)
            if startTime > day:
                future += 1
    keys = slots.keys()
    keys.sort()
    print 'Available Items Report'
    for key in keys:
        dow = DOW[key.isoweekday()-1]
        dfmt = key.strftime("%Y-%m-%d")
        nItems = len(slots[key])
        print "%s %s has %d item(s) available"%(dow, dfmt, nItems)
        if nItems > 0:
            items = slots[key]
            for item in items:
                print "\t",item.line
    print "Future items: %d"%future


def usage():
    print "USAGE:  %s [todo.txt] [done.txt]"% (sys.argv[0], )

    
def separator(c):
    sep = ""
    sep = c * 42
    print sep


def main(argv):
    # make sure you have all your args
    if len(argv) < 2:
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
    except IOError:
        print "ERROR:  The file named %s could not be read."% (argv[1], )
        usage()
        sys.exit(2)

    forecastDue(allItems)
    separator("=")
    forecastAvailable(allItems)




if __name__ == "__main__":
    main(sys.argv[1:])
