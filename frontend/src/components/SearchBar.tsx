import React, { FormEvent, useState } from "react";
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

  const onSubmitForm = (e: FormEvent<HTMLFormElement>) => {
    // Select the top option in the list if enter is pressed
    e.preventDefault();

    if (displayedProfs.length > 0) {
      setSearchName(displayedProfs[0].prof.name);
      onSelectProfessor(displayedProfs[0]);
      setdropdownVisibility(false);
    }
  }

  return (
    <form className="search-bar-container" onSubmit={onSubmitForm}>
      <div className="input-wrapper">
        <FaSearch id="search-icon" />
        <input
          className="input"
          type="text"
          placeholder="Who are you looking for?"
          value={searchName}
          autoFocus={true}
          onChange={(e) => handleChange(e.target.value)}
        />
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
    </form>
  );
};

export default SearchBar;