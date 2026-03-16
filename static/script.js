const ctx = document.getElementById('crowdChart');

let labels = [];
let data = [];

const chart = new Chart(ctx, {

type: 'line',

data: {

labels: labels,

datasets: [{

label: 'People Count',

data: data,

borderColor: 'red',

backgroundColor: 'rgba(255,0,0,0.2)',

tension: 0.4

}]

},

options: {

responsive: true,

scales: {

y: {

beginAtZero: true

}

}

}

});


function updateGraph(count){

let time = new Date().toLocaleTimeString();

labels.push(time);

data.push(count);

if(labels.length > 15){

labels.shift();

data.shift();

}

chart.update();

}


async function updateData(){

let response = await fetch("/count");

let dataRes = await response.json();

let count = dataRes.count;

document.getElementById("count").innerText = count;


if(count < 5){

document.getElementById("density").innerText = "LOW";

document.getElementById("alert").innerText = "SAFE";

}

else if(count < 10){

document.getElementById("density").innerText = "MEDIUM";

document.getElementById("alert").innerText = "WARNING";

}

else{

document.getElementById("density").innerText = "HIGH";

document.getElementById("alert").innerText = "DANGER";

}

updateGraph(count);

}


async function toggleSystem(){

await fetch("/toggle");

}


setInterval(updateData,2000);