from flask import Flask, render_template, Response, jsonify
import cv2
from ultralytics import YOLO
import time

from alert import send_alert

app = Flask(__name__)

# Load YOLO model
model = YOLO("yolov8n.pt")

# Webcam
camera = cv2.VideoCapture(0)

# Variables
people_count = 0
last_alert_time = 0
system_running = True


def generate_frames():

    global people_count
    global last_alert_time
    global system_running

    while True:

        success, frame = camera.read()

        if not success:
            break

        if system_running:

            results = model(frame)

            people_count = 0

            for r in results:
                for box in r.boxes:

                    cls = int(box.cls[0])

                    if cls == 0:   # person detected

                        people_count += 1

                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

            cv2.putText(frame,
                        f"People Count: {people_count}",
                        (10,40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0,0,255),
                        2)

            # ALERT CONDITION
            if people_count > 10 and time.time() - last_alert_time > 30:

                send_alert(people_count)

                last_alert_time = time.time()

        else:

            cv2.putText(frame,
                        "SYSTEM PAUSED",
                        (200,200),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0,0,255),
                        3)

        ret, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Dashboard page
@app.route('/')
def dashboard():
    return render_template("index.html")


# Live video stream
@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# API for crowd count (used by graph)
@app.route('/count')
def get_count():
    global people_count
    return jsonify({"count": people_count})


# Toggle ON / OFF monitoring
@app.route('/toggle')
def toggle():

    global system_running

    system_running = not system_running

    return jsonify({"status": system_running})


if __name__ == "__main__":
    app.run(debug=True)