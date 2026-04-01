from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import base64
import time
import os
from ultralytics import YOLO
from alert import send_alert

app = Flask(__name__)

# ✅ lightweight model
model = YOLO("yolov8n.pt")

people_count = 0
last_alert_time = 0
system_running = True
last_counts = []

@app.route('/')
def dashboard():
    return render_template("index.html")


@app.route('/process_frame', methods=['POST'])
def process_frame():

    global people_count, last_alert_time, system_running, last_counts

    if not system_running:
        return jsonify({"count": people_count, "image": None})

    data = request.json['image']
    img_data = base64.b64decode(data.split(',')[1])

    np_arr = np.frombuffer(img_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # ✅ smaller image for speed
    frame = cv2.resize(frame, (320, 240))

    # ✅ faster inference
    results = model(frame, imgsz=320)

    people_count = 0

    for r in results:
        for box in r.boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if cls == 0 and conf > 0.5:
                people_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)

    # ✅ smoothing
    last_counts.append(people_count)
    if len(last_counts) > 5:
        last_counts.pop(0)

    people_count = int(sum(last_counts) / len(last_counts))

    # ✅ alert control
    if people_count > 10 and time.time() - last_alert_time > 30:
        send_alert(people_count)
        last_alert_time = time.time()

    # ✅ encode image (low quality for speed)
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    frame_base64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "count": people_count,
        "image": frame_base64
    })


@app.route('/toggle')
def toggle():
    global system_running
    system_running = not system_running
    return jsonify({"status": system_running})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))