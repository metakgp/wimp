from bs4 import BeautifulSoup
from classes import *

import werkzeug

# Adjust werkzeug cached property for compatibility with RoboBrowser
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

from config import HEADERS, DEFAULT_PAYLOAD

# Define the absolute path for the current directory
path = os.path.abspath(os.path.dirname(__file__))

# Load professor data from JSON file (currently not used, initializing as an empty dictionary)
"""try:
    with open(os.path.join(path, "data/data.json"), "r") as f:
        profs_dict = CaseInsensitiveDict(json.load(f))
except FileNotFoundError:
    profs_dict = CaseInsensitiveDict({})"""
profs_dict = {}

# Load department data from JSON file (currently not used, initializing as an empty dictionary)
"""try:
    with open(os.path.join(path, "data/dept_data"), "r") as f:
        dept_data = CaseInsensitiveDict(json.load(f))
except FileNotFoundError:
    dept_data = CaseInsensitiveDict({})"""
dept_data = {}

# Constants for dictionary keys and URLs
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

    start = 0  # Start index for pagination
    length = 10  # Number of records to fetch per request
    more_pages = True  # Flag to indicate if there are more pages to fetch
    draw = 1  # Counter for pagination requests

    while more_pages:

        # Get prof department
        """
        Note:

        If a prof teaches subjects from other departments,
        it's not a good idea to add directly from the table.
        Instead, we try to find it from IIT KGP website. If
        not found, we'll add it from out data of the subject.

        """
        # Payload for the POST request to fetch department data
        PAYLOAD = DEFAULT_PAYLOAD.copy()
        PAYLOAD['draw'] = draw
        PAYLOAD['start'] = start
        PAYLOAD['length'] = length

        # Fetch department data
        dept_resp = session.post(DEPT_FETCH_URL, headers=HEADERS, data=PAYLOAD)
        dept_raw_data = json.loads(dept_resp.content).get("aaData", [])

        if not dept_raw_data:
            more_pages = False  # Stop fetching if no more data

        else:
            for prof in dept_raw_data:
                emp_name_html = prof.get("empname", "")
                department = prof.get("department", "N/A")
                designation = prof.get("designation", "N/A")

                # Ensure emp_name_html is not empty before processing
                if emp_name_html:
                    # Extract the name from the HTML content
                    emp_name_match = re.findall(r">(.+?)<", emp_name_html)
                    emp_name = emp_name_match[0].replace("  ", "") if emp_name_match else "Unknown"

                    # Parse the HTML to get the href attribute
                    soup = BeautifulSoup(emp_name_html, "lxml")
                    emp_url = None
                    prof_code = None
                    for tag in soup.find_all("a", href=True):
                        href = tag["href"]
                        emp_url = KGP_WEBSITE_URL + href if href.startswith("/") else href
                        prof_code_match = re.search(r"/faculty/(.+?)$", href)
                        prof_code = prof_code_match.group(1) if prof_code_match else None

                    if emp_url and prof_code:
                        # Transform the data into the desired format
                        dept_data[emp_name] = {
                            'dept': department,
                            'website': emp_url
                        }

                    else:
                        print(f"Failed to extract URL for: {emp_name_html}")
                else:
                    print(f"No empname found for prof: {prof}")

            start += length  # Increment start to fetch the next set of data
            draw += 1  # Increment draw to simulate pagination
    
    # Save the department data to a file
    with open("data/dept_data", "w") as f:
        json.dump(dept_data, f)

    try:
        # Fetch timetable data
        response = session.get(TIMETABLE_FETCH_URL % dep)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        html = soup.find_all("table")[4]
        print("Fetched for %s" % dep)
    except Exception as err:
        print("Can't fetch %s" % dep)
        print(err)
        return

    # Parse table data from the fetched HTML
    table_data = [
        [cell.text for cell in row("td")]
        for row in BeautifulSoup(str(html), "lxml")("tr")
    ]
    table_data = [row for row in table_data[2:] if len(row) == 7]

    # Save table data for testing
    with open("data/table_test", "w") as f:
        f.write(str(table_data))

    # Process each row in the table
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

                # Append slot times and venues to the professor's timetable
                profs_dict[prof_name][TIMETABLE_KEY].append([get_time(slot), venues])

    if len(profs_dict):
        return profs_dict  # Return the populated professor dictionary
    else:
        print("No records found for %s" % dep)

def populate_data(specific_dep=None):
    """Populate the data for a specific department or all departments"""
    headers = {
        'timeout': '20',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0'
    }

    # Initialize a session and log in
    session = requests.Session()
    _, ssoToken = erp.login(headers, session, ERPCREDS=env, LOGGING=True, SESSION_STORAGE_FILE='.session')

    # Load department codes
    with open(os.path.join(path, "data/deps.4")) as f:
        deps = f.read().split("\n")

    # Parse HTML for each department or a specific department
    if specific_dep is None:
        for dep in deps:
            parse_html(dep, session)
    else:
        parse_html(specific_dep, session)

    # Save the updated professor data
    with open(os.path.join(path, "data/data.json"), "w") as f:
        json.dump(profs_dict, f)

def main():
    """Main function to execute the script"""
    dep = str(input("Is there a specific department which you want to enter (write dep code), leaving this will update for all departments:\n"))
    if dep == "":
        dep = None
    populate_data(dep)

if __name__ == "__main__":
    main()
    # Uncomment below to test specific professor data
    # print(get_table(get_times('Jitendra Kumar')))


