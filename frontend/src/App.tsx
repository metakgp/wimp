import React from "react";
import Footer from "./components/Footer";
import "./index.css";

import Body from "./components/Body";
import Table from "./components/Table";

const App: React.FC = () => {
  return (
    <>
      <div className="App">
        <Body />
        <Table />
        <Footer />
      </div>
    </>
  );
};

export default App;