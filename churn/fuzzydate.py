# -*- coding: utf-8 -*-

import re
import datetime
import dateutil.tz
import unittest

class fuzzydate:
    def __init__(self, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None, tzinfo=None):
        self.year=year
        self.month=month
        self.day=day
        self.hour=hour
        self.minute=minute
        self.second=second
        self.microsecond=microsecond
        self.tzinfo=tzinfo
    def empty_date(self):
        return self.year is None and self.month is None and self.day is None
    def empty_time(self):
        return self.hour is None and self.minute is None and self.second is None and self.microsecond is None and self.tzinfo is None
    def empty(self):
        return self.empty_date() and self.empty_time()

    def date(self):
        assert(self.year is not None and self.month is not None and self.day is not None)
        return datetime.date(self.year, self.month, self.day)

    def time(self):
        assert(self.hour is not None and self.minute is not None)
        # allow 0 for missing sec/ms
        second = self.second if self.second is not None else 0
        microsecond = self.microsecond if self.microsecond is not None else 0
        return datetime.time(self.hour, self.minute, second, microsecond, self.tzinfo)

    def datetime(self):
        if self.year is None:
            return None
        return datetime.datetime.combine(self.date(), self.time())

    def __repr__(self):
        return "%s-%s-%s %s:%s:%s %s" %(self.year,self.month,self.day, self.hour,self.minute, self.second, self.tzinfo)
    @classmethod
    def combine(cls, *args):
        fd = fuzzydate()
        for a in args:
            fd.year = fd.year if a.year is None else a.year
            fd.month = fd.month if a.month is None else a.month
            fd.day = fd.day if a.day is None else a.day
            fd.hour = fd.hour if a.hour is None else a.hour
            fd.minute = fd.minute if a.minute is None else a.minute
            fd.second = fd.second if a.second is None else a.second
            fd.microsecond = fd.microsecond if a.microsecond is None else a.microsecond
            fd.tzinfo = fd.tzinfo if a.tzinfo is None else a.tzinfo
        return fd
        

# order is important(ish) - want to match as much of the string as we can
date_crackers = [

    #"Tuesday 16 December 2008"
    #"Tue 29 Jan 08"
    #"Monday, 22 October 2007"
    #"Tuesday, 21st January, 2003"
    r'(?P<dayname>\w{3,})[.,\s]+(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>\w{3,})[.,\s]+(?P<year>(\d{4})|(\d{2}))',

    # "Friday    August    11, 2006"
    # "Tuesday October 14 2008"
    # "Thursday August 21 2008"
    #"Monday, May. 17, 2010"
    r'(?P<dayname>\w{3,})[.,\s]+(?P<month>\w{3,})[.,\s]+(?P<day>\d{1,2})(?:st|nd|rd|th)?[.,\s]+(?P<year>(\d{4})|(\d{2}))',

    # "9 Sep 2009", "09 Sep, 2009", "01 May 10"
    # "23rd November 2007", "22nd May 2008"
    r'(?P<day>\d{1,2})(?:st|nd|rd|th)?\s+(?P<month>\w{3,})[.,\s]+(?P<year>(\d{4})|(\d{2}))',
    # "Mar 3, 2007", "Jul 21, 08", "May 25 2010", "May 25th 2010", "February 10 2008"
    r'(?P<month>\w{3,})[.,\s]+(?P<day>\d{1,2})(?:st|nd|rd|th)?[.,\s]+(?P<year>(\d{4})|(\d{2}))',

    # "2010-04-02"
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})',
    # "2007/03/18"
    r'(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})',
    # "22/02/2008"
    # "22-02-2008"
    # "22.02.2008"
    r'(?P<day>\d{1,2})[/.-](?P<month>\d{1,2})[/.-](?P<year>\d{4})',
    # "09-Apr-2007", "09-Apr-07"
    r'(?P<day>\d{1,2})-(?P<month>\w{3,})-(?P<year>(\d{4})|(\d{2}))',


    # dd-mm-yy
    r'(?P<day>\d{1,2})-(?P<month>\d{1,2})-(?P<year>\d{2})',
    # dd/mm/yy
    r'(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{2})',
    # dd.mm.yy
    r'(?P<day>\d{1,2})[.](?P<month>\d{1,2})[.](?P<year>\d{2})',

    # TODO:
    # mm/dd/yy
    # dd.mm.yy
    # etc...
    # YYYYMMDD

    # TODO:
    # year/month only

    # "May/June 2011" (common for publications) - just use second month
    r'(?P<cruftmonth>\w{3,})/(?P<month>\w{3,})\s+(?P<year>\d{4})',

    # "May 2011"
    r'(?P<month>\w{3,})\s+(?P<year>\d{4})',
]

