#!/usr/bin/python3
#-*- coding: utf-8 -*-

from classes import FacultyMember, Department, TT, Subject
import requests


FACULTY_FETCH_URL = 'https://hercules-10496.herokuapp.com/api/v1/faculty/info/all'
TIMETABLE_FETCH_URL = 'https://hercules-10496.herokuapp.com/api/v1/faculty/timetable'

def fetch_faculty():
    """Returns a list of all the faculty members."""

    # Fetch the data from hercules
    r = requests.get(FACULTY_FETCH_URL)
    if r.status_code != 200:
        return None # TODO: raise better exception

    # Process response
    data = r.json() 
    
    faculty = []
    for fm in data:
        # Decode data into objects
        new_faculty_member = FacultyMember(**fm)
        faculty.append(new_faculty_member)

    return faculty

def fetch_faculty_timetable(fm):
    """Returns the weekly timetable of the given faculty member."""

    # Fetch the data from hercules
    params = dict(name=fm.name, dept=fm.department.code)
    r = requests.get(TIMETABLE_FETCH_URL, params=params)
    if r.status_code != 200:
        print("unable to fetch timetable")
        return None # TODO: raise better exception

    # Process response
    data = r.json() # TODO: handle possible exceptions

    # Initialise an empty timetable
    timetable = TT()

     # Iterate over each day and the daily schedule
    for day, schedule in data.items():
        # Iterate over daily schedule
        if schedule is None:
            continue
    
        for s in schedule: 
            # Decode subject into an object
            new_subject = Subject(**s)
            timetable[day].append(new_subject)

    return timetable

def main():
    # faculty = fetch_faculty()
    fm = FacultyMember(name="Pratima Panigrahi", department={"name":"Mathematics", "code":"MA"})
    timetable = fetch_faculty_timetable(fm)
    print(timetable)

if __name__ == '__main__':
    main()