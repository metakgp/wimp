import Fuse from "fuse.js";

import RAW_DATA from "../../../data/data.json";

export interface IProfData {
	name: string;
	dept_code: string;
	department: string;
	profile_url: string;
}

export interface IProfCourseTimetable {
	course_code: string;
	course_name: string;
	/** This is an array of tuples where the first coordinate is the day index and the second is the hour (slot) index */
	slots: number[][];
	rooms: string[];
}

export interface IProfTimetable {
	prof: IProfData;
	timetable: IProfCourseTimetable[];
}

export const TIMETABLES: IProfTimetable[] = RAW_DATA;

export function findProf(name: string, limit: number = 5): IProfTimetable[] {
	const fuse = new Fuse(TIMETABLES, {
		includeScore: true,
		threshold: 0.2,
		isCaseSensitive: false,
		keys: ["prof.name"],
	});

	const matches = fuse.search(name).slice(0, limit + 1);

	return matches
		.sort((a, b) => a.score! - b.score!)
		.map((record) => record.item);
}

export type SlotInfo = { occupied: false } | {
  occupied: true;
  courses: {
    course_code: string;
    course_name: string;
    rooms: string[];
  }[];
};
export function getTimeSlotInfo(
	timetable: IProfTimetable,
	searchSlot: [number, number]
): SlotInfo {
	const slotCourses = timetable.timetable.filter((course) => {
		return course.slots.some((course_slot) =>
			course_slot.every(
				(value, index) => value === searchSlot[index]
			)
		);
	});

	if (slotCourses.length > 0) {
		return {
			occupied: true,
			courses: slotCourses.map((course) => {
				return {
					course_code: course.course_code,
					course_name: course.course_name,
					rooms: course.rooms,
				};
			}),
		};
	} else {
		return {
			occupied: false,
		};
	}
}