date_crackers = [re.compile(pat,re.UNICODE|re.IGNORECASE) for pat in date_crackers]

dayname_lookup = {
    'mon': 'mon', 'monday': 'mon',
    'tue': 'tue', 'tuesday': 'tue',
    'wed': 'wed', 'wednesday': 'wed',
    'thu': 'thu', 'thursday': 'thu',
    'fri': 'fri', 'friday': 'fri',
    'sat': 'sat', 'saturday': 'sat',
    'sun': 'sun', 'sunday': 'sun',
    # es
    'lunes': 'mon',
    'martes': 'tue',
    'miércoles': 'wed',
    'jueves': 'thu',
    'viernes': 'fri',
    'sábado': 'sat',
    'domingo': 'sun',
}


month_lookup = {
    '01': 1, '1':1, 'jan': 1, 'january': 1,
    '02': 2, '2':2, 'feb': 2, 'february': 2,
    '03': 3, '3':3, 'mar': 3, 'march': 3,
    '04': 4, '4':4, 'apr': 4, 'april': 4,
    '05': 5, '5':5, 'may': 5, 'may': 5,
    '06': 6, '6':6, 'jun': 6, 'june': 6,
    '07': 7, '7':7, 'jul': 7, 'july': 7,
    '08': 8, '8':8, 'aug': 8, 'august': 8,
    '09': 9, '9':9, 'sep': 9, 'september': 9,
    '10': 10, '10':10, 'oct': 10, 'october': 10,
    '11': 11, '11':11, 'nov': 11, 'november': 11,
    '12': 12, '12':12, 'dec': 12, 'december': 12,
    # es
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12,
}


# "BST" ,"+02:00", "+02"
tz_pat = r'(?P<tz>Z|[A-Z]{2,10}|(([-+])(\d{2})((:?)(\d{2}))?))'
ampm_pat = r'(?:(?P<am>am)|(?P<pm>pm))'

time_crackers = [
    #4:48PM GMT
    r'(?P<hour>\d{1,2})[:.](?P<min>\d{2})(?:[:.](?P<sec>\d{2}))?\s*' + ampm_pat + r'\s*' + tz_pat,
    #3:34PM
    #10:42 am
    r'(?P<hour>\d{1,2})[:.](?P<min>\d{2})(?:[:.](?P<sec>\d{2}))?\s*' + ampm_pat,
    #13:21:36 GMT
    #15:29 GMT
    #12:35:44+00:00
    #00.01 BST
    r'(?P<hour>\d{1,2})[:.](?P<min>\d{2})(?:[:.](?P<sec>\d{2}))?\s*' + tz_pat,
    #12.33
    #14:21
    # TODO: BUG: this'll also pick up time from "30.25.2011"!
    r'(?P<hour>\d{1,2})[:.](?P<min>\d{2})(?:[:.](?P<sec>\d{2}))?\s*',

    # TODO: add support for microseconds?
]
time_crackers = [re.compile(pat,re.UNICODE|re.IGNORECASE) for pat in time_crackers]


def parse_date(s):
    for c in date_crackers:
        m = c.search(s)
        if not m:
            continue

        g = m.groupdict()

        year,month,day = (None,None,None)

        if 'year' in g:
            year = int(g['year'])
            if year < 100:
                year = year+2000

        if 'month' in g:
            month = month_lookup.get(g['month'].lower(),None)
            if month is None:
                continue    # not a valid month name (or number)

            # special case to handle "Jan/Feb 2010"...
            # we'll make sure the first month is valid, then ignore it
            if 'cruftmonth' in g:
                cruftmonth = month_lookup.get(g['month'].lower(),None)
                if cruftmonth is None:
                    continue    # not a valid month name (or number)

        if 'dayname' in g:
            dayname = dayname_lookup.get(g['dayname'].lower(),None)
            if dayname is None:
                continue

        if 'day' in g:
            day = int(g['day'])
            if day<1 or day>31:    # TODO: should take month into account
                continue

        if year is not None or month is not None or day is not None:
            return (fuzzydate(year,month,day),m.span())

    return (fuzzydate(),None)



def parse_time(s):
    i = 0
    for cracker in time_crackers:
        i=i+1
        m = cracker.search(s)
        if not m:
            continue

        g = m.groupdict()

        hour,minute,second,microsecond,tzinfo = (None,None,None,None,None)

        if g.get('hour', None) is not None:
            hour = int(g['hour'])

            # convert to 24 hour time
            # if no am/pm, assume 24hr
            if g.get('pm',None) is not None and hour>=1 and hour <=11:
                hour = hour + 12
            if g.get('am',None) is not None and hour==12:
                hour = hour - 12

            if hour<0 or hour>23:
                continue

        if g.get('min', None) is not None:
            minute = int(g['min'])
            if minute<0 or minute>59:
                continue

        if g.get('sec', None) is not None:
            second = int(g['sec'])
            if second<0 or second>59:
                continue

        if g.get('tz', None) is not None:
            tzinfo = dateutil.tz.gettz(g['tz'])


        if hour is not None or min is not None or sec is not None:
            return (fuzzydate(hour=hour,minute=minute,second=second,microsecond=microsecond,tzinfo=tzinfo),m.span())

    return (fuzzydate(),None)


def parse_datetime(s):
    # TODO: include ',', 'T', 'at', 'on' between  date and time in the matched span...

    time,timespan = parse_time(s)
    if timespan:
        # just to make sure time doesn't get picked up again as date... (bad news as hour can look like year!)
        s = s[:timespan[0]] + s[timespan[1]:]

    date,datespan = parse_date(s)
#    if datespan:
#        # just to make sure date doesn't get picked up again as time...
#        s = s[:datespan[0]] + s[datespan[1]:]

    fd = fuzzydate.combine(date,time)
#    print "%s -> %s" % (s,fd)
    return fd







