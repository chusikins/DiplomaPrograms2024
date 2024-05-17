import cv2
import panorama
import os

# camera = cv2.VideoCapture(0)
# ret, pano = camera.read()

path = "C:\\Users\\aleks\\PycharmProjects\\TRIK-geo\\data\\frames"
fname = os.path.join(path, f"frame{10}.jpg")
pano = cv2.imread(fname)
for i in range(11, 59, 3):
    print(i)
    try:
        fname = os.path.join(path, f"frame{i}.jpg")
        frame = cv2.imread(fname)
        new = panorama.makePano(pano, frame)
        pano = new
    except Exception as e:
        print(e)
        print("Skipping frame")
    # cv2.waitKey(500)
cv2.imshow("out", pano)
cv2.imwrite("data/pano/pano.jpg", pano)
cv2.waitKey(5000)