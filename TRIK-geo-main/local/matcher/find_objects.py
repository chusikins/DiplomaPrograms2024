import cv2
import numpy as np
import matplotlib.pyplot as plt
import pickle
from sift_matcher import get_bounding_box
from scipy.ndimage.filters import gaussian_filter


BOX_LEN_IN_PX = 50

pano = cv2.imread('data/pano/pano.jpg')

finish = cv2.imread('data/samples/finish.jpg')
box1 = cv2.imread('data/samples/box1.jpg')
box2 = cv2.imread('data/samples/box2.jpg')
tools = cv2.imread('data/samples/toolbox.jpg')


finish_bound = get_bounding_box(finish, pano)
box1_bound = get_bounding_box(box1, pano)
box2_bound = get_bounding_box(box2, pano)
toolbox_bound = get_bounding_box(tools, pano)


# Draw bounding box on original image
img = cv2.polylines(pano, [finish_bound], True, (0,255,0),3, cv2.LINE_AA)
img = cv2.polylines(img, [box1_bound], True, (0,0,255),3, cv2.LINE_AA)
img = cv2.polylines(img, [box2_bound], True, (0,0,255),3, cv2.LINE_AA)
img = cv2.polylines(img, [toolbox_bound], True, (0,0,255),3, cv2.LINE_AA)

# draw obsacles on map
black_map = np.zeros(pano.shape)
black_map = cv2.polylines(black_map, [box1_bound], True, (255, 255, 255), 1, cv2.LINE_AA)
black_map = cv2.polylines(black_map, [box2_bound], True, (255, 255, 255), 1, cv2.LINE_AA)
black_map = cv2.polylines(black_map, [toolbox_bound], True, (255, 255, 255), 1, cv2.LINE_AA)


# ищем центр финиша и рисуем его на оригинальном изображении
bound = finish_bound
center_x = np.sum([bound[0][0][0], bound[1][0][0], bound[2][0][0], bound[3][0][0]]) // 4
center_y = np.sum([bound[0][0][1], bound[1][0][1], bound[2][0][1], bound[3][0][1]]) // 4
img = cv2.circle(img, (center_x, center_y), 5, (0, 255, 0), 4)


# масштабируем изображение до 1см/пиксель
p1 = toolbox_bound[0][0]
p2 = toolbox_bound[1][0]
p3 = toolbox_bound[2][0]

v1 = p1 - p2
v2 = p2 - p3
v3 = p1 - p3

l1 = np.linalg.norm(v1)
l2 = np.linalg.norm(v2)
l3 = np.linalg.norm(v3)

m = sorted([l1, l2, l3])[1]
factor = BOX_LEN_IN_PX / m
center_x *= factor
center_y *= factor

box1_bound = (box1_bound * factor).astype('int')
box2_bound = (box2_bound * factor).astype('int')
toolbox_bound = (toolbox_bound * factor).astype('int')

img = cv2.resize(img, (0, 0), fx=factor, fy=factor)
black_map = cv2.resize(black_map, (0, 0), fx=factor, fy=factor)

# при помощи гауссовского фильтра размываем границы препятствий
obstacles = gaussian_filter(black_map, sigma=10)
# для визуализации накладываем старые границы
obstacles_copy = cv2.polylines(obstacles, [box1_bound], True, (255,0,0),2, cv2.LINE_AA)
obstacles_copy = cv2.polylines(obstacles_copy, [box2_bound], True, (255,0,0),2, cv2.LINE_AA)
obstacles_copy = cv2.polylines(obstacles_copy, [toolbox_bound], True, (255,0,0),2, cv2.LINE_AA)

# выводим все на экран
cv2.imshow("img", img)
cv2.imshow("black_map", black_map)
cv2.imshow("obstacles_copy", obstacles_copy)


# строим карту методов отталикивающих потенциалов

fig = plt.figure()
axe = fig.add_subplot(121, projection='3d')

dataForX = np.linspace(0, black_map.shape[1], black_map.shape[1])
dataForY = np.linspace(0, black_map.shape[0], black_map.shape[0])

dataForX, dataForY = np.meshgrid(dataForX, dataForY)

# black_map = black_map[:, :, 0]
obstacles = (obstacles[:, :, 0] + obstacles[:, :, 1] + obstacles[:, :, 2]) // 3
Z = ((dataForX - center_x)**2 + (dataForY - center_y)**2) /1000 + obstacles
Z = gaussian_filter(Z, sigma=10)

surface = axe.plot_surface(dataForX, dataForY, Z, cmap='inferno', linewidth=0, antialiased=False)

fig.colorbar(surface, shrink=0.7, aspect=10)

axe.set_xlabel('X')
axe.set_ylabel('Y')
axe.set_zlabel('Z')

axe.set_title('3D Surface Plot')

gradients = np.gradient(Z)
print(gradients[0].shape, gradients[1].shape)
# start = [30, 30]
# f_start = Z[30, 30]
# end = [300, 300]
# f_end = Z[300, 300]

X_1 = [150]
Y_1 = [120]
Z_1 = [Z[120, 150]]

for i in range(30):
    last_x = X_1[-1]
    last_y = Y_1[-1]
    # grad = gradients[last_x, last_y]
    alpha = 100
    last_x -= int(gradients[1][last_y, last_x] * alpha)
    last_y -= int(gradients[0][last_y, last_x] * alpha)
    print(last_x, last_y)
    X_1.append(last_x)
    Y_1.append(last_y)
    Z_1.append(Z[last_x, last_y])


print("center: ", center_x, center_y)
ax1 = fig.add_subplot(122, projection='3d')
ax1.plot3D(X_1, Y_1, Z_1, color='black', linewidth=5)
# ax1.show()

plt.figure()
plt.imshow(Z, cmap='hot')
plt.savefig("heatmap.png")
plt.show()





# save all images
cv2.imwrite("data/maps/bounding_boxes.jpg", img)
cv2.imwrite("data/maps/black_map.jpg", black_map)

with open('data/maps/map.pickle', 'wb') as handle:
    pickle.dump(black_map, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('data/maps/gradients.pickle', 'wb') as handle:
    pickle.dump(gradients, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('data/maps/gradients_lists.pickle', 'wb') as handle:
    gradients_lists = [gradients[0].tolist(), gradients[1].tolist()]
    pickle.dump(gradients_lists, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open('data/maps/bounds.pickle', 'wb') as handle:
    pickle.dump([box1_bound, box2_bound, toolbox_bound], handle, protocol=pickle.HIGHEST_PROTOCOL)