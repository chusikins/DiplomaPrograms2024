import cv2
import numpy as np

def makePano(pano, frame):
    w_pano, h_pano = pano.shape[1], pano.shape[0]
    w_frame, h_frame = frame.shape[1], frame.shape[0]
    pano = cv2.copyMakeBorder(pano, h_frame//2, h_frame//2, w_frame//2, w_frame//2, cv2.BORDER_CONSTANT, value=[0,0,0])
    frame = cv2.copyMakeBorder(frame, h_pano//2, 0, w_pano//2, 0, cv2.BORDER_CONSTANT, value=[0,0,0])

    img1 = cv2.cvtColor(pano, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # находим фичи
    sift = cv2.xfeatures2d.SIFT_create()
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(img2, None)

    # пользуемся методом брут-форс для определения соответствия фич
    match = cv2.BFMatcher()
    matches = match.knnMatch(des1, des2, k=2)
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    MIN_MATCH_COUNT = 3
    if len(good) > MIN_MATCH_COUNT:
        # находим преобразование
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1, 1, 2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        dst = cv2.warpPerspective(pano, M, (pano.shape[0]*2, pano.shape[1]*2))

        print(f"{h_frame}={frame.shape[0] - h_pano//2};{w_frame}={frame.shape[1] - w_pano//2};")
        dst[(h_pano//2):(h_pano//2+h_frame), (w_pano//2):(w_pano//2+w_frame)] = frame[h_pano//2:, w_pano//2:]
        # обрезка контура
        dst = crop(dst)
        return dst
    else:
        print("Not enought matches are found - ", len(good), "/", MIN_MATCH_COUNT)

def crop(image):
    y_nonzero, x_nonzero, _ = np.nonzero(image)
    return image[np.min(y_nonzero):np.max(y_nonzero), np.min(x_nonzero):np.max(x_nonzero)]

if __name__ == "__main__":
    pass
    # # img1 = cv2.imread("./images/original_image_left.jpg")
    # # img2 = cv2.imread("./images/original_image_right.jpg")
    # path = "./capture/"
    # names = os.listdir(path)
    # fname = os.path.join(path, names[0])
    # pano = cv2.imread(fname)
    # for i in names[1:]:
    #     fname = os.path.join(path, i)
    #     # print(fname)
    #     img0 = cv2.imread(fname)
    #     try:
    #         merge = makePano(img0, pano)
    #         pano = merge
    #     except:
    #         print("Skip frame")
    # cv2.imshow("dst", pano)
    # cv2.waitKey()

    # makePano(img2, img1)