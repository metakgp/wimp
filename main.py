#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from classes import *
import mechanize
import cookielib
import itertools
import requests
import json
import re
import os

path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(path, 'data/data.json'), 'rb') as f:
    profs_dict =  CaseInsensitiveDict(json.load(f))

DEPT_KEY = 'dept'
WEBSITE_KEY = 'website'
TIMETABLE_KEY = 'timetable'
KGP_WEBSITE_URL = 'http://www.iitkgp.ac.in/'
DEPT_FETCH_URL = 'http://www.iitkgp.ac.in/facultylist?processOn=onload&colName=&searchContent=&_=1538283022101'
TIMETABLE_FETCH_URL = 'https://erp.iitkgp.ac.in/Acad/timetable_track.jsp?action=second&dept=%s'

# Get time from slot
def get_time(slot):
    with open(os.path.join(path, 'data/slots.1')) as f:
        for line in f:
            if line.startswith(slot):
                return line.split()[1:]


def parse_html(dep):
    # Get prof timetable
    try:

        r = br.open(TIMETABLE_FETCH_URL % dep)

    except:

        print("Can't fetch %s" % dep)
        return

    html = r.read()
    soup = BeautifulSoup(html, 'lxml')
    html = soup.find_all('table')[4]

    table_data = [[cell.text for cell in row("td")] for row in BeautifulSoup(str(html), 'lxml')("tr")]
    table_data = [row for row in table_data[2:] if len(row) == 7]

    # Get prof department
    """
    Note:

    If a prof teaches subjects from other departments,
    it's not a good idea to add directly from the table.
    Instead, we try to find it from IIT KGP website. If
    not found, we'll add it from out data of the subject.

    """
    dept_resp = requests.get(DEPT_FETCH_URL)
    dept_raw_data = json.loads(dept_resp.content)['data']
    dept_data = CaseInsensitiveDict({})

    for prof in dept_raw_data:
        name = re.findall(r'>(.+?)<', prof['faculty'])[0]
        name = name.replace('  ', '')
        dept = prof['dept_code']

        soup = BeautifulSoup(prof['faculty'], 'lxml')

        for tag in soup.findAll('a', href=True):
            href = tag['href']

            website = KGP_WEBSITE_URL + href

            dept_data[name] = { 'dept' : dept,
                                'website' : website }


    for row in table_data:
        prof_names = [name.title() for name in row[2].split(',')]
        slots = [slot.replace(' ', '') for slot in row[5].split(',')]
        venues = [venue.replace('Deptt.', 'Dept') for venue in row[6].split(',')]

        for prof_name in prof_names:
            for slot in slots:
                if prof_name not in profs_dict:
                    profs_dict[prof_name] = { }

                    try:

                        profs_dict[prof_name][DEPT_KEY] = dept_data[prof_name][DEPT_KEY]
                        profs_dict[prof_name][WEBSITE_KEY] = dept_data[prof_name][WEBSITE_KEY]

                    except KeyError:

                        profs_dict[prof_name][DEPT_KEY] = dep
                        profs_dict[prof_name][WEBSITE_KEY] = '#'

                    profs_dict[prof_name][TIMETABLE_KEY] = [ ]

                profs_dict[prof_name][TIMETABLE_KEY].append([get_time(slot), venues])


    if len(profs_dict):
        return profs_dict

    else:
        print('No records found for %s' % dep)


def get_times(prof_name):
    data = CaseInsensitiveDict(profs_dict)
    result = [ ]

    try:

        result = data[prof_name][TIMETABLE_KEY]

        if result:
            result.sort()
            result = list(result for result, _ in itertools.groupby(result))

    except:

        pass

    return result


def correct_spelling(prof_name):
    prof_names = profs_dict.keys()

    if prof_name not in prof_names:
        corrector = SpellingCorrector(prof_names)

        return corrector.correction(prof_name)

    return prof_name


def get_attr(prof_name, key):
    data = CaseInsensitiveDict(profs_dict)
    result = ""

    try:

        result = data[prof_name][key]

    except:

        pass

    return result


def get_table(details):
    tb = { }

    for i in range(5):
        for j in range(9):
            tb.update({'%d%d' % (i,j): []})

    for times, venues in details:
        venues = set(v.strip() for v in venues)

        for time in times:
            tb[time] = venues

    return tb


def populate_data():
    cookie = os.getenv('JSESSIONID')

    # Browser
    global br
    br = mechanize.Browser()

    # Enable cookie support
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_proxies({})

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)

    # Debugging messages
    br.set_debug_http(True)
    br.set_debug_redirects(True)
    br.set_debug_responses(True)

    br.addheaders = [('User-agent', 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'), ('Cookie','JSESSIONID=%s' % cookie)]

    with open(os.path.join(path, 'data/deps.4')) as f:
        deps = f.read().split('\n')

    for dep in deps:
        parse_html(dep)

    with open(os.path.join(path, 'data/data.json'), 'wb') as f:
        json.dump(profs_dict, f)

def main():
    populate_data()

if __name__ == '__main__':
    # Run main to populate data
    main()

    # Test run
    print(get_table(get_times('Jitendra kumar')))
