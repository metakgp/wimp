import React from "react";

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

interface ProfessorIDProps {
  professor: Professor;
}

const ProfessorID: React.FC<ProfessorIDProps> = ({ professor }) => {
  return (
    <div className="card mb-3">
      <div className="card-body">
        <h5 className="card-title">ID: {professor.id}</h5>
        <h6 className="card-subtitle mb-2 text-muted">
          Name: {professor.name}
        </h6>
        <h6 className="card-subtitle mb-2 text-muted">
          Department: {professor.department}
        </h6>
        <ul className="list-group">
          {professor.timetable.map((slot, idx) => (
            <li key={idx} className="list-group-item">
              {slot.day} - {slot.time} : {slot.subject}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ProfessorID;
