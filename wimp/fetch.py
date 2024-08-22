from typing import Optional
from bs4 import BeautifulSoup
import json
import requests
import constants
import iitkgp_erp_login.erp as erp

from .parse import parse_prof_raw_data, ProfData


def get_session(creds: Optional[erp.ErpCreds] = None) -> requests.Session:
    """Logs into ERP and returns a session"""
    session = requests.Session()
    erp.login(
        headers=constants.DEFAULT_REQUEST_HEADERS,
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

    start = 0  # Start index for pagination
    more_pages = True  # Flag to indicate if there are more pages to fetch
    draw = 1  # Counter for pagination requests

    profs_by_dept: ProfsList = {}
    for dept_code in constants.DEPARTMENT_CODES:
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
            "length": 1000,
            "search[value]": "",
            "search[regex]": "false",
            "lang": "en",
        }

        prof_resp = session.post(
            constants.DEPT_FETCH_URL,
            headers=constants.DEFAULT_REQUEST_HEADERS,
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


def get_dept_timetable(session: requests.Session, dept: str):
    try:
        # Fetch timetable data
        response = session.get(constants.TIMETABLE_FETCH_URL % dept)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        html = soup.find_all("table")[4]
        print(f"Fetched for {dept}")

    except Exception as err:
        print(f"Can't fetch {dept}")
        print(err)
        return []

    # Parse table data from the fetched HTML
    table_data = [
        [cell.text for cell in row("td")]
        for row in BeautifulSoup(str(html), "lxml")("tr")
    ]
    table_data = [
        {
            "slot": row[5].split(","),
            "prof_name_list": row[2].split(",s"),
            "room": row[6],
        }
        for row in table_data[2:]
        if len(row) == 7
    ]

    return table_data
