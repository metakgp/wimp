from bs4 import BeautifulSoup
from typing import TypedDict, Literal
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
    name_anchor: str = raw_data.get("empname", "")
    department = raw_data.get("department", "N/A")

    # Get the href from the empname (url to the prof's website)
    profile_url = name_anchor.split(" ")[1].split("href=")[1]

    # Get department code form url
    dept_code = re.findall(r"department/(.+?)/", profile_url)[0]

    # Get the prof's name
    emp_name_match = re.findall(r">(.+?)<", name_anchor)
    prof_name = sanitize_name(
        emp_name_match[0].replace("  ", "") if emp_name_match else "Unknown"
    )

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


class ProfCourseTimetable(TypedDict):
    """A particular professor's particular course's schedule. Includes the course code, name, and list of slots and rooms where it is taught."""

    course_code: str
    course_name: str
    slots: list[tuple[int, int]]
    """Time slots for the course as coordinates in the central timetable. See `SLOTS_COORDINATE_MAP` in `wimp/constants.py` for more information."""
    rooms: list[str]
    """The rooms/locations where this course is taught."""


def get_slot_coordinates(slot: str) -> list[tuple[int, int]]:
    """Returns a list of coordinates for a given central timetable slot.
    Sometimes subsections of a slot are mentioned. For example, the slot `D4` has four one-hour slots and they can be separately mentioned as `D41`, `D42` etc.
    This function returns a list of coordinates. If a subsection is mentioned, only that slot is returned. If only the slot name is mentioned, all slot coordinates are returned.
    """
    slot_name = slot[:2]
    slot_subsection = slot[2] if len(slot) > 2 else None

    slot_coords = SLOTS_COORDINATE_MAP[slot_name]

    return [slot_coords[int(slot_subsection) - 1]] if slot_subsection else slot_coords


def build_prof_course_timetable(course_tt: CourseTimetable) -> ProfCourseTimetable:
    """Builds a `ProfCourseTimetable` from a `CourseTimetable`."""
    return {
        "course_code": course_tt["code"],
        "course_name": course_tt["course_name"],
        "slots": [
            coordinate
            for slot in course_tt["slots"]
            for coordinate in get_slot_coordinates(slot)
        ],
        "rooms": course_tt["rooms"],
    }


class ProfTimetable(TypedDict):
    prof: ProfData
    timetable: list[ProfCourseTimetable]


class Inaccuracy(TypedDict):
    """A potential inaccuracy in the timetable due to a mistake in the ERP."""
    reason: Literal['MULTINAME', 'TYPO']
    """The reason for the inaccuracy.
    - `MULTINAME`: Multiple professors have the same name.
    - `TYPO`: The name has a typo (i.e, did not match with the name in the faculty directory)
    """
    solution: Literal['DEP_PRIORITY', 'FUZZY_SEARCH', 'SKIP']
    """How the inaccuracy was accounted for (may not be correct).
    - `DEP_PRIORITY`: The course department matched with only one of the professors and was given priority.
    - `SKIP`: No reliable solution was found and was skipped.
    - `FUZZY_SEARCH`: Fuzzy search was used to match names with typos.
    """


def build_prof_timetables(
    profs: list[ProfData], dept_timetables: dict[str, list[CourseTimetable]]
) -> list[ProfTimetable]:
    """Builds the timetables for all the professors.

    Since the department timetable only mentions the professor's name, there is no way to accurately know which professor teaches the course if two have the same name. To handle these cases the following logic is used:
    1. Each course is parsed and assigned to its professor's timetable.
    2. If the professor is unique, the course is assigned to that professor.
    3. If there are multiple professors with the same name, the course is assigned to the professor within the department offering the course.
    4. If multiple professors from the same department share a name, cry.
    """

    # Create a map of professor's name to an array of their details (array since multiple can share a name)
    prof_map: dict[str, list[ProfTimetable]] = {}

    for prof in profs:
        # Since the final output is a list of professors and their timetables
        prof_tt: ProfTimetable = {"prof": prof, "timetable": []}

        if prof["name"] in prof_map:
            prof_map[prof["name"]].append(prof_tt)
        else:
            prof_map[prof["name"]] = [prof_tt]

    # Iterate through all courses' timetables
    for dept_code in dept_timetables:
        for course_tt in dept_timetables[dept_code]:
            for prof_teaching in course_tt["professors"]:
                if prof_teaching in prof_map:
                    matching_profs = prof_map[prof_teaching]

                    # Case 1: Unique professor name
                    if len(matching_profs) == 1:
                        matching_profs[0]["timetable"].append(
                            build_prof_course_timetable(course_tt=course_tt)
                        )
                    # Multiple professors with the same name
                    else:
                        print(
                            f"{len(matching_profs)} professors with the name {prof_teaching} found, giving priority to the course department {dept_code} (if possible)."
                        )

                        same_dep_profs = [
                            prof
                            for prof in matching_profs
                            if prof["prof"]["dept_code"] == dept_code
                        ]

                        # Case 2: No profs match the department of the course. Give up.
                        if len(same_dep_profs) == 0:
                            print(
                                "The course department doesn't match with any of the profs. Giving up."
                            )
                        # Case 3: Only one prof's department matches with that of the course. Assign it but read with a grain of salt.
                        # TODO: In the future, add a field of possible inaccuracies that can be displayed on the frontend.
                        elif len(same_dep_profs) == 1:
                            print(
                                "The course department matches with one of the profs'. Assigning the course to that prof."
                            )
                        # Case 4: Multiple prof's department matches with that of the course. This means there are multiple professors with the same name in the same department. Give up and cry.
                        else:
                            print(
                                f"The course department matches with {len(same_dep_profs)} profs. Giving up (and also crying)."
                            )

                else:
                    # Yes, _even this_ can happen. This is usually due to a typo. I want to cry.
                    print(
                        f"No match found for {prof_teaching} in the faculty directory. Using fuzzy search."
                    )

                    # Most typos are due to missing a single character or due to writing `First Last` as `Firstlast`. Yes that last one also happens.
                    # In this case use a fuzzy search (idk what I am doing at this point)
                    # TODO: Again, add this as a potential inaccuracy. Also log a summary of these inaccuracies so a maintainer can take conscious decisions.

    prof_timetables: list[ProfTimetable] = []
    for prof_name in prof_map:
        prof_timetables.extend(prof_map[prof_name])

    return prof_timetables
