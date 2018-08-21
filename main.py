#!/usr/bin/python3
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import mechanize
import cookielib
import json
import os
import itertools

cookie = os.getenv('JSESSIONID')

# CaseInsensitiveDict class inherited from dict
class CaseInsensitiveDict(dict):
    """Basic case insensitive dict with strings only keys."""

    proxy = {}

    def __init__(self, data):
        self.proxy = dict((k.lower(), k) for k in data)
        for k in data:
            self[k] = data[k]

    def __contains__(self, k):
        return k.lower() in self.proxy

    def __delitem__(self, k):
        key = self.proxy[k.lower()]
        super(CaseInsensitiveDict, self).__delitem__(key)
        del self.proxy[k.lower()]

    def __getitem__(self, k):
        key = self.proxy[k.lower()]
        return super(CaseInsensitiveDict, self).__getitem__(key)

    def get(self, k, default=None):
        return self[k] if k in self else default

    def __setitem__(self, k, v):
        super(CaseInsensitiveDict, self).__setitem__(k, v)
        self.proxy[k.lower()] = k


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
    table_data = [row for row in table_data[2:] if len(row) == 7]
    td = CaseInsensitiveDict({})

    for row in table_data:
        prof_names = row[2].split(',')
        slots = [slot.replace(' ', '') for slot in row[5].split(',')]
        venues = row[6].split(',')

        for prof_name in prof_names:
            for slot in slots:
                if prof_name not in td:
                    td[prof_name] = [[get_time(slot), venues]]

                else:
                    td[prof_name].append([get_time(slot), venues])


    if len(td):
        return td

    else:
        print('No records found for %s' % dep)

def get_dep():
    with open('deps.4') as f:
        deps = f.read().split('\n')

    results = Parallel(n_jobs=len(deps), verbose=1, backend="threading")(map(delayed(parse_html), deps))
    results = [result for result in results if result]
    _results = CaseInsensitiveDict({})

    for result in results:
        _results.update(result)

    return _results

def get_times(prof_name):
    with open('data.json', 'rb') as f:
        data = CaseInsensitiveDict(json.load(f))

    result = data[prof_name]

    if result:
        result.sort()
        result = list(result for result, _ in itertools.groupby(result))

    return result

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

    br.addheaders = [('User-agent', 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'), ('Cookie','JSESSIONID=%s' % cookie)]

    results = get_dep()

    with open('data.json', 'wb') as f:
        json.dump(results, f)

def main():
    populate_data()

if __name__ == '__main__':
    # Run main to populate data
    #main()

    print(get_times('debdoot Sheet')) # Test run
