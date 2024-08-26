import wimp
import json
import erpcreds
from multiprocessing.pool import ThreadPool

if __name__ == "__main__":
    session = wimp.get_session(erpcreds)
    profs = wimp.get_profs(session)

    # Concurrently fetch all department timetables
    fetch_pool = ThreadPool()
    dept_timetables_list = fetch_pool.starmap(
        wimp.get_dept_timetable, [(session, code) for code in wimp.DEPARTMENT_CODES]
    )

    timetables, inaccuracies = wimp.build_prof_timetables(
        profs, dept_timetables=dict(zip(wimp.DEPARTMENT_CODES, dept_timetables_list))
    )

    with open("data/data.json", "w") as data_file:
        json.dump(timetables, data_file, indent=2)

    with open("data/inaccuracies.json", "w") as inaccuracy_file:
        json.dump(inaccuracies, inaccuracy_file, indent=2)
