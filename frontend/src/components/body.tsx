import React from "react";
import doodleImage from "../assets/doodle.png";

const Body: React.FC = () => {
  return (
    <>
      <div className="main">
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <h1>MetaKGP - WIMP</h1>
          <h2>Where Is My Prof?</h2>
          <img src={doodleImage} style={{ width: "40%" }} alt="Doodle" />
        </div>
        <div>
          <p style={{ textAlign: "center" }}>
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
