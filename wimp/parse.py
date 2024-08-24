from bs4 import BeautifulSoup
from typing import TypedDict
import re

from .constants import SLOTS_COORDINATE_MAP


class ProfData(TypedDict):
    name: str
    """The name of the professor."""
    dept_code: str
    """The department code. (e.g., `EC`, `CS`, `BT`)"""
    department: str
    """The full department name of the professor."""
    profile_url: str
    """A URL to the professor's profile on the IITKGP website."""


def sanitize_name(name: str) -> str:
    """Used to sanitize a professor's name so that names from different sources match.
    1. Removes leading and trailing whitespaces.
    2. Replaces series of multiple spaces by a single one because yes that can sometimes happens. (Also replaces special whitespace characters by a normal space ` `)
    3. Writes the name in title case (i.e., only the first letter of each word is capitalized) because yes sometimes the name is written in full caps for no reason. Sorry if your name is DeNiro or DiNozzo or something, but you will have to take that up with ERP. Cool name, btw.
    """
    return " ".join(name.split()).title()


def parse_prof_raw_data(raw_data: list) -> ProfData:
    """Parses the raw data returned by the faculty list endpoint."""
    # empname is an html anchor tag with the URL to the prof's page and the professor's name in the description
    name_anchor = BeautifulSoup(raw_data.get("empname", ""), "lxml").find("a")
    department = raw_data.get("department", "N/A")

    # Get the href from the empname (url to the prof's website)
    profile_url = name_anchor.attrs["href"].strip()

    # Get department code form url
    dept_code = re.findall(r"department/(.+?)/", profile_url)[0]

    # Get the prof's name
    prof_name = sanitize_name(name_anchor.text if name_anchor.text else "Unknown")

    return {
        "name": prof_name,
        "department": department,
        "dept_code": dept_code,
        "profile_url": profile_url,
    }


class CourseTimetable(TypedDict):
    """Information for a particular course in the department timetable."""

    code: str
    """The course code."""
    course_name: str
    """The full course name."""
    professors: list[str]
    """Names of the professors teaching the course."""
    slots: list[str]
    """Time slots for the course."""
    rooms: list[str]
    """The rooms in which the course is taught."""


def parse_department_timetable(
    timetable_html: str, exclude_empties: bool = True
) -> list[CourseTimetable]:
    """Parses the department timetable HTML.
    If `exclude_empties` is set to True (default), all courses with no slot mentioned will be excluded (as it is useless for wimp)
    """
    soup = BeautifulSoup(timetable_html, "lxml")
    table = soup.find_all("table")[4]

    table_data: list[CourseTimetable] = []

    for row in BeautifulSoup(str(table), "lxml")("tr")[2:]:
        # Ignore the first two rows - title and heading
        columns = [cell.text for cell in row("td")]

        # Also ignore rows of less than 7 columns
        if len(columns) == 7:
            table_data.append(
                {
                    "code": columns[0].strip(),
                    "course_name": columns[1].strip(),
                    "professors": [
                        sanitize_name(name)
                        for name in columns[2].split(",")
                        if name.strip() != ""
                    ],
                    "slots": [
                        slot.strip()
                        for slot in columns[5].split(",")
                        if slot.strip() != ""
                    ],
                    "rooms": [
                        room.strip()
                        for room in columns[6].split(",")
                        if room.strip() != ""
                    ],
                }
            )

    return [
        course
        for course in table_data
        if len(course["slots"]) > 0 or not exclude_empties
    ]


def get_slot_coordinates(slot: str) -> list[tuple[int, int]]:
    """Returns a list of coordinates for a given central timetable slot.
    Sometimes subsections of a slot are mentioned. For example, the slot `D4` has four one-hour slots and they can be separately mentioned as `D41`, `D42` etc.
    This function returns a list of coordinates. If a subsection is mentioned, only that slot is returned. If only the slot name is mentioned, all slot coordinates are returned.
    """
    slot_name = slot[:2]
    slot_subsection = slot[2] if len(slot) > 2 else None

    slot_coords = SLOTS_COORDINATE_MAP[slot_name]

    return [slot_coords[int(slot_subsection) - 1]] if slot_subsection else slot_coords
