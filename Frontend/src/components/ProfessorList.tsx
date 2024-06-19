import React, { useEffect, useState } from "react";
import ProfessorID from "./ProfessorID";

interface TimetableSlot {
  day: string;
  time: string;
  subject: string;
}

interface Professor {
  id: string;
  name: string;
  department: string;
  timetable: TimetableSlot[];
}

const ProfessorList: React.FC = () => {
  const [professors, setProfessors] = useState<Professor[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/timetable")
      .then((response) => response.json())
      .then((data) => {
        setProfessors(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Loading data...</p>;
  }

  return (
    <div className="container">
      <h1>Where is My Professor?</h1>
      {professors.length > 0 ? (
        professors.map((prof, index) => (
          <ProfessorID key={index} professor={prof} />
        ))
      ) : (
        <p>No data available.</p>
      )}
    </div>
  );
};

export default ProfessorList;
