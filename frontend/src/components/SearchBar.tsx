import React, { useState } from "react";
import { FaSearch } from "react-icons/fa";
import Records from "../../../data/converted_data.json";
import "./searchbar.css";
import Fuse from "fuse.js";

const fuse = new Fuse(Records, {
  keys: ["name", "dept", "website", "timetable"],
});

interface SearchBarProps {
  onSelectProfessor: (profName: string) => void; // Callback to select professor
}

const SearchBar: React.FC<SearchBarProps> = ({ onSelectProfessor }) => {
  const [input, setInput] = useState<string>("");
  const [dropdownVisibility, setdropdownVisibility] = useState<boolean>(true);

  const handleChange = (input: string) => {
    setInput(input);
    input ? setdropdownVisibility(true) : setdropdownVisibility(false);
  };

  const results = fuse.search(input).slice(0, 4);
  const onSearch = (input: string) => {
    setInput(input);
    onSelectProfessor(input); // Call the parent component's onSelectProfessor
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
              value={input}
              onChange={(e) => handleChange(e.target.value)}
            />
          </div>
        </div>
        {dropdownVisibility && (
          <div className="dropdown">
            {results.map((record) => (
              <div
                onClick={() => onSearch(record.item.name)}
                className="dropdown-row"
                key={record.item.name}
              >
                {record.item.name} | {record.item.dept}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
};

export default SearchBar;
