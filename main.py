import wimp
from multiprocessing.pool import ThreadPool

if __name__ == "__main__":
    session = wimp.get_session()
    profs_by_dept = wimp.get_profs(session)

    # Concurrently fetch all department timetables
    fetch_pool = ThreadPool()
    dept_timetables = fetch_pool.starmap(
        wimp.get_dept_timetable, [(session, code) for code in wimp.DEPARTMENT_CODES]
    )