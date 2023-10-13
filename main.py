#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

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

from dotenv import load_dotenv

load_dotenv()

path = os.path.abspath(os.path.dirname(__file__))

try:
    with open(os.path.join(path, "data/data.json"), "r") as f:
        profs_dict = CaseInsensitiveDict(json.load(f))

except FileNotFoundError:
    profs_dict = CaseInsensitiveDict({})

NAME_KEY = "name"
DEPT_KEY = "dept"
WEBSITE_KEY = "website"
TIMETABLE_KEY = "timetable"
DEPT_FETCH_URL = "https://www.iitkgp.ac.in/Departments/fetchAllFacListByDept"
TIMETABLE_FETCH_URL = (
    "https://erp.iitkgp.ac.in/Acad/timetable_track.jsp?action=second&dept=%s"
)


def get_time(slot):
    # Obtains time for each slot from 'data/slots.1' file

    with open(os.path.join(path, "data/slots.1")) as f:
        for line in f:
            if line.startswith(slot):
                return line.split()[1:]


def parse_html(dep):
    # Get prof timetable
    try:
        br.open(TIMETABLE_FETCH_URL % dep)
        # print(br.response.content)
        html = br.response.content
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

    # Test code for writing data obtained to, uncomment when want to test
    with open("data/table_test", "w") as f:
        f.write(str(table_data))

    # Get prof department
    """
    Note:

    If a prof teaches subjects from other departments,
    it's not a good idea to add directly from the table.
    Instead, we try to find it from IIT KGP website. If
    not found, we'll add it from our data of the subject.

    """
    dept_resp = requests.post(DEPT_FETCH_URL,data={'lang':'en'})
    dept_raw_data = json.loads(dept_resp.content)["aaData"]
    dept_data = CaseInsensitiveDict({})

    for prof in dept_raw_data:
        name = re.findall(r">(.+?)<", prof["empname"])[0]
        name = name.replace("  ", "")
        dept = re.findall(r"department\/(..)",prof["empname"])[0]

        soup = BeautifulSoup(prof["empname"], "lxml")
        
        for tag in soup.find_all("a", href=True):
            website = tag["href"]
            prof_id =  website.split("/")[-1]
            dept_data[prof_id] = {"name":name,"dept": dept, "website": website}
            with open("data/dept_data", "w") as f:
                json.dump(dept_data, f)

    for row in table_data:
        prof_names = [name.title() for name in row[2].split(",")]
        slots = [slot.replace(" ", "") for slot in row[5].split(",")]
        venues = [venue.replace("Instrumentaion", "Instrumentation") for venue in re.split(r"[,#]+",row[6])]

        
        for prof_name in prof_names:
            """
            Note:
            "ERP > Academic > Timetable > Subject List with Timetable Slots" does not tell which prof 
            is teaching the course in case of profs with the same name. So either we completely ignore
            these courses, or assume that the prof belongs to the dept offering the course. This is not
            the ideal implementation as there can be courses where none of these same-name profs belong
            to the course dept. In that case the best we can do is to skip this prof for the particular course.
            """
            prof = {k:v for k,v in dept_data.items() if v[NAME_KEY]==prof_name}
            # Get prof id
            if(len(prof.keys())>1):
                prof_id= next((k for k,v in prof.items() if v[DEPT_KEY]==dep),None)
            else:
                prof_id = next((k for k in prof.keys()), None)
            if prof_id is None:
                continue

            for slot in slots:
                if prof_id not in profs_dict:
                    profs_dict[prof_id] = {}

                    try:
                        profs_dict[prof_id][NAME_KEY] = dept_data[prof_id][NAME_KEY]
                        profs_dict[prof_id][DEPT_KEY] = dept_data[prof_id][DEPT_KEY]
                        profs_dict[prof_id][WEBSITE_KEY] = dept_data[prof_id][WEBSITE_KEY]

                    except KeyError:
                        profs_dict[prof_id][NAME_KEY] = "Bhoot"
                        profs_dict[prof_id][DEPT_KEY] = dep
                        profs_dict[prof_id][WEBSITE_KEY] = "#"

                    profs_dict[prof_id][TIMETABLE_KEY] = []
                
                profs_dict[prof_id][TIMETABLE_KEY].append([get_time(slot), venues])

    if len(profs_dict):
        # with open('data/test_prof', 'w') as f:
        #     json.dump(profs_dict, f)
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
            tb.update({"%d%d" % (i, j): []})

    for times, venues in details:
        venues = set(v.strip() for v in venues)

        for time in times:
            tb[time] = venues

    return tb


def populate_data(specific_dep=None):
    if not os.getenv("JSESSIONID"):
        print("ERROR: Please set environment variable JSESSIONID!")
        sys.exit(1)

    cookie = {"JSESSIONID": os.getenv("JSESSIONID")}

    # Browser
    global br
    br = RoboBrowser(
        history=True,
        user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
        parser="lxml",
    )

    # Update cookie
    br.session.cookies.update(cookie)

    with open(os.path.join(path, "data/deps.4")) as f:
        deps = f.read().split("\n")
    # parse_html('EC')
    if specific_dep is None:
        for dep in deps:
            parse_html(dep)
    else:
        parse_html(specific_dep)

    with open(os.path.join(path, "data/data.json"), "w") as f:
        json.dump(profs_dict, f)


def main():
    dep = None
    dep = str(
        input(
            """Is there a specific dep which you want to enter (write dep code),leaving this will update for all deps:\n"""
        )
    )
    if dep == "":
        dep = None
    populate_data(dep)


if __name__ == "__main__":
    # Run main to populate data
    main()

    # Test run, uncomment if you want to test one output
    # print(get_table(get_times('Abhijit Das')))
