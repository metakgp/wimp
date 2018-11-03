#!/usr/bin/python3
#-*- coding: utf-8 -*-

import collections
import requests
import re

# CaseInsensitiveDict class inherited from dict
# Also returns '' on KeyError
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
        try:

            key = self.proxy[k.lower()]
            return super(CaseInsensitiveDict, self).__getitem__(key)


        except KeyError:

            return ''


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


class Department:
    """Represents a department"""
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.code = kwargs.get("code")
    
    def __str__(self):
        return "Department(name={0}, code={1})".format(self.name, self.code)

class FacultyMember:
    """Represents a faculty member"""
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.department = Department(**kwargs.get("department"))
        self.designation = kwargs.get("designation")

    def __str__(self):
        return "FacultyMember(name={0}, department={1}, designation={2})".format(self.name, self.department, self.designation)

class Subject:
    """Represents a subject"""
    def __init__(self, **kwargs):
        self.course = Course(**kwargs.get("course"))
        self.slot = Slot(**kwargs.get("slot"))
        self.rooms = kwargs.get("rooms")
    
    def __str__(self):
        return "Subject(course={0}, slot={1}, rooms={2})".format(self.course, self.slot, self.rooms)

class Course:
    "Represents a course"
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.code = kwargs.get("code")
        self.credits = kwargs.get("credits")
    
    def __str__(self):
        return "Course(name={0}, code={1}, credits={2})".format(self.name, self.code, self.credits)

class Slot:
    "Represents a slot"
    def __init__(self, **kwargs):
        self.time = Time(**kwargs.get("time"))
        self.slot = kwargs.get("slot")
    
    def __str__(self):
        return "Slot(time={0}, slot={1})".format(self.time, self.slot)

class Time:
    """Represents an academic time slot"""
    def __init__(self, **kwargs):
        self.day = kwargs.get("day")
        self.time = kwargs.get("time")

    def __str__(self):
        return "Time(day={0}, time={1})".format(self.day, self.time)

class TT(dict):
    "Represents a weekly timetable"
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    def __init__(self, **kwargs):
        for day in self.days:
            self[day] = kwargs.get(day, list())

    def __str__(self):
        r = ''
        for day, schedule in self.items():
            for s in schedule: 
                r += "{0}: {1}\n".format(day, s)

        return r

class TimeTable(object):
    def __init__(self, prof):
        self.prof = prof

    
    def __repr__(self):
        r = requests.get(TIMETABLE_FETCH_URL.format(name=self.prof.name, dept=self.prof.dept))
        raw_data = r.json()
        data = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for day in days:
            for slot in raw_data[day]:
                i = str(days.index(day))
                j = int(re.findall(r'\d+', slot['slot']['time']['time'])[0])
                j = j - 8 if j > 5 else j + 3
                j = str(j)
                rooms = slot['rooms']
                data[i+j] = rooms

        return str(data)