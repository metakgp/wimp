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
import env
import iitkgp_erp_login.erp as erp

path = os.path.abspath(os.path.dirname(__file__))

# Load professor data
try:
    with open(os.path.join(path, "data/data.json"), "r") as f:
        profs_dict = CaseInsensitiveDict(json.load(f))
except FileNotFoundError:
    profs_dict = CaseInsensitiveDict({})

# Load department data
try:
    with open(os.path.join(path, "data/dept_data"), "r") as f:
        dept_data = CaseInsensitiveDict(json.load(f))
except FileNotFoundError:
    dept_data = CaseInsensitiveDict({})

DEPT_KEY = "dept"
WEBSITE_KEY = "website"
TIMETABLE_KEY = "timetable"
KGP_WEBSITE_URL = "http://www.iitkgp.ac.in/"
DEPT_FETCH_URL = "https://www.iitkgp.ac.in/Departments/fetchAllFacListByDept"
TIMETABLE_FETCH_URL = "https://erp.iitkgp.ac.in/Acad/timetable_track.jsp?action=second&dept=%s"

def get_time(slot):
    """Obtains time for each slot from 'data/slots.1' file"""
    with open(os.path.join(path, "data/slots.1")) as f:
        for line in f:
            if line.startswith(slot):
                return line.split()[1:]

def parse_html(dep, session):
    """Parses HTML to get professor information and their timetable"""
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'ci_session=gk7bi3u0r2ej0h3qnihk4gocf0vp9e8e',
        'Host': 'www.iitkgp.ac.in',
        'Origin': 'https://www.iitkgp.ac.in',
        'Referer': 'https://www.iitkgp.ac.in/faclistbydepartment',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }

    start = 0
    length = 10
    more_pages = True

    while more_pages:
        payload = {
            'draw': 1,
            'columns[0][data]': 'empname',
            'columns[0][name]': '',
            'columns[0][searchable]': 'true',
            'columns[0][orderable]': 'true',
            'columns[0][search][value]': '',
            'columns[0][search][regex]': 'false',
            'columns[1][data]': 'department',
            'columns[1][name]': '',
            'columns[1][searchable]': 'true',
            'columns[1][orderable]': 'true',
            'columns[1][search][value]': '',
            'columns[1][search][regex]': 'false',
            'columns[2][data]': 'designation',
            'columns[2][name]': '',
            'columns[2][searchable]': 'true',
            'columns[2][orderable]': 'true',
            'columns[2][search][value]': '',
            'columns[2][search][regex]': 'false',
            'order[0][column]': '0',
            'order[0][dir]': 'asc',
            'start': str(start),
            'length': str(length),
            'search[value]': '',
            'search[regex]': 'false',
            'lang': 'en'
        }

        dept_resp = session.post(DEPT_FETCH_URL, headers=headers, data=payload)
        dept_raw_data = json.loads(dept_resp.content).get("data", [])

        if not dept_raw_data:
            more_pages = False
        else:
            for prof in dept_raw_data:
                name = re.findall(r">(.+?)<", prof["faculty"])[0].replace("  ", "")
                dept = prof["dept_code"]

                soup = BeautifulSoup(prof["faculty"], "lxml")
                for tag in soup.findAll("a", href=True):
                    href = tag["href"]
                    website = KGP_WEBSITE_URL + href

                    dept_data[name] = {"dept": dept, "website": website}

            start += length

    with open("data/dept_data", "w") as f:
        json.dump(dept_data, f)

    try:
        response = session.get(TIMETABLE_FETCH_URL % dep)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        html = soup.find_all("table")[4]
        print("Fetched for %s" % dep)
    except Exception as err:
        print("Can't fetch %s" % dep)
        print(err)
        return

    table_data = [
        [cell.text for cell in row("td")]
        for row in BeautifulSoup(str(html), "lxml")("tr")
    ]
    table_data = [row for row in table_data[2:] if len(row) == 7]

    with open("data/table_test", "w") as f:
        f.write(str(table_data))

    for row in table_data:
        prof_names = [name.title() for name in row[2].split(",")]
        slots = [slot.replace(" ", "") for slot in row[5].split(",")]
        venues = [venue.replace("Deptt.", "Dept") for venue in row[6].split(",")]

        for prof_name in prof_names:
            for slot in slots:
                if prof_name not in profs_dict:
                    profs_dict[prof_name] = {}

                    try:
                        profs_dict[prof_name][DEPT_KEY] = dept_data[prof_name][DEPT_KEY]
                        profs_dict[prof_name][WEBSITE_KEY] = dept_data[prof_name][WEBSITE_KEY]
                    except KeyError:
                        profs_dict[prof_name][DEPT_KEY] = dep
                        profs_dict[prof_name][WEBSITE_KEY] = "#"

                    profs_dict[prof_name][TIMETABLE_KEY] = []

                profs_dict[prof_name][TIMETABLE_KEY].append([get_time(slot), venues])

    if len(profs_dict):
        return profs_dict
    else:
        print("No records found for %s" % dep)

def get_times(prof_name):
    data = CaseInsensitiveDict(profs_dict)
    result = []

    try:
        result = data[prof_name][TIMETABLE_KEY]
        if result:
            result.sort()
            result = list(result for result, _ in itertools.groupby(result))
    except KeyError:
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
    except KeyError:
        pass

    return result

def get_table(details):
    tb = {f"{i}{j}": [] for i in range(5) for j in range(9)}

    for times, venues in details:
        venues = set(v.strip() for v in venues)

        for time in times:
            tb[time] = venues

    return tb

def populate_data(specific_dep=None):
    headers = {
        'timeout': '20',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'
    }

    session = requests.Session()
    _, ssoToken = erp.login(headers, session, ERPCREDS=env, LOGGING=True, SESSION_STORAGE_FILE='.session')

    with open(os.path.join(path, "data/deps.4")) as f:
        deps = f.read().split("\n")

    if specific_dep is None:
        for dep in deps:
            parse_html(dep, session)
    else:
        parse_html(specific_dep, session)

    with open(os.path.join(path, "data/data.json"), "w") as f:
        json.dump(profs_dict, f)

def main():
    dep = str(input("Is there a specific dep which you want to enter (write dep code), leaving this will update for all deps:\n"))
    if dep == "":
        dep = None
    populate_data(dep)

if __name__ == "__main__":
    main()
    # Uncomment below to test
    # print(get_table(get_times('Jitendra Kumar')))

