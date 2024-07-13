import React, { useState } from "react";
import { FaSearch } from "react-icons/fa";
import Records from "../../../data/converted_data.json";
import "./searchbar.css";

interface SearchBarProps {
  onSelectProfessor: (profName: string) => void; // Callback to select professor
}

const SearchBar: React.FC<SearchBarProps> = ({ onSelectProfessor }) => {
  const [input, setInput] = useState<string>("");

  const handleChange = (input: string) => {
    setInput(input);
  };

  const onSearch = (input: string) => {
    setInput(input);
    onSelectProfessor(input); // Call the parent component's onSelectProfessor
  };

  return (
    <>
      <div className="search-bar-container">
        <div className="input-wrapper">
          <div>
            <FaSearch id="search-icon" />
            <input
              type="text"
              placeholder="Who are you looking for?"
              value={input}
              onChange={(e) => handleChange(e.target.value)}
            />
          </div>
        </div>
        <div className="dropdown">
          {Records.filter((record) => {
            const searchTerm = input.toLowerCase();
            const name = record.name.toLowerCase();

            return (
              searchTerm && name.startsWith(searchTerm) && name !== searchTerm
            );
          }).map((record) => (
            <div
              onClick={() => onSearch(record.name)}
              className="dropdown-row"
              key={record.name}
            >
              {record.name}
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default SearchBar;
