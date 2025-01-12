import React from "react";
import doodleImage from "../assets/doodle-optimized.jpg";
import logo from "../assets/logo.png";
import "../index.css";
const Body: React.FC = () => {
  return (
    <>
      <div className="main">
        <div>
          <img
            src={logo}
            alt="MetaKGPlogo"
            className="logo"
          />
          <h1>Where Is My Prof?</h1>
          <img
            src={doodleImage}
            alt="Doodle"
            className="doodle"
          />
        </div>
        <div>
          <p>
            Start entering a professor's name in the text box. Select the
            professor from the list. The result will show the weekly timetable
            of the professor!
          </p>
        </div>
      </div>
    </>
  );
};

export default Body;