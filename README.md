# 🚗 Real-Time Driver Monitoring System (AI Safety Assistant)

A real-time computer vision system that monitors driver alertness using facial behavior analysis.

The system detects fatigue indicators such as eye closure, blink patterns, and yawning, computes a fatigue risk score, and triggers an alert to prevent accidents.

---

## Features

- Face landmark tracking (MediaPipe)
- Eye Aspect Ratio (EAR) based blink detection
- Microsleep detection
- Yawn detection
- Fatigue scoring system
- Real-time alarm alert
- Session report generation

---

## How It Works

The system continuously monitors the driver's face using a webcam and evaluates behavioral signals:

| Signal | Meaning |
|------|------|
| No blink for 4s | Sleepiness |
| Eyes closed > 2s | Microsleep (danger) |
| Yawning | Fatigue indicator |

A fatigue score is accumulated over time and an alarm is triggered when the risk becomes unsafe.

---

## Demo

Run the system:

```bash
cd driver-monitoring-system
source venv/bin/activate
python main.py

Press ESC to end session and view the driver report.

========= DRIVER REPORT =========
Trip Duration: 5 min 12 sec
Total Blinks: 132
Yawn Events: 2
Danger Events: 1
Average Fatigue: 31.4%
Driver Rating: TIRED
=================================