class Tests(unittest.TestCase):

    # examples from the wild:
    examples_in_the_wild = [
        # timestring, expected result in UTC
        ("2010-04-02T12:35:44+00:00", (2010,4,2,12,35,44)),#(iso8601, bbc blogs)
        ("2008-03-10 13:21:36 GMT", (2008,3,10, 13,21,36)),  #(technorati api)
        ("9 Sep 2009 12.33", (2009,9,9,12,33,0)), #(heraldscotland blogs)
        ("May 25 2010 3:34PM", (2010,5,25,15,34,0)), #(thetimes.co.uk)
        ("Thursday August 21 2008 10:42 am", (2008,8,21,10,42,0)), #(guardian blogs in their new cms)
        ('Tuesday October 14 2008 00.01 BST', (2008,10,13,23,1,0)), #(Guardian blogs in their new cms)
        ('Tuesday 16 December 2008 16.23 GMT', (2008,12,16,16,23,0)), #(Guardian blogs in their new cms)
        ("3:19pm on Tue 29 Jan 08", (2008,1,29,15,19,0)), #(herald blogs)
        ("2007/03/18 10:59:02", (2007,3,18,10,59,2)),
        ("Mar 3, 2007 12:00 AM", (2007,3,3,0,0,0)),
        ("Jul 21, 08 10:00 AM", (2008,7,21,10,0,0)), #(mirror blogs)
        ("09-Apr-2007 00:00", (2007,4,9,0,0,0)), #(times, sundaytimes)
        ("4:48PM GMT 22/02/2008", (2008,2,22,16,48,0)), #(telegraph html articles)
        ("09-Apr-07 00:00", (2007,4,9,0,0,0)), #(scotsman)
        ("Friday    August    11, 2006", (2006,8,11,0,0,0)), #(express, guardian/observer)
        ("26 May 2007, 02:10:36 BST", (2007,5,26,1,10,36)), #(newsoftheworld)
        ("2:43pm BST 16/04/2007", (2007,4,16,13,43,0)), #(telegraph, after munging)
        ("20:12pm 23rd November 2007", (2007,11,23,20,12,0)), #(dailymail)
        ("2:42 PM on 22nd May 2008", (2008,5,22,14,42,0)), #(dailymail)
        ("February 10 2008 22:05", (2008,2,10,22,5,0)), #(ft)
#        ("22 Oct 2007, #(weird non-ascii characters) at(weird non-ascii characters)11:23", (2007,10,22,11,23,0)), #(telegraph blogs OLD!)
        ('Feb 2, 2009 at 17:01:09', (2009,2,2,17,1,9)), #(telegraph blogs)
        ("18 Oct 07, 04:50 PM", (2007,10,18,16,50,0)), #(BBC blogs)
        ("02 August 2007  1:21 PM", (2007,8,2,13,21,0)), #(Daily Mail blogs)
        ('October 22, 2007  5:31 PM', (2007,10,22,17,31,0)), #(old Guardian blogs, ft blogs)
        ('October 15, 2007', (2007,10,15,0,0,0)), #(Times blogs)
        ('February 12 2008', (2008,2,12,0,0,0)), #(Herald)
        ('Monday, 22 October 2007', (2007,10,22,0,0,0)), #(Independent blogs, Sun (page date))
        ('22 October 2007', (2007,10,22,0,0,0)), #(Sky News blogs)
        ('11 Dec 2007', (2007,12,11,0,0,0)), #(Sun (article date))
        ('12 February 2008', (2008,2,12,0,0,0)), #(scotsman)
        ('03/09/2007', (2007,9,3,0,0,0)), #(Sky News blogs, mirror)
        ('Tuesday, 21 January, 2003, 15:29 GMT', (2003,1,21,15,29,0)), #(historical bbcnews)
        ('2003/01/21 15:29:49', (2003,1,21,15,29,49)), #(historical bbcnews (meta tag))
        ('2010-07-01', (2010,7,1,0,0,0)),
        ('2010/07/01', (2010,7,1,0,0,0)),
        ('Feb 20th, 2000', (2000,2,20,0,0,0)),
        ('May 2008', (2008,5,1,0,0,0)),
        ('Monday, May. 17, 2010', (2010,5,17,0,0,0)),   # (time.com)
        ('Thu Aug 25 10:46:55 BST 2011', (2011,8,25,9,46,55)), # (www.yorkshireeveningpost.co.uk)

        #
        ('September, 26th 2011 by Christo Hall', (2011,9,26,0,0,0)),    # (www.thenewwolf.co.uk)
        # TODO: add better timezone parsing:
    #    ("Thursday April 7, 2011 8:56 PM NZT", (2011,4,7,8,56,00)),    # nz herald

        # some that should fail!
        ('50.50', None),
        ('13:01pm', None),
        ('01:62pm', None),
        # TODO: should reject these: (but day is just ignored)
#        ('32nd dec 2010', None),
    ]


    def setUp(self):
        self.utc = dateutil.tz.tzutc()
        pass

    def testExamplesInWild(self):
        for foo in self.examples_in_the_wild:
            fuzzy = parse_datetime(foo[0])
            got = self.fuzzy_to_dt(fuzzy)
            if foo[1] is not None:
                expected = datetime.datetime(*foo[1], tzinfo=self.utc)
            else:
                expected = None

            self.assertEqual(got,expected, "'%s': expected '%s', got '%s')" % (foo[0],expected,got))

    def testSpans(self):
        """ tests to make sure we are precise """
        got,span = parse_date('blah blah blah wibble foo, may 25th, 2011 some more crap here')
        self.assertEqual(span,(27,41))
 
        got,span = parse_date('wibble 25-01-2011 pibble')
        self.assertEqual(span,(7,17))

    def fuzzy_to_dt(self,fuzzy):
        """ helper to munge fuzzy date into full datetime """
        # year/month only is ok
        if fuzzy.day is None:
            fuzzy.day = 1

        # dates without time are OK
        if fuzzy.empty_time():
            fuzzy.hour=0
            fuzzy.minute=0
            fuzzy.second=0

        # assume utc if no timezone given
        if fuzzy.tzinfo is None:
            fuzzy.tzinfo = self.utc

        # convert to utc
        dt = fuzzy.datetime()
        if dt is not None:
            dt = dt.astimezone(self.utc)
        return dt

 
if __name__ == "__main__":
    unittest.main()
 
