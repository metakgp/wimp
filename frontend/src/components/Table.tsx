import { useState, useMemo, useCallback } from "react";
import data from "../../../data/converted_data.json";
import SearchBar from "./SearchBar";
import "../index.css";

interface Info {
  name: string;
  dept: string;
  website: string;
  timetable: string[][][];
}

function Table() {
  const profData: Info[] = data;
  const [selectedProfessor, setSelectedProfessor] = useState<Info | null>(null);
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

  // Function to select a professor by name
  const selectProfessorByName = (profName: string) => {
    const professor = profData.find((prof) => prof.name === profName);
    setSelectedProfessor(professor || null);
  };

  // Memoize timetable entries
  const memoizedTimetable = useMemo(() => {
    if (!selectedProfessor) return [];

    const memoizedEntries: [string[], string][] = [];
    selectedProfessor.timetable.forEach((entry) => {
      const [timeIndexes, classes] = entry;
      const memoizedTimeIndexes = timeIndexes.map(String);
      memoizedEntries.push([memoizedTimeIndexes, classes[0]]);
    });

    return memoizedEntries;
  }, [selectedProfessor]);

  // Memoize callback functions to avoid re-renders
  const isClassScheduled = useCallback(
    (dayIndex: number, hourIndex: number) => {
      if (!selectedProfessor) return false;

      return memoizedTimetable.some(([timeIndexes]) =>
        timeIndexes.includes(dayIndex.toString() + hourIndex.toString())
      );
    },
    [memoizedTimetable, selectedProfessor]
  );

  const getClassInfo = useCallback(
    (dayIndex: number, hourIndex: number) => {
      if (!selectedProfessor) return "-";

      const matchingEntries = memoizedTimetable.filter(([timeIndexes]) =>
        timeIndexes.includes(dayIndex.toString() + hourIndex.toString())
      );

      if (matchingEntries.length > 0) {
        const classes = matchingEntries
          .map(([_, classes]) => classes)
          .join(", ");
        return classes === "0" ? "In dept" : classes; // Render "In dept" for zeros
      } else {
        return "-";
      }
    },
    [memoizedTimetable, selectedProfessor]
  );

  return (
    <div className="search-results">
      <SearchBar onSelectProfessor={selectProfessorByName} />
      {selectedProfessor && (
        <div className="table-container">
          <div className="table-caption">
            <span>
              <a
                href={`${selectedProfessor.website}`}
                target="_blank"
              >
                {selectedProfessor.name}
              </a>
            </span>
            <span className="dept space">|</span>
            <span className="dept">{selectedProfessor.dept}
            </span>
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
                  {hours.map((_, hourIndex) => (
                    <td key={`${dayIndex}-${hourIndex}`}>
                      {isClassScheduled(dayIndex, hourIndex)
                        ? getClassInfo(dayIndex, hourIndex)
                        : "-"}
                    </td>
                  ))}
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