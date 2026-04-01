// 📊 Chart
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
            y: { beginAtZero: true }
        }
    }
});

// 📈 Graph update
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

// 📡 Fetch count
async function updateData(){
    try {
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

    } catch(err) {
        console.log("Server error:", err);
    }
}

setInterval(updateData, 2000);

// 🔘 Toggle
async function toggleSystem(){
    await fetch("/toggle");
}

// 🎥 CAMERA (FINAL FIX)
const video = document.getElementById("video");

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });

        video.srcObject = stream;

        video.onloadedmetadata = () => {
            video.play();
        };

        video.muted = true;
        video.setAttribute("playsinline", true);

    } catch (error) {
        alert("Camera not accessible!");
        console.error(error);
    }
}

startCamera();

// 📸 Send frame (LIGHT VERSION)
const canvas = document.getElementById("canvas");

async function sendFrame(){

    if(video.readyState !== 4) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    const image = canvas.toDataURL("image/jpeg");

    try {
        await fetch("/process_frame", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ image: image })
        });
    } catch(err){
        console.log("Frame send error");
    }
}

setInterval(sendFrame, 3000);