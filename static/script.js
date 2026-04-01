const ctx = document.getElementById('crowdChart');

let labels = [];
let dataPoints = [];
let systemRunning = true;

// Chart
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'People Count',
            data: dataPoints,
            borderColor: 'red',
            backgroundColor: 'rgba(255,0,0,0.2)',
            tension: 0.4
        }]
    }
});

function updateGraph(count){
    let time = new Date().toLocaleTimeString();

    labels.push(time);
    dataPoints.push(count);

    if(labels.length > 15){
        labels.shift();
        dataPoints.shift();
    }

    chart.update();
}

// Camera
const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => video.srcObject = stream)
.catch(() => alert("Camera permission denied"));

// Send frame
async function sendFrame(){

    if(!systemRunning) return;

    // ✅ smaller resolution
    canvas.width = 320;
    canvas.height = 240;

    const ctx2 = canvas.getContext("2d");
    ctx2.drawImage(video, 0, 0, 320, 240);

    // ✅ medium quality
    const image = canvas.toDataURL("image/jpeg", 0.7);

    try{
        const res = await fetch("/process_frame", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ image: image })
        });

        const data = await res.json();

        if(data.image){
            document.getElementById("output").src =
                "data:image/jpeg;base64," + data.image;
        }

        let count = data.count;

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

    } catch(err){
        console.log("Error:", err);
    }
}

// ✅ slower interval (smooth + safe)
setInterval(sendFrame, 1500);

// Toggle
async function toggleSystem(){
    let res = await fetch("/toggle");
    let data = await res.json();
    systemRunning = data.status;

    alert(systemRunning ? "Started" : "Stopped");
}