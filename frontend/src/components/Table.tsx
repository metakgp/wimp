import { useState } from "react";
import SearchBar from "./SearchBar";
import "../index.css";

import { getTimeSlotInfo, IProfTimetable } from "../util/data";

function Table() {
  const [selectedProfessor, setSelectedProfessor] =
    useState<IProfTimetable | null>(null);
  const hours = [
    "8am",
    "9am",
    "10am",
    "11am",
    "12pm",
    "2pm",
    "3pm",
    "4pm",
    "5pm",
    "6pm",
  ];
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

  const onSelectProf = (timetable: IProfTimetable) => {
    setSelectedProfessor(timetable);
  };

  return (
    <div className="search-results">
      <SearchBar onSelectProfessor={onSelectProf} />

      {selectedProfessor && (
        <div className="table-container">
          <div className="table-caption">
            <span>
              <a href={`${selectedProfessor.prof.profile_url}`} target="_blank">
                {selectedProfessor.prof.name}
              </a>
            </span>
            <span className="dept space">|</span>
            <span className="dept">{selectedProfessor.prof.dept_code}</span>
          </div>
          <div className="time-table">
            <table className="table">
              <thead className="thead">
                <tr>
                  <th></th>
                  {hours.map((hour, hourIndex) => (
                    <th key={hourIndex}>{hour}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {days.map((day, dayIndex) => (
                  <tr key={dayIndex}>
                    <td>{day}</td>
                    {hours.map((_, hourIndex) => {
                      const timeslotInfo = getTimeSlotInfo(selectedProfessor, [
                        dayIndex,
                        hourIndex,
                      ]);

                      return timeslotInfo.occupied ? (
                        <td
                          key={`${dayIndex}-${hourIndex}`}
                          className="tt-cell"
                        >
                          {timeslotInfo.courses.map((course) => (
                            <div
                              key={course.course_code}
                              className="tt-cell-content"
                              title={course.course_name}
                            >
                              <p className="room">
                                {course.rooms.length > 0
                                  ? course.rooms.join(", ")
                                  : "N/A"}
                              </p>
                              <p className="course-code">
                                ({course.course_code})
                              </p>
                            </div>
                          ))}
                        </td>
                      ) : (
                        <td
                          key={`${dayIndex}-${hourIndex}`}
                          className="tt-cell"
                        >
                          <div className="tt-cell-content"></div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default Table;
