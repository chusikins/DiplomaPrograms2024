import pickle
import math
import cv2
import numpy as np
from PIL import Image
from scipy.ndimage.filters import gaussian_filter

# 1 pixel per cm
with open('../data/maps/map.pickle', 'rb') as handle:
    black_map = pickle.load(handle)

with open('../data/maps/gradients.pickle', 'rb') as handle:
    gradients = pickle.load(handle)

with open('../data/maps/bounds.pickle', 'rb') as handle:
    bounds = pickle.load(handle)

rad = 180 / math.pi

vec = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 305, 292, 281, 280, 282, 284, 286, 289, 292, 294, 297, 300, 304, 307, 311, 315, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 117, 115, 115, 114, 114, 113, 113, 113, 112, 112, 112, 112, 112, 111, 111, 111, 111, 111, 111, 111, 112, 112, 112, 112, 112, 113, 113, 113, 115, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 126, 124, 123, 121, 120, 118, 117, 116, 115, 113, 112, 111, 110, 109, 108, 108, 109, 110, 114, 120, 126, 132, 140, 148, 157, 168, 180, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

points = []
X = []
Y = []
rad = 180 / math.pi

FACTOR = 1.72
THETA = math.pi
for i in range(0, 360):
    phi = i / rad
    dist = vec[i] / FACTOR
    if dist == 0 or dist > 200:
        continue
    x1 = int(dist * math.cos(phi))
    y1 = int(dist * math.sin(phi))
    X.append(x1)
    Y.append(y1)
    points.append((y1, x1))

x_max, x_min = max(X), min(X)
y_max, y_min = max(Y), min(Y)


img = np.zeros((y_max - y_min + 1, x_max - x_min + 1))
for point in points:
    img[point[0] - y_min, point[1] - x_min] = 255


segments = []

for bound in bounds:
    points = bound[0][0], bound[1][0], bound[2][0], bound[3][0]
    print(points)
    segments.append(np.array([points[0], points[1]]))
    segments.append(np.array([points[1], points[2]]))
    segments.append(np.array([points[2], points[3]]))
    segments.append(np.array([points[3], points[0]]))

print(len(segments))


def dist_point_to_point(a, b):
    return np.linalg.norm(a - b)

def distanse_point_to_segment(point, segment):
    # print(point.shape)
    # print(segment.shape)
    v = segment[1] - segment[0]
    w = point - segment[0]

    c1 = np.dot(w, v)
    if c1 <= 0:
        return dist_point_to_point(point, segment[0])
    c2 = np.dot(v, v)
    if c2 <= c1:
        return dist_point_to_point(point, segment[1])

    b = c1 / c2
    Pb = segment[0] + b * v
    return dist_point_to_point(point, Pb)

# np_distanse_point_to_segment = np.vectorize(distanse_point_to_segment)

np_vec = np.array(vec) / FACTOR
np_angles = np.array(range(0, 360)) / rad
np_angles = np_angles[np_vec != 0]
np_vec = np_vec[np_vec != 0]

N = np_vec.shape[0]

print("Hello")
best = 1e18
best_y = 0
best_x = 0
best_theta = 0

for y in range(0, 430, 15):
    print(y)
    for x in range(0, 430, 15):
        for theta in range(0, 360, 10):
            np_angles = np_angles + theta
            np_cos = np.cos(np_angles)
            np_sin = np.sin(np_angles)
            np_x = np_vec * np_cos + x
            np_y = np_vec * np_sin + y

            points = np.stack((np_y, np_x), axis=1)

            min_distances = np.ones(N) * 1e9
            for i in range(N):
                for segment in segments:
                    d = distanse_point_to_segment(points[i], segment)
                    min_distances[i] = min(min_distances[i], d)

            min_d = np.sum(min_distances)
            if (min_d < best):
                best = min_d
                best_x = x
                best_y = y
                best_theta = theta

print("best ", best)
print("best x ", best_x)
print("best y ", best_y)
print("best theta ", best_theta)

np_angles = np_angles + 210
np_cos = np.cos(np_angles)
np_sin = np.sin(np_angles)
np_x = np_vec * np_cos + 150
np_y = np_vec * np_sin + 120
# print(np.max(np_x))
# print(np.max(np_y))

# points = np.stack((np_y, np_x), axis=1)



points = np.stack((np_y, np_x), axis=1)

min_distances = np.ones(N) * 1e9
for i in range(N):
    for segment in segments:
        d = distanse_point_to_segment(points[i], segment)
        min_distances[i] = min(min_distances[i], d)

min_d = np.sum(min_distances)
print("min d", min_d)

print(points.shape)
for point in points:
    # print(point.shape)
    black_map[int(point[1]), min(int(point[0]), 430), 2] = 255

cv2.imshow("map", black_map)
cv2.waitKey(10000)