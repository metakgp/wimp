from bs4 import BeautifulSoup
from typing import TypedDict
import re

class ProfData(TypedDict):
    name: str
    """The name of the professor."""
    department: str
    """The full department name of the professor."""
    profile_url: str
    """A URL to the professor's profile on the IITKGP website."""


def parse_prof_raw_data(raw_data: list) -> tuple[str, ProfData]:
    """Parses the raw data returned by the faculty list endpoint."""
    # empname is an html anchor tag with the URL to the prof's page and the professor's name in the description
    name_anchor: str = raw_data.get("empname", "")
    department = raw_data.get("department", "N/A")

    # Get the href from the empname (url to the prof's website)
    profile_url = name_anchor.split(" ")[1].split("href=")[1]

    # Get department code form url
    dept_code = re.findall(r"department/(.+?)/", profile_url)[0]

    # Get the prof's name
    emp_name_match = re.findall(r">(.+?)<", name_anchor)
    prof_name = emp_name_match[0].replace("  ", "") if emp_name_match else "Unknown"

    return (
        dept_code,
        {"name": prof_name, "department": department, "profile_url": profile_url},
    )

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

def parse_department_timetable(timetable_html: str, exclude_empties: bool = True) -> list[CourseTimetable]:
    """Parses the department timetable HTML.
    If `exclude_empties` is set to True (default), all courses with no room or no slot mention will be excluded (as it is useless for wimp)
    """
    soup = BeautifulSoup(timetable_html, "lxml")
    table = soup.find_all("table")[4]

    table_data: list[CourseTimetable] = []

    for row in BeautifulSoup(str(table), "lxml")("tr")[2:]:
        # Ignore the first two rows - title and heading
        columns = [cell.text for cell in row("td")]

        # Also ignore rows of less than 7 columns
        if len(columns) == 7:
            table_data.append({
                "code": columns[0].strip(),
                "course_name": columns[1].strip(),
                "professors": [name.strip() for name in columns[2].split(",") if name.strip() != ""],
                "slots": [slot.strip() for slot in columns[5].split(",") if slot.strip() != ""],
                "rooms": [room.strip() for room in columns[6].split(",") if room.strip() != ""]
            })

    return [
        course for course in table_data if
        (len(course["slots"]) > 0 and len(course["rooms"]) > 0) or
        not exclude_empties
    ]