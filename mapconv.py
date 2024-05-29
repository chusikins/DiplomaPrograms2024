import cv2
import numpy as np
from matplotlib import pyplot as plt
import asearch

image = cv2.imread("map.jpg")
# print(image.shape)
# print(image[0,0])
# print(image[1, 1, 0])
# print(image.all())
robotsize = 23
# print(image[0:10,0:10,0])
def simpleconv(img, maxsize):
    x = 0
    y = 0
    newx = img.shape[0] - maxsize
    newy = img.shape[1] - maxsize
    newmap = np.zeros((newx, newy), dtype=int)
    for yj in range(newy):
        for xi in range(newx):
            res = img[x:maxsize+x, y:maxsize+y, 0].all()
            if not res:
                newmap[xi, yj] = 1
            x += 1
        y += 1
        x = 0
    for i in range(newmap.shape[0]):
        for j in range(newmap.shape[1]):
            if newmap[i,j] == 1:
                newmap[i,j] = 0
            else:
                newmap[i,j] = 1
    return newmap


test = simpleconv(image, 23)
print(test)

src =[400, 400]
# dest = [242, 195]
dest = [0,0]
test2 = asearch.a_star_search(test,src,dest)
for i in range(len(test2)):
    l = test2[i][0]
    k = test2[i][1]
    test[l,k] = 3

plt.imshow(test, interpolation='nearest')
plt.show()