#!/usr/bin/python3
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import mechanize
import cookielib
import json
import pickle
import os

cookie = os.getenv('JSESSIONID')

# Professor class
class Prof(object):
    def __init__(self, name, slots, venues):
        self.name = name
        self.slots = slots
        self.venues = venues

    def status(self):
        times = []

        for slot in self.slots:
            times.append(get_time(slot))

        return [times, self.venues]


# Get time from slot
def get_time(slot):
    with open('slots.1') as f:
        for line in f:
            if line.startswith(slot):
                return line.split()[1:]

def parse_html(dep):
    # Authenticate
    try:
        r = br.open('https://erp.iitkgp.ac.in/Acad/timetable_track.jsp?action=second&dept=%s' % dep)
    except:
        print("Can't fetch %s" % dep)
        return

    html = r.read()
    soup = BeautifulSoup(html, 'lxml')
    html = soup.find_all('table')[4]

    table_data = [[cell.text for cell in row("td")] for row in BeautifulSoup(str(html), 'lxml')("tr")]
    table_data = table_data[2:]

    table_data = [row for row in table_data if len(row) == 7]
    td = []

    for row in table_data:
        prof_names = row[2].split(',')
        slots = row[5].split(',')
        venues = row[6].split(',')

        for prof_name in prof_names:
            td.append(Prof(prof_name, slots, venues))

    table_data = td

    if len(table_data):
        return table_data

    else:
        print('No records found for %s' % dep)

def get_dep():
    with open('deps.4') as f:
        deps = f.read().split('\n')

    results = Parallel(n_jobs=len(deps), verbose=1, backend="threading")(map(delayed(parse_html), deps))
    results = [result for result in results if result is not None]

    return results

def get_times(prof_name):
    with open('data.pkl', 'rb') as f:
        data = pickle.load(f)

    details = {prof_name: []}

    for prof in data:
        if prof.name.lower() == prof_name.lower():
            details[prof_name].append(prof.status())

    return details

def populate_data():
    # Browser
    global br
    br = mechanize.Browser()

    # Enable cookie support
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    #br.set_handle_gzip( True )
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

    br.addheaders = [ ( 'User-agent', 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0' ), ('Cookie','JSESSIONID=%s' % cookie)]

    results = get_dep()

    with open('data.pkl', 'wb') as f:
        for result in results:
            pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)

def main():
    populate_data()

if __name__ == '__main__':
    main()

    print(get_times('Somnath Ghosh')) # Test run
