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
            content += '<a href="/?prof=' + datalist[r.index] + '" class="list-group-item list-group-item-action" class="suggestion-item">' + datalist[r.index] + '</a>'
        }
        
        suggestions.querySelector('ul').innerHTML = content;
        
        suggestions.querySelectorAll('a').forEach(function(elem) {
            elem.addEventListener('mousedown', function(e) {prof_query.value = e.target.innerText;});
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
    });

    prof_query.addEventListener('blur', function(e) {
        if (popper !== null) {
            destroyPopper();
        }
    });
}
