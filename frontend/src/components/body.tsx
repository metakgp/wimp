import React from "react";
import doodleImage from "../assets/doodle.png";
import logo from "../assets/logo.png";
import "./body.css";
const Body: React.FC = () => {
  return (
    <>
      <div className="main">
        <div>
          <img
            src={logo}
            alt="MetaKGPlogo"
            style={{ marginBottom: "-70px" }}
            className="logo"
          />
          <h1>Where Is My Prof?</h1>
          <img
            src={doodleImage}
            style={{ marginTop: "-48px", width: "40%" }}
            alt="Doodle"
          />
        </div>
        <div>
          <p style={{ margin: "0 auto", textAlign: "left", width: "70%" }}>
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
