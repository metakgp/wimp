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
            content += '<li><a href="/?prof=' + datalist[r.index] + '" tabindex="1" class="list-group-item list-group-item-action" class="suggestion-item">' + datalist[r.index] + '</a></li>'
        }
        
        suggestions.querySelector('ul').innerHTML = content;
        
        suggestions.querySelectorAll('a').forEach(function(elem) {
            elem.addEventListener('mousedown', function(e) {prof_query.value = e.target.innerText;});
        });
        
        var list = document.getElementById('list'); // targets the <ul>
        var first = list.firstChild; // targets the first <li>
        var maininput = document.getElementById('prof_query');  // targets the input, which triggers the functions populating the list
        document.onkeydown = function(e) { // listen to keyboard events
            switch (e.keyCode) {
            case 38: // if the UP key is pressed
                if (document.activeElement == (maininput || first)) { break; } // stop the script if the focus is on the input or first element
                else { document.activeElement.parentNode.previousSibling.firstChild.focus(); } // select the element before the current, and focus it
                break;
            case 40: // if the DOWN key is pressed
                if (document.activeElement == maininput) { first.firstChild.focus(); } // if the currently focused element is the main input --> focus the first <li>
                else { document.activeElement.parentNode.nextSibling.firstChild.focus(); } // target the currently focused element -> <a>, go up a node -> <li>, select the next node, go down a node and focus it
            break;
            }
        }
        
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
