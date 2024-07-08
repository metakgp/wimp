function autocomplete(datalist, worker) {
    var processing = false;
    var nextQuery = null;
    var currentQuery = null;

    var prof_query = document.getElementById('prof_query');
    var suggestions = document.getElementById('suggestions');


    // fuzzy search
    worker.postMessage({type: 'data', data: datalist});

    worker.onmessage = function(results) {
        displayResult(results.data);

        processing = false;
        if (nextQuery !== null) {
            var query = nextQuery;
            nextQuery = null;
            search(query);
        }
    };


    function search(query) {
        currentQuery = query;
        processing = true;
        worker.postMessage({type: 'query', query: query}); 
    }


    // display

    function displayResult(results) {    
        var content = '';
        for (r of results) {
            content += '<a href="#' + datalist[r.index] + '" class="list-group-item list-group-item-action" class="suggestion-item">' + datalist[r.index] + '</a>'
        }
        
        suggestions.querySelector('ul').innerHTML = content;
        
        suggestions.querySelectorAll('a').forEach(function(elem) {
            elem.addEventListener('mousedown', function(e) {
                prof_query.value = e.target.innerText;});
        });
        
    }

    
    // events

    prof_query.addEventListener('input', function(e) {
            var query = e.target.value.trim();
            if (processing) {
                nextQuery = query;
                return;
            } 
            if (currentQuery === query) return;
            
            search(query);
    }
);

// Function to handle hash change and redirect to Timetable.html
function handleHashChange() {
    var fragment = window.location.hash;
    if (fragment.startsWith('#')) {
        fragment = fragment.substring(1); // Remove leading #
    }
    var professorName = decodeURIComponent(fragment);

    console.log(professorName);

    // Redirect to Timetable.html with professorName as query parameter
    window.location.href = './TimeTable.html?prof=' + encodeURIComponent(professorName);
}

// Listen for hashchange event to detect URL fragment changes
window.addEventListener('hashchange', function() {
    console.log("hmmm");
    handleHashChange();
});

// Initial check in case the hash is already present on page load
if (window.location.hash) {
    console.log("Heyy");
    handleHashChange();
}
}
