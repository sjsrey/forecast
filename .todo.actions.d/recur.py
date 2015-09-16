#!/usr/bin/python

""" TODO.TXT Forecast
USAGE:
    recur.py

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
import re


__version__ = "0.3"
__date__ = "2012-05-29"
__updated__ = "2014-05-31"
__author__ = "Serge Rey  (sjsrey@gmail.com)"
__copyright__ = "Copyright 2015,  Sergio Rey"
__license__ = "GPL"
__history__ = """
0.1 - Dev.
"""

NOW = datetime.date.today()
NOW_DATE_STRING = NOW.strftime("%Y-%m-%d")
DOW = "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"

NOW_DOW = NOW.weekday()
print NOW_DOW

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

freqs = {"W":7, "M": 31, "D": 1, "Y": 365}
dow = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3,
       "FRI": 4, "SAT": 5, "SUN": 6}

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
            future = today + datetime.timedelta(days=num * FREQS[freq])
            return future
        except:
            try:
                weekday = today.weekday()
                dsupper = ds.upper()
                if dsupper == 'TOD':
                    fwkd = weekday
                else:
                    fwkd = DOW[ds.upper()]
                if weekday > fwkd:
                    future = today + datetime.timedelta(days = 7 + fwkd - weekday)
                else:
                    future = today + datetime.timedelta(days = fwkd - weekday)
                return future
            except:
                print 'bad shortcut: ', dateString

DONE = "done.txt"


class Item:
    """
    Individual task item
    """
    def __init__(self, line):

        words = line.strip().split()
        taskWords = words[:]
        self.dow = words[0].split(":")[0]
        self.dow = self.dow.upper()[:3]
        self.add = False
        self.project = None
        if self.dow in DOW and DOW.index(self.dow) == NOW_DOW:
            print 'today'
            self.add = True
        elif self.dow not in DOW: # daily
            print "Daily"
            self.add = True

        if self.add:

            # get date
            line  = "s:"+NOW_DATE_STRING

            # reformat so project is at the beginning of string

            project = [ word for word in taskWords if word[0]=="+"]
            self.project = project
            body_words = [ word for word in taskWords[1:] if word[0]!="+"]
            words = [project[0], line]
            words.extend(body_words)
            self.line = " ".join(words)


    
def separator(c):
    sep = ""
    sep = c * 42
    print sep


def main(argv):
    # make sure you have all your args
    if len(argv) < 1:
        usage()
        sys.exit(2)

    # process recur.txt
    addItems = {}
    try:
        f = open(argv[1], "r")
        lines = f.readlines()
        f.close()
        id = 1
        for line in lines:
            print line
            item = Item(line)
            if item.add:
                addItems[item] = item
            for item in addItems:
                print item.line
    except IOError:
        print "ERROR:  The file named %s could not be read."% (argv[1], )
        usage()
        sys.exit(2)

    if addItems:
        # process todo.txt and add new items
        try:
            f = open(argv[0], 'r')
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            f.close()
            for item in addItems:
                lines.append(item.line)
                lines.sort()
            print "\n".join(lines)
            f = open(argv[0], 'w')
            f.write("\n".join(lines))
            f.close()

        except IOError:
            print "Error: The file name %s could not be read."%(argv[0], )
            


if __name__ == "__main__":
    main(sys.argv[1:])
