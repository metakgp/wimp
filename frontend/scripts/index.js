document.addEventListener("DOMContentLoaded", () => {
    fetch('../frontend/data.json') 
        .then(response => response.json())
        .then(data => {
            const datalist = Object.keys(data);
            console.log(datalist);

            var worker = new Worker("./worker.js");
            autocomplete(datalist, worker);
        })
        .catch(error => console.error('Error fetching data.json:', error));
});