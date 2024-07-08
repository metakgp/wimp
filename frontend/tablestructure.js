document.addEventListener("DOMContentLoaded", function() {
    // Define the days and times
    var days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    var times = ['8am', '9am', '10am', '11am', '12pm', '2pm', '3pm', '4pm', '5pm'];

    var theadRow = document.querySelector('.thead-light tr');
    var tbody = document.getElementById('timetable-body');

    // Render times in thead
    times.forEach(function(time) {
        var th = document.createElement('th');
        th.textContent = time;
        theadRow.appendChild(th);
    });

    // Loop through days to create rows
    days.forEach(function(day) {
        var row = document.createElement('tr');
        var dayCell = document.createElement('td');
        dayCell.textContent = day;
        row.appendChild(dayCell);

        // Loop through times to create cells for each day
        times.forEach(function(time) {
            var cell = document.createElement('td');
            var dayIndex=days.indexOf(day);
            var timeIndex=times.indexOf(time);
            cell.id = dayIndex.toString()+timeIndex.toString();
            console.log(cell.id);
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });
});
