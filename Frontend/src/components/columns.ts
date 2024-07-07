import { days, timeSlots } from './constants'; // Assuming days and timeSlots are defined elsewhere

interface TimetableEntry {
  location: string; // Assuming the third element holds the location name
}

interface FacultyData {
  name: string;
  dept: string;
  website: string;
  timetable: TimetableEntry[][];
}

export const COLUMNS = [
  { Header: 'Day', accessor: 'day' }, // Placeholder for day information (not directly used)
  ...timeSlots.map((slot) => ({
    Header: slot,
    accessor: (row: FacultyData) => {
      // Access timetable data for the current row
      const timetable = row.timetable;
      // Extract day information from the first element of the first nested array
      const day = timetable?.[0]?.[0] ?? 0; // Default to 0 if data is missing

      // Check if data exists for this day and slot
      if (!timetable || !timetable[days.indexOf(day)]) {
        return '—'; // Display "-" if no data
      }

      const slotData = timetable[days.indexOf(day)][timeSlots.indexOf(slot)];
      return slotData ? slotData[2] : '—'; // Return location name or "-" if no data
    },
    // Option 1: Extract location name directly (simpler)
    Cell: ({ value }) => value, // Render the retrieved value (location name or "-")

    // Option 2: Customize Cell rendering (more flexible)
    // Cell: ({ value }) => {
    //   if (value && typeof value === 'object') {
    //     return value.location; // Render location if available
    //   } else {
    //     return value; // Render the original value ("—" or potentially other data)
    //   }
    // },
  })),
];
