from typing import Optional
import json
import requests
from .constants import *
import iitkgp_erp_login.erp as erp

from .parse import parse_prof_raw_data, ProfData, parse_department_timetable


def get_session(creds: Optional[erp.ErpCreds] = None) -> requests.Session:
    """Logs into ERP and returns a session"""
    session = requests.Session()
    erp.login(
        headers=DEFAULT_REQUEST_HEADERS,
        session=session,
        LOGGING=True,
        SESSION_STORAGE_FILE=".session",
        ERPCREDS=creds,
    )

    return session


ProfsList = dict[str, list[ProfData]]


def get_profs(session: requests.Session) -> ProfsList:
    """Fetches a list of department-wise professors from the IITKGP Website.
    Returns a dict where the key is the department code and the value is a list of `ProfData` dicts.
    """
    """
        Note:

        If a prof teaches subjects from other departments,
        it's not a good idea to add directly from the table.
        Instead, we try to find it from IIT KGP website. If
        not found, we'll add it from out data of the subject.
    """

    start = 0  # Start index for the current page
    more_pages = True  # Flag to indicate if there are more pages to fetch
    draw = 1  # The page number to be fetched

    profs_by_dept: ProfsList = {}
    for dept_code in DEPARTMENT_CODES:
        profs_by_dept[dept_code] = []

    while more_pages:
        # Payload for the faculty list post request
        payload = {
            "draw": draw,
            "columns[0][data]": "empname",
            "columns[1][data]": "department",
            "order[0][column]": "0",
            "order[0][dir]": "asc",
            "start": start,
            "length": 1000, # Fetch 1000 names at a time
            "search[value]": "",
            "search[regex]": "false",
            "lang": "en",
        }

        prof_resp = session.post(
            DEPT_FETCH_URL,
            headers=DEFAULT_REQUEST_HEADERS,
            data=payload,
        )
        profs_data = json.loads(prof_resp.content).get("aaData", [])

        for prof_raw_data in profs_data:
            dept_code, prof_data = parse_prof_raw_data(raw_data=prof_raw_data)
            profs_by_dept[dept_code].append(prof_data)

        if len(profs_data) < payload["length"]:
            more_pages = False
        else:
            start += payload["length"]
            draw += 1

    return profs_by_dept


def get_dept_timetable(session: requests.Session, dept_code: str):
    try:
        # Fetch timetable data
        response = session.get(TIMETABLE_FETCH_URL % dept_code)
        print(f"Fetched timetable for {dept_code}")
        html = response.content

        return parse_department_timetable(timetable_html=html)

    except Exception as err:
        print(f"Can't fetch {dept_code}")
        print(err)
        return []