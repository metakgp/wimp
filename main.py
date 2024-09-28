import sys
import wimp
import json
from multiprocessing.pool import ThreadPool

if __name__ == "__main__":
    # Get profs list from iitkgp.ac.in
    print("[~]", "Fetching prof list from iitkgp.ac.in")
    profs = wimp.get_profs()
    print("[+]", "Successfully fetched prof list from iitkgp.ac.in")

    # Generate session
    print("[~]", "Generating ERP session")
    if sys.argv[1] == 'auto':
        import erpcreds
        session = wimp.get_session(erpcreds, 2)
    else:
        session = wimp.get_session()
    print("[+]", "Successfully generated ERP session")

    # Concurrently fetch all department timetables
    print("[~]", "Concurrently fetching timetable of all departments")
    fetch_pool = ThreadPool()
    dept_timetables_list = fetch_pool.starmap(
        wimp.get_dept_timetable, [(session, code) for code in wimp.DEPARTMENT_CODES]
    )
    print("[+]", "Successfully fetched timetable of all departments")

    print("[~]", "Building timetables")
    timetables, inaccuracies = wimp.build_prof_timetables(
        profs, dept_timetables=dict(zip(wimp.DEPARTMENT_CODES, dept_timetables_list))
    )
    print("[~]", "Successfully built timetables")

    with open("data/data.json", "w") as data_file:
        json.dump(timetables, data_file, indent=2)

    with open("data/inaccuracies.json", "w") as inaccuracy_file:
        json.dump(inaccuracies, inaccuracy_file, indent=2)
