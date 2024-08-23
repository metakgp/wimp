from typing import TypedDict, Literal
import Levenshtein as levenshtein

from .parse import get_slot_coordinates, ProfData, CourseTimetable


class ProfCourseTimetable(TypedDict):
    """A particular professor's particular course's schedule. Includes the course code, name, and list of slots and rooms where it is taught."""

    course_code: str
    course_name: str
    slots: list[tuple[int, int]]
    """Time slots for the course as coordinates in the central timetable. See `SLOTS_COORDINATE_MAP` in `wimp/constants.py` for more information."""
    rooms: list[str]
    """The rooms/locations where this course is taught."""


class ProfTimetable(TypedDict):
    prof: ProfData
    timetable: list[ProfCourseTimetable]


class Inaccuracy(TypedDict):
    """A potential inaccuracy in the timetable due to a mistake in the ERP."""

    reason: Literal["MULTINAME", "TYPO"]
    """The reason for the inaccuracy.
    - `MULTINAME`: Multiple professors have the same name.
    - `TYPO`: The name has a typo (i.e, did not match with the name in the faculty directory)
    This is a list since `TYPO` and `MULTINAME` together is theoretically possible. This is scary.
    """
    solution: list[Literal["DEP_PRIORITY", "FUZZY_SEARCH", "SKIP"]]
    """How the inaccuracy was accounted for (may not be correct).
    - `DEP_PRIORITY`: The course department matched with only one of the professors and was given priority.
    - `SKIP`: No reliable solution was found and was skipped.
    - `FUZZY_SEARCH`: Fuzzy search was used to match names with typos.

    This is a list since `TYPO` and `MULTINAME` together is theoretically possible.
    """
    context_course: CourseTimetable
    """The course that that has this inaccuracy."""
    context_profs: list[ProfData]
    """List of professors that may be related to this inaccuracy (e.g, the names of the professors matching the fuzzy search or the list of professors with the same name)."""


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


def handle_multiname(prof_teaching: str, matching_profs: list[ProfTimetable], dept_code: str, course_tt: CourseTimetable):
    """Handles the case in which multiple professors have the same name."""
    print(
        f"{len(matching_profs)} professors with the name {prof_teaching} found, giving priority to the course department {dept_code} (if possible)."
    )

    same_dep_profs = [
        i
        for (i, prof) in enumerate(matching_profs)
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
        matching_profs[same_dep_profs[0]]["timetable"].append(
            build_prof_course_timetable(course_tt=course_tt)
        )
    # Case 4: Multiple prof's department matches with that of the course. This means there are multiple professors with the same name in the same department. Give up and cry.
    else:
        print(
            f"The course department matches with {len(same_dep_profs)} profs. Giving up (and also crying)."
        )

def handle_typo(prof_teaching: str, prof_map: dict[str, list[ProfTimetable]], course_tt: CourseTimetable, dept_code: str):
    """Handles the case where there is a typo in the professor's name."""
    print(
        f"No match found for {prof_teaching} in the faculty directory. Using fuzzy search (yes)."
    )

    # Most typos are due to missing a single character or due to writing `First Last` as `Firstlast`. Yes that last one also happens.
    # In this case use a fuzzy search (idk what I am doing at this point)
    # TODO: Again, add this as a potential inaccuracy. Also log a summary of these inaccuracies so a maintainer can take conscious decisions.

    fuzzy_matches = [
        (prof_name, levenshtein.distance(prof_name, prof_teaching))
        for prof_name in prof_map.keys()
        if levenshtein.distance(prof_name, prof_teaching) <= 2
    ]
    if len(fuzzy_matches) > 0:
        print(
            f"Found the following fuzzy matches: {', '.join([f'{match[0]} ({match[1]})' for match in fuzzy_matches])}"
        )

        # Get the match with the lowest Levenshtein distance
        fuzzy_matches.sort(key=lambda x: x[1])
        match_name = fuzzy_matches[0][0]

        print(
            f"Using {match_name} because it has the lowest distance and I am lazy (and also because there is probably only one match)."
        )

        matching_profs = prof_map[match_name]

        # Case 1: Unique professor name
        if len(matching_profs) == 1:
            matching_profs[0]["timetable"].append(
                build_prof_course_timetable(course_tt=course_tt)
            )
        # Multiple professors with the same name (I seriously hope this doesn't happen!)
        else:
            handle_multiname(prof_teaching, matching_profs, dept_code, course_tt)

    else:
        print("No fuzzy matches found.")

def build_prof_timetables(
    profs: list[ProfData], dept_timetables: dict[str, list[CourseTimetable]]
) -> list[ProfTimetable]:
    """Builds the timetables for all the professors.

    Since the department timetable only mentions the professor's name, there is no way to accurately know which professor teaches the course if two have the same name. To handle these cases the following logic is used:
    1. Each course is parsed and assigned to its professor's timetable.
    2. If the professor is unique, the course is assigned to that professor.
    3. If there are multiple professors with the same name, the course is assigned to the professor within the department offering the course.
    4. If multiple professors from the same department share a name, cry.
    5. If the professors name has a typo (missing a character etc., yes this can happen), a fuzzy search is done and the closest name (<= 2 Levenshtein distance) is used, if there is a match.
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
                        handle_multiname(prof_teaching, matching_profs, dept_code, course_tt)

                else:
                    # Yes, _even this_ can happen. This is usually due to a typo. I want to cry.
                    handle_typo(prof_teaching, prof_map, course_tt, dept_code)

    prof_timetables: list[ProfTimetable] = []
    for prof_name in prof_map:
        prof_timetables.extend(prof_map[prof_name])

    return prof_timetables
