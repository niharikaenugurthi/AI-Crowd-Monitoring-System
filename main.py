from alert import send_alert
from aws_upload import upload_image
import cv2
import time
import numpy as np
from ultralytics import YOLO

# load YOLO model
model = YOLO("yolov8n.pt")

# open webcam
cap = cv2.VideoCapture(0)

heatmap = None

# alert control
last_alert_time = 0

while True:

    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape

    # initialize heatmap
    if heatmap is None:
        heatmap = np.zeros((h, w), dtype=np.float32)

    results = model(frame)

    people_count = 0

    for r in results:
        for box in r.boxes:

            cls = int(box.cls[0])

            # class 0 = person
            if cls == 0:

                people_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                # update heatmap
                heatmap[y1:y2, x1:x2] += 1


    # crowd density logic
    if people_count > 10:
        density = "HIGH"
    elif people_count > 5:
        density = "MEDIUM"
    else:
        density = "LOW"


    # heatmap generation
    heatmap_norm = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
    heatmap_color = cv2.applyColorMap(heatmap_norm.astype(np.uint8), cv2.COLORMAP_JET)

    overlay = cv2.addWeighted(frame, 0.7, heatmap_color, 0.3, 0)


    # show people count
    cv2.putText(overlay,
                f"People Count: {people_count}",
                (10,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                2)

    # show density
    cv2.putText(overlay,
                f"Density: {density}",
                (10,80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255,0,0),
                2)


    # high crowd alert banner
    if people_count > 10:

        cv2.putText(overlay,
                    "ALERT: CROWD DENSITY HIGH",
                    (50,120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,0,255),
                    3)

        # send SNS alert once every 30 seconds
        if time.time() - last_alert_time > 30:
            send_alert(people_count)
            last_alert_time = time.time()

        # upload image to S3
        cv2.imwrite("crowd_alert.jpg", overlay)
        upload_image("crowd_alert.jpg")


    # show window
    cv2.imshow("AI Crowd Monitoring System", overlay)

    if cv2.waitKey(1) == 27:
        break


cap.release()
cv2.destroyAllWindows()