import React, { useState } from "react";
import { FaSearch } from "react-icons/fa";
import { findProf } from "../util/data";
import "../index.css";

import { IProfTimetable } from "../util/data";

interface SearchBarProps {
  onSelectProfessor: (timetable: IProfTimetable) => void; // Callback to select professor
}

const SearchBar: React.FC<SearchBarProps> = ({ onSelectProfessor }) => {
  const [searchName, setSearchName] = useState<string>("");
  const [displayedProfs, setDisplayedProfs] = useState<IProfTimetable[]>([]);
  const [dropdownVisibility, setdropdownVisibility] = useState<boolean>(true);

  const handleChange = (input: string) => {
    setSearchName(input);
    setDisplayedProfs(findProf(input));
    input ? setdropdownVisibility(true) : setdropdownVisibility(false);
  };

  const onSelect = (timetable: IProfTimetable) => {
    setSearchName(timetable.prof.name);
    onSelectProfessor(timetable); // Call the parent component's onSelectProfessor
    setdropdownVisibility(false);
  };

  return (
    <>
      <div className="search-bar-container">
        <div className="input-wrapper">
          <div>
            <FaSearch id="search-icon" />
            <input
              className="input"
              type="text"
              placeholder="Who are you looking for?"
              value={searchName}
              onChange={(e) => handleChange(e.target.value)}
            />
          </div>
        </div>
        {dropdownVisibility && (
          <div className="dropdown">
            {displayedProfs.map((timetable) => (
              <div
                onClick={() => onSelect(timetable)}
                className="dropdown-row"
                key={timetable.prof.profile_url}
              >
                {timetable.prof.name} | {timetable.prof.dept_code}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
};

export default SearchBar;