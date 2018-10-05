from classes import *
import itertools
import os
import json


path = os.path.abspath(os.path.dirname(__file__))

try:

    with open(os.path.join(path, 'data/data.json'), 'r') as f:
        profs_dict =  CaseInsensitiveDict(json.load(f))

except FileNotFoundError:
    profs_dict = CaseInsensitiveDict({})

TIMETABLE_KEY = 'timetable'

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
