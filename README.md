![Compatibility](https://img.shields.io/badge/compatible%20with-python3.6.x-blue.svg)
# WIMP - Where Is My Prof?

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)
![Screenshot](https://raw.githubusercontent.com/metakgp/wimp/master/static/screenshot.png)

Alwin is a wimpy kid. What? Is he lazy? Not at all! He always asks me, 'Where is my Prof?'. He is in search of his project and sick of waiting for hours in front of his Prof's office. Boom! He got an idea. He started to search the Prof's timetable and decided to meet him after his class. He went to ERP. Wow! What a beautiful place it is! He found the Prof's department and checked department time table, found out his slots, compared his slots with time and finally, he met him. But, alas! He was late. The Prof gave his project to another stud. Alwin asked him, 'Bro, how did you find him earlier?'. He replied, 'Use WIMP kid!'.

## Development

### Getting Valid JSESSIONID
1. Login to the ERP
2. Go to Academic -> Timetable -> Subject List with Timetable Slots
3. Open the browser console. Switch to the Network tab
4. Choose any department and wait for the time table to load
5. After the time table is loaded, check the Network tab for the `POST
   timetable_track.js ...` request. Select this request; switch to the Cookies
   tab and copy the `JSESSIONID` cookie value to your `.env` file
6. You can also add it using the following command for the current terminal session
    ```bash
    export JSESSIONID="[JSESSIONID FROM ERP]"
    ```
The JSESSIONID is only used to update the data using main.py and not for running the app.py.

### Host machine

```sh
git clone https://github.com/metakgp/wimp.git
cd wimp
sudo pip install pipenv
pipenv install && pipenv shell # loads .env file variables, install dependencies
python main.py # To populate data
python app.py # Locate your browser to the local address
```

### Docker container

```sh
git clone https://github.com/themousepotato/wimp.git
cd wimp
docker build -t wimp .
docker run -p 5000:5000 wimp
```

### Pretty printing `data.json`

You can use any JSON utility that is installed on your computer.
[`jq`](https://stedolan.github.io/jq/) is recommended.

```sh
$ jq '' data/data.json > data/data2.json
$ mv data/data2.json data/data.json
```

## Wiki
We've a list of FAQ [here](https://github.com/metakgp/wimp/wiki/FAQ). If you've any queries, find the answer from there. If your question is not there, add it by yourself. We would love to answer.

## Contributions

PRs are most welcome!

[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)


## Maintainer

[Navaneeth Suresh](https://github.com/themousepotato) (@themousepotato on [metakgp Slack](https://slack.metakgp.org).)

