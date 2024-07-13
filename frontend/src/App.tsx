import React from "react";
import Footer from "./components/Footer";
import "./App.css";

import Body from "./components/body";
import Table from "./components/table";

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
