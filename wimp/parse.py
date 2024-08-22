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
