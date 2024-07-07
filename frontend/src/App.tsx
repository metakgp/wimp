import React from "react";
import Footer from "./components/Footer";
import "./App.css";
import { SparklesPreview } from "./components/UI/SparklesPreview";
import SearchBar from "./components/SearchBar";
//import DisplayData from "./components/DisplayData";

const App: React.FC = () => {
  return (
    <>
      <div className="App">
        <SparklesPreview />
        <div className="search-bar-container">
          <SearchBar />
        </div>
        <Footer />
      </div>
    </>
  );
};

export default App;
