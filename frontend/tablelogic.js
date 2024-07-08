// Example user-inputted variable
document.addEventListener('DOMContentLoaded',function(){

var urlParams = new URLSearchParams(window.location.search);
var userInput = urlParams.get('prof');


fetch('data.json').then((response)=>response.json()).then(data=>{

if (data.hasOwnProperty(userInput)) {

    // Access the corresponding data using userInput
    var userObject = data[userInput];
    const caption= window.document.querySelector("caption");
    const website=userObject.website;
    caption.innerHTML= `<h1><span style="color: #007bff"><a href=${website}>${userInput}</a></span> | ${userObject.dept}</span></h1>`;
    
    // Accessing the timetable array
    var timetable = userObject.timetable;

    timetable.forEach(function(entry, index) {
        var firstArray = entry[0];
        var secondArray = entry[1];
        
        // Print each entry dynamically
        console.log(`Entry ${index + 1}:`);
        for(let el of firstArray){
            let elementId = `${el}`
            let dataatId=window.document.getElementById(elementId);
            let elementdata=secondArray[0];
            if(elementdata==="0"){
                dataatId.innerHTML="In Dept.";
            }
            else{
                dataatId.innerHTML=elementdata;
            }
            
        }
    })
}
})
});
