import cv2
import numpy as np

coordinates = []

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(coordinates) < 4:
            coordinates.append((x,y))
            cv2.circle(bin_img, (x,y), radius=5, color=(255,0,0), thickness=-1)
            cv2.imshow('binary_image', bin_img)

def sortpoints(list):
    new_list = [list[0][0]+list[0][1], list[1][0]+list[1][1], list[2][0]+list[2][1], list[3][0]+list[3][1]]
    sorted_list = [x for _,x in sorted(zip(new_list, list))]
    sorted_list.reverse()
    cycle_list = [sorted_list[0], sorted_list[1], sorted_list[3], sorted_list[2]]
    print(sorted_list)
    print(cycle_list)
    return cycle_list

def minmax(img):
    minX = img.shape[1]
    maxX = -1
    minY = img.shape[0]
    maxY = -1
    for point in coordinates:
        x = point[0]
        y = point[1]

        if x < minX:
            minX = x
        if x > maxX:
            maxX = x
        if y < minY:
            minY = y
        if y > maxY:
            maxY = y
    return minX, maxX, minY, maxY

def crop(img):
    minX, maxX, minY, maxY = minmax(img)        
    cropped_img = np.zeros_like(img)
    for y in range(0, img.shape[0]):
        for x in range(0, img.shape[1]):
            if x < minX or x > maxX or y < minY or y > maxY:
                continue
            if cv2.pointPolygonTest(np.asarray(coordinates), (x,y), False) >= 0:
                cropped_img[y, x] = img[y, x]
    
    return cropped_img[minY:maxY, minX:maxX]

def warp(img):
    minX, maxX, minY, maxY = minmax(img) 
    stretched_img = np.float32([[0,0],[img.shape[1],0],[img.shape[1],img.shape[0]],[0,img.shape[0]]])
    img_transform = np.zeros_like(stretched_img)
    i = 0
    for point in coordinates:
        x = point[0]
        y = point[1]
        newX = x - minX
        newY = y - minY
        img_transform[i] = [newX, newY]
        i += 1
    
    M = cv2.getPerspectiveTransform(np.asarray(img_transform).astype(np.float32), np.asarray(stretched_img).astype(np.float32))
    warped_img = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))
    return warped_img

if __name__=="__main__":
    img_name = input("Image name:\n")
    img = cv2.imread('image/' + img_name)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, bin_img = cv2.threshold(img_gray, 128, 255, cv2.THRESH_BINARY)
    #255 (free space, white) or 0 (occupied, black)
    og_bi_img = bin_img
    cv2.imshow('binary_image', bin_img)
    cv2.setMouseCallback('binary_image',click_event)
    cv2.waitKey(0)
    if len(coordinates) == 4:
        sortpoints(coordinates)
    cropped = crop(og_bi_img)
    warped = warp(cropped)
    cv2.imshow('warped', warped)
    cv2.waitKey(0)    
    cv2.imwrite('output/binarized_' + img_name, warped)