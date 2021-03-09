#!/usr/bin/python3.6
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from classes import *

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser

import itertools
import requests
import json
import re
import os
import sys

path = os.path.abspath(os.path.dirname(__file__))

try:

    with open(os.path.join(path, 'data/data.json'), 'r') as f:
        profs_dict = CaseInsensitiveDict(json.load(f))

except FileNotFoundError:
    profs_dict = CaseInsensitiveDict({})

DEPT_KEY = 'dept'
WEBSITE_KEY = 'website'
TIMETABLE_KEY = 'timetable'
KGP_WEBSITE_URL = 'http://www.iitkgp.ac.in/'
DEPT_FETCH_URL = 'http://www.iitkgp.ac.in/facultylist?processOn=onload&colName=&searchContent=&_=1538283022101'
TIMETABLE_FETCH_URL = 'https://erp.iitkgp.ac.in/Acad/timetable_track.jsp?action=second&dept=%s'


def get_time(slot):
    # Obtains time for each slot from 'data/slots.1' file

    with open(os.path.join(path, 'data/slots.1')) as f:
        for line in f:
            if line.startswith(slot):
                return line.split()[1:]


def parse_html(dep):
    # Get prof timetable
    try:

        br.open(TIMETABLE_FETCH_URL % dep)
        # print(br.response.content)
        html = br.response.content
        soup = BeautifulSoup(html, 'lxml')
        html = soup.find_all('table')[4]
        print("Fetched for %s" % dep)
    except Exception as err:
        print("Can't fetch %s" % dep)
        print(err)
        return

    table_data = [[cell.text for cell in row("td")] for row in BeautifulSoup(str(html), 'lxml')("tr")]
    table_data = [row for row in table_data[2:] if len(row) == 7]

    # Test code for writing data obtained to, uncomment when want to test
    with open('data/table_test', 'w') as f:
        f.write(str(table_data))

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

            dept_data[name] = {'dept': dept,
                               'website': website}
            with open('data/dept_data', 'w') as f:
                json.dump(dept_data, f)

    for row in table_data:
        prof_names = [name.title() for name in row[2].split(',')]
        slots = [slot.replace(' ', '') for slot in row[5].split(',')]
        venues = [venue.replace('Deptt.', 'Dept') for venue in row[6].split(',')]

        for prof_name in prof_names:
            # print(prof_name)
            for slot in slots:
                if prof_name not in profs_dict:
                    profs_dict[prof_name] = {}

                    try:

                        profs_dict[prof_name][DEPT_KEY] = dept_data[prof_name][DEPT_KEY]
                        profs_dict[prof_name][WEBSITE_KEY] = dept_data[prof_name][WEBSITE_KEY]

                    except KeyError:

                        profs_dict[prof_name][DEPT_KEY] = dep
                        profs_dict[prof_name][WEBSITE_KEY] = '#'

                    profs_dict[prof_name][TIMETABLE_KEY] = []

                profs_dict[prof_name][TIMETABLE_KEY].append([get_time(slot), venues])

    if len(profs_dict):
        # with open('data/test_prof', 'w') as f:
        #     json.dump(profs_dict, f)
        return profs_dict

    else:
        print('No records found for %s' % dep)


def get_times(prof_name):
    data = CaseInsensitiveDict(profs_dict)
    result = []

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
    tb = {}

    for i in range(5):
        for j in range(9):
            tb.update({'%d%d' % (i, j): []})

    for times, venues in details:
        venues = set(v.strip() for v in venues)

        for time in times:
            tb[time] = venues

    return tb


def populate_data(specific_dep=None):
    if not os.getenv('JSESSIONID'):
        print("ERROR: Please set environment variable JSESSIONID!")
        sys.exit(1)

    cookie = {
        "JSESSIONID": os.getenv('JSESSIONID')
    }

    # Browser
    global br
    br = RoboBrowser(history=True,
                     user_agent='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0',
                     parser='lxml'
                     )

    # Update cookie
    br.session.cookies.update(cookie)

    with open(os.path.join(path, 'data/deps.4')) as f:
        deps = f.read().split('\n')
    # parse_html('EC')
    if specific_dep is None:
        for dep in deps:
            parse_html(dep)
    else:
        parse_html(specific_dep)

    with open(os.path.join(path, 'data/data.json'), 'w') as f:
        json.dump(profs_dict, f)


def main():
    dep = None
    dep = str(input('''Is there a specific dep which you want to enter (write dep code),leaving this will update for all deps:\n'''))
    if dep == "":
        dep = None
    populate_data(dep)


if __name__ == '__main__':
    # Run main to populate data
    main()

    # Test run, uncomment if you want to test one output
    # print(get_table(get_times('Jitendra kumar')))
