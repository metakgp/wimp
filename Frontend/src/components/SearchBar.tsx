import "./searchbar.css";
import { useState } from "react";
import { FaSearch } from "react-icons/fa";
import Records from "../../../data/converted_data.json";

function SearchBar() {
  const [input, setInput] = useState("");
  //const fetchData = (value) => {};

  const handleChange = (input: string) => {
    setInput(input);
  };
  const onSearch = (input: string) => {
    // if (e.key === "Enter") {
    setInput(input);
    // Perform your action here, e.g., fetch data
    console.log("Enter key pressed");
    //fetchData(input);
    // }
  };
  return (
    <>
      <div className="input-wrapper">
        <div>
          <FaSearch id="search-icon" />
          <input
            type="text"
            placeholder="Enter Professor's name"
            value={input}
            onChange={(e) => handleChange(e.target.value)}
            //onKeyDown={(e) => handleKeyDown(e)}
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
        }).map((record) => {
          return (
            <div
              onClick={() => onSearch(record.name)}
              className="dropdown-row"
              key={record.name}
            >
              {record.name}
            </div>
          );
        })}
      </div>
    </>
  );
}
export default SearchBar;
