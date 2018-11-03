#!/usr/bin/python3
#-*- coding: utf-8 -*-

from classes import *
import requests


profs = []


def populate():
    r = requests.get(PROFESSOR_FETCH_URL)
    data = r.json()

    for prof in data:
        name = prof['name']
        dept = prof['department']['code']

        profs.append(Professor(name, dept))


def main():
    populate()

    tb = TimeTable(profs[1])
    print(profs[1].name)
    print(tb)


if __name__ == '__main__':
    main()