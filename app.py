#-*- coding: utf-8 -*-

from flask import Flask, render_template, request
from main import get_table, get_times
import json
import os

app = Flask(__name__)

path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(path, 'data/data.json')) as f:
    profs = list(set(json.load(f).keys()))
    profs.sort()

def fetch_results(prof):
    tb = [['Monday'], ['Tuesday'], ['Wednesday'], ['Thursday'], ['Friday']]
    times = ['', '8 AM - 9 AM', '9 AM - 10 AM', '10 AM - 11 AM', '11 AM - 12 AM', '12 PM - 1 PM', '2 PM - 3 PM', '3 PM - 4PM', '4 PM - 5 PM', '5 PM - 6 PM']

    data = get_table(get_times(prof))

    for row in tb:
        for i in range(9):
            row.append('')

    for item in data:
        for venue in data[item]:
            if venue != '0':
                tb[int(item[0])][int(item[1])+1] +=  venue + " | "
        
        tb[int(item[0])][int(item[1])+1] = tb[int(item[0])][int(item[1])+1][:-2]

    return [tb, times]

@app.route('/', methods=['POST'])
def result():
    prof = request.form['prof']
    tb, times = fetch_results(prof)
    return render_template('main.html', name=prof, data=tb, times=times, profs=profs)

@app.route('/', methods=['GET'])
def main():
    prof = request.args.get('prof')
    if prof:
        tb, times = fetch_results(prof)
        return render_template('main.html', name=prof, data=tb, times=times, profs=profs)
    else:
        return render_template('main.html', profs=profs)       

if __name__ == '__main__':
    app.run(debug=True)
