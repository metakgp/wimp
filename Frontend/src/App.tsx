import React from "react";
import ProfessorList from "./components/ProfessorList";
import Footer from "./components/Footer";
import "./App.css";

const App: React.FC = () => {
  return (
    <div className="App">
      <ProfessorList />
    </div>
  );
};
export default App;
