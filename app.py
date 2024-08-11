#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import json
import os
import itertools
from flask import Flask, abort, render_template, request
from werkzeug.exceptions import BadRequest
from requests.structures import CaseInsensitiveDict

app = Flask(__name__)

# Determine the absolute path of the current file's directory
path = os.path.abspath(os.path.dirname(__file__))

# Load the professor data from a JSON file and sort the professor names
with open(os.path.join(path, "data/data.json")) as f:
    profs_dict = json.load(f)
    profs = list(set(profs_dict.keys()))
    profs.sort()

# Define a constant for the timetable key used in the data
TIMETABLE_KEY = 'timetable'

# Basic spelling corrector class for correcting professor names
class SpellingCorrector:
    def __init__(self, word_list):
        self.words = word_list
    
    def correction(self, word):
        # Return the closest match based on the first letter of the word
        for w in self.words:
            if w.lower().startswith(word.lower()[0]):
                return w
        return word

# Function to get the timetable details for a professor
def get_times(prof_name):
    data = CaseInsensitiveDict(profs_dict)
    result = []

    try:
        result = data[prof_name][TIMETABLE_KEY]
        if result:
            # Sort and remove duplicates from the timetable slots
            result.sort()
            result = list(result for result, _ in itertools.groupby(result))
    except KeyError:
        pass

    return result

# Function to correct the spelling of the professor's name if needed
def correct_spelling(prof_name):
    prof_names = profs_dict.keys()

    if prof_name not in prof_names:
        corrector = SpellingCorrector(prof_names)
        return corrector.correction(prof_name)

    return prof_name

# Function to get an attribute (like department or website) for a professor
def get_attr(prof_name, key):
    data = CaseInsensitiveDict(profs_dict)
    result = ""

    try:
        result = data[prof_name][key]
    except KeyError:
        pass

    return result

# Function to process the timetable details and map times to venues
def get_table(details):
    # Initialize an empty timetable dictionary with keys for each time slot
    tb = {f"{i}{j}": [] for i in range(5) for j in range(9)}

    for times, venues in details:
        # Ensure times and venues are lists
        if not isinstance(times, list) or not isinstance(venues, list):
            continue

        # Clean up and remove empty venues
        venues = set(v.strip() for v in venues if v)

        # Process each time slot and assign venues
        for time in times:
            if time:  # Ensure time is not empty
                tb[time] = venues

    return tb

# Function to fetch the results for a professor's timetable
def fetch_results(prof):
    # Initialize the timetable structure with days and time slots
    tb = [[["Monday"]], [["Tuesday"]], [["Wednesday"]], [["Thursday"]], [["Friday"]]]
    times = [
        "",
        "8 AM",
        "9 AM",
        "10 AM",
        "11 AM",
        "12 PM",
        "2 PM",
        "3 PM",
        "4 PM",
        "5 PM",
    ]

    # Correct the spelling of the professor's name if needed
    prof = correct_spelling(prof)
    # Get the timetable data, department, and website for the professor
    slot_data = get_times(prof)
    dept = get_attr(prof, "dept")
    website = get_attr(prof, "website")

    # If no data is found, return a 404 error
    if len(slot_data) == 0 and len(dept) == 0:
        abort(404)

    # Process the slot data into the timetable
    data = get_table(slot_data)

    # Initialize the timetable with empty slots
    for row in tb:
        for i in range(9):
            row.append([])

    # Fill the timetable with venues based on the time slots
    for item in data:
        for venue in data[item]:
            if venue == "0":
                venue = "In Dept"
            if venue:  # Ensure the venue is not empty
                tb[int(item[0])][int(item[1]) + 1].append(venue)

    # Return the processed timetable along with other details
    return [tb, times, dept, website, prof.title()]

# Route to handle form submission via POST and render the results
@app.route("/", methods=["POST"])
def result():
    prof = request.form["prof"]
    tb, times, dept, website, prof = fetch_results(prof)
    return render_template(
        "main.html",
        name=prof,
        website=website,
        data=tb,
        times=times,
        profs=profs,
        dept=dept,
        error=False,
    )

# Error handler for 404 - professor not found
@app.errorhandler(404)
def prof_not_found(error):
    form = dict(request.form)
    if form.get("prof") is None and request.path != "/favicon.ico":
        raise BadRequest()
    
    prof = form.get("prof")
    return render_template("main.html", error=True, name=prof), 404

# Route to handle GET requests and display the main page or results
@app.route("/", methods=["GET"])
def main():
    prof = request.args.get("prof")

    if prof:
        tb, times, dept, website, prof = fetch_results(prof)
        return render_template(
            "main.html",
            name=prof,
            website=website,
            data=tb,
            times=times,
            profs=profs,
            dept=dept,
            error=False,
        )

    else:
        return render_template("main.html", profs=profs)

if __name__ == "__main__":
    app.run()
