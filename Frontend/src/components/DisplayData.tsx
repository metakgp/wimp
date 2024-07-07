import { useMemo } from "react";
import { useTable } from "react-table";
import data from "../../../data/converted_data.json";
import { COLUMNS } from "./columns";
import "./Table.css";

// Adjust COLUMNS if needed to match your data structure
export const BasicTable = () => {
    const columns = useMemo(
      () => COLUMNS.map((col) => ({ ...col, accessor: col.accessor as "email" })),
      []
    );

const BasicTable = () => {
  // Assuming data is structured correctly as per your JSON format
  const data = useMemo(() => {
    // Transform data into a format suitable for table rows
    return data.map((faculty) => {
      // Map timetable to create rows for each day and time slot
      const timetableRows = faculty.timetable.flatMap((daySlots) =>
        daySlots[0].map((dayIndex, timeSlotIndex) => ({
          day: dayIndex,
          timeSlot: timeSlotIndex,
          location: daySlots[1][timeSlotIndex], // Assuming this is the location information
        }))
      );

      // Flatten timetableRows with faculty information
      return timetableRows.map((row) => ({
        name: faculty.name,
        dept: faculty.dept,
        ...row,
      }));
    }).flat();
  }, []);

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable({ columns, data });

  return (
    <table {...getTableProps()} className="table">
      <thead>
        {headerGroups.map((headerGroup) => (
          <tr {...headerGroup.getHeaderGroupProps()}>
            {headerGroup.headers.map((column) => (
              <th {...column.getHeaderProps()}>{column.render("Header")}</th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody {...getTableBodyProps()}>
        {rows.map((row) => {
          prepareRow(row);
          return (
            <tr {...row.getRowProps()}>
              {row.cells.map((cell) => (
                <td {...cell.getCellProps()}>{cell.render("Cell")}</td>
              ))}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default BasicTable;