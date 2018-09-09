#!/usr/bin/python2.7
#-*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from joblib import Parallel, delayed
import mechanize
import cookielib
import json
import os
import itertools
import collections

path = os.path.abspath(os.path.dirname(__file__))
profs_dict = {}
with open(os.path.join(path, 'data/data.json'), 'rb') as f:
    profs_dict = json.load(f)

DEPT_KEY = 'dept'
TIMETABLE_KEY = 'timetable'

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

class SpellingCorrector():
    """
        Spelling Corrector in Python 3; see http://norvig.com/spell-correct.html
        Copyright (c) 2007-2016 Peter Norvig
        MIT license: www.opensource.org/licenses/mit-license.php
    """
    word_list = []
    WORDS = collections.Counter([])

    def __init__(self, words):
        self.word_list = [t.lower() for t in words]
        self.WORDS = collections.Counter(self.word_list)

    def P(self, word, N=sum(WORDS.values())):
        "Probability of `word`."
        if N == 0:
            return 0
        return self.WORDS[word] / N

    def correction(self, word):
        "Most probable spelling correction for word."
        return max(self.candidates(word), key=self.P)

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.WORDS)

    def edits1(self, word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        "All edits that are two edits away from `word`."
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

# Get time from slot
def get_time(slot):
    with open(os.path.join(path, 'data/slots.1')) as f:
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
        prof_names = [name.title() for name in row[2].split(',')]
        slots = [slot.replace(' ', '') for slot in row[5].split(',')]
        venues = [venue.replace('Deptt.', 'Dept') for venue in row[6].split(',')]

        for prof_name in prof_names:
            for slot in slots:
                if prof_name not in td:
                    td[prof_name] = { }
                    td[prof_name][DEPT_KEY] = dep
                    td[prof_name][TIMETABLE_KEY] = [ ]

                td[prof_name][TIMETABLE_KEY].append([get_time(slot), venues])


    if len(td):
        return td

    else:
        print('No records found for %s' % dep)

def get_dep():
    with open(os.path.join(path, 'data/deps.4')) as f:
        deps = f.read().split('\n')

    results = Parallel(n_jobs=len(deps), verbose=1, backend="threading")(map(delayed(parse_html), deps))
    results = [result for result in results if result]
    _results = CaseInsensitiveDict({})

    for result in results:
        _results.update(result)

    return _results

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

def get_dept(prof_name):
    data = CaseInsensitiveDict(profs_dict)
    result = ""

    try:

        result = data[prof_name][DEPT_KEY]

    except:

        pass

    return result

def get_table(details):
    tb = {}

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

    results = get_dep()

    with open(os.path.join(path, 'data/data.json'), 'wb') as f:
        json.dump(results, f)

def main():
    populate_data()

if __name__ == '__main__':
    # Run main to populate data
    main()

    # Test run
    print(get_table(get_times('Jitendra kumar')))
