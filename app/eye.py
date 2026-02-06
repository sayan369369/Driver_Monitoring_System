import numpy as np
from scipy.spatial import distance as dist

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(eye_points, landmarks, w, h):
    coords = []

    for i in eye_points:
        lm = landmarks.landmark[i]
        coords.append((int(lm.x*w), int(lm.y*h)))

    A = dist.euclidean(coords[1], coords[5])
    B = dist.euclidean(coords[2], coords[4])
    C = dist.euclidean(coords[0], coords[3])

    ear = (A + B) / (2.0 * C)
    return ear
