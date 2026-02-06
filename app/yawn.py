from scipy.spatial import distance as dist

# MediaPipe mouth landmark indexes
UPPER_LIP = 13
LOWER_LIP = 14

def mouth_aspect_ratio(landmarks, w, h):
    top = landmarks.landmark[UPPER_LIP]
    bottom = landmarks.landmark[LOWER_LIP]

    top_point = (int(top.x * w), int(top.y * h))
    bottom_point = (int(bottom.x * w), int(bottom.y * h))

    mar = dist.euclidean(top_point, bottom_point)
    return mar
