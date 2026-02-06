import cv2
import time
import threading
import os
import subprocess

from app.camera import get_camera
from app.face_landmarks import get_landmarks
from app.eye import eye_aspect_ratio, LEFT_EYE, RIGHT_EYE
from app.yawn import mouth_aspect_ratio


cap = get_camera()

# -------- PATH --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALARM_PATH = os.path.join(BASE_DIR, "assets", "alarm.wav")

# -------- SESSION TRACKING --------
session_start = time.time()
fatigue_history = []
yawn_events = 0
danger_events = 0

# -------- STATE VARIABLES --------
eye_closed_start = None
blink_count = 0
blink_start = None
last_blink_time = time.time()
yawn_start = None

fatigue_score = 0
last_alarm_time = 0
alarm_playing = False

# -------- CONSTANTS --------
EAR_THRESHOLD = 0.23
BLINK_MIN = 0.08
BLINK_MAX = 0.4
YAWN_THRESHOLD = 25


# -------- SAFE ALARM --------
def play_alarm():
    global alarm_playing
    if alarm_playing:
        return
    alarm_playing = True

    def _play():
        global alarm_playing
        try:
            subprocess.run(["afplay", ALARM_PATH])
        except:
            pass
        alarm_playing = False

    threading.Thread(target=_play, daemon=True).start()


while True:
    ret, frame = cap.read()
    if not ret:
        break

    current_time = time.time()
    landmarks = get_landmarks(frame)

    if landmarks is None:
        fatigue_score = max(0, fatigue_score - 2)
        cv2.putText(frame, "NO FACE", (30,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200,200,200), 2)

    else:
        h, w, _ = frame.shape

        # -------- EYE EAR --------
        leftEAR = eye_aspect_ratio(LEFT_EYE, landmarks, w, h)
        rightEAR = eye_aspect_ratio(RIGHT_EYE, landmarks, w, h)
        ear = (leftEAR + rightEAR) / 2.0

        # -------- BLINK DETECTION --------
        if ear < EAR_THRESHOLD:
            if blink_start is None:
                blink_start = current_time
            if eye_closed_start is None:
                eye_closed_start = current_time
        else:
            if blink_start is not None:
                blink_duration = current_time - blink_start
                if BLINK_MIN < blink_duration < BLINK_MAX:
                    blink_count += 1
                    last_blink_time = current_time
                blink_start = None
            eye_closed_start = None

        # -------- YAWN DETECTION --------
        mar = mouth_aspect_ratio(landmarks, w, h)
        if mar > YAWN_THRESHOLD:
            if yawn_start is None:
                yawn_start = current_time
        else:
            if yawn_start and current_time - yawn_start > 1.5:
                yawn_events += 1
            yawn_start = None

        # -------- FATIGUE CALCULATION --------
        time_since_last_blink = current_time - last_blink_time
        closed_duration = (current_time - eye_closed_start) if eye_closed_start else 0

        fatigue_increment = 0

        if closed_duration > 2:
            fatigue_increment += 10
            state = "DANGER"
            color = (0,0,255)
            danger_events += 1

        elif yawn_start and (current_time - yawn_start > 1.5):
            fatigue_increment += 4
            state = "YAWNING"
            color = (255,140,0)

        elif time_since_last_blink > 4:
            fatigue_increment += 2
            state = "SLEEPY"
            color = (0,165,255)

        else:
            fatigue_increment -= 1
            state = "AWAKE"
            color = (0,255,0)

        fatigue_score = max(0, min(100, fatigue_score + fatigue_increment))
        fatigue_history.append(fatigue_score)

        # -------- ALARM --------
        if fatigue_score > 15 and current_time - last_alarm_time > 3:
            play_alarm()
            last_alarm_time = current_time

        # -------- DISPLAY --------
        cv2.putText(frame, state, (30,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

        cv2.putText(frame, f"Blinks: {blink_count}", (30,100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        cv2.putText(frame, f"Fatigue: {fatigue_score}", (30,140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

    cv2.imshow("Driver Monitoring System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break


# -------- SESSION REPORT --------
cap.release()
cv2.destroyAllWindows()

session_duration = time.time() - session_start
avg_fatigue = sum(fatigue_history)/len(fatigue_history) if fatigue_history else 0

if avg_fatigue < 20:
    rating = "SAFE"
elif avg_fatigue < 50:
    rating = "TIRED"
else:
    rating = "UNSAFE"

print("\n========= DRIVER REPORT =========")
print(f"Trip Duration: {int(session_duration//60)} min {int(session_duration%60)} sec")
print(f"Total Blinks: {blink_count}")
print(f"Yawn Events: {yawn_events}")
print(f"Danger Events: {danger_events}")
print(f"Average Fatigue: {avg_fatigue:.1f}%")
print(f"Driver Rating: {rating}")
print("=================================\n")
