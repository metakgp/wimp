#-*- coding: utf-8 -*-

from flask import Flask, render_template, request, abort
from main import get_table, get_times, get_dept, correct_spelling
import json
import os

app = Flask(__name__)

path = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(path, 'data/data.json')) as f:
    profs = list(set(json.load(f).keys()))
    profs.sort()


def fetch_results(prof):
    tb = [[['Monday']], [['Tuesday']], [['Wednesday']], [['Thursday']], [['Friday']]]
    times = ['', '8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '2 PM', '3 PM', '4 PM', '5 PM']

    prof = correct_spelling(prof)
    slot_data = get_times(prof)
    dept = get_dept(prof)

    if len(slot_data) == 0 and len(dept) == 0:
        abort(404)

    data = get_table(slot_data)

    for row in tb:
        for i in range(9):
            row.append([])

    for item in data:
        for venue in data[item]:
            if venue == '0':
                venue = 'In Dept'

            tb[int(item[0])][int(item[1])+1].append(venue)
        
    return [tb, times, dept, prof.title()]


@app.route('/', methods=['POST'])
def result():
    prof = request.form['prof']
    tb, times, dept, prof = fetch_results(prof)
    return render_template('main.html', name=prof, data=tb, times=times, profs=profs, dept=dept)


@app.errorhandler(404)         
def prof_not_found(error):
    return render_template('404.html'), 404


@app.route('/', methods=['GET'])
def main():
    prof = request.args.get('prof')

    if prof:
        tb, times, dept, prof = fetch_results(prof)
        return render_template('main.html', name=prof, data=tb, times=times, profs=profs, dept=dept)

    else:
        return render_template('main.html', profs=profs)      


if __name__ == '__main__':
    app.run(debug=True)
