#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# usage: ./increase_picture.py hogehoge.jpg
#

import cv2
import numpy as np
import sys
import os
import shutil


# ヒストグラム均一化
def equalizeHistRGB(src):
    RGB = cv2.split(src)
    Blue = RGB[0]
    Green = RGB[1]
    Red = RGB[2]
    for i in range(3):
        cv2.equalizeHist(RGB[i])

    img_hist = cv2.merge([RGB[0], RGB[1], RGB[2]])
    return img_hist


# ガウシアンノイズ
def addGaussianNoise(src):
    row, col, ch = src.shape
    mean = 0
    var = 0.1
    sigma = 15
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    noisy = src + gauss

    return noisy


# salt&pepperノイズ
def addSaltPepperNoise(src):
    row, col, ch = src.shape
    s_vs_p = 0.5
    amount = 0.004
    out = src.copy()
    # Salt mode
    num_salt = np.ceil(amount * src.size * s_vs_p)
    coords = [np.random.randint(0, i - 1, int(num_salt))
              for i in src.shape]
    out[coords[:-1]] = (255, 255, 255)

    # Pepper mode
    num_pepper = np.ceil(amount * src.size * (1. - s_vs_p))
    coords = [np.random.randint(0, i - 1, int(num_pepper))
              for i in src.shape]
    out[coords[:-1]] = (0, 0, 0)
    return out


# グレースケール変換
def rgbaToGray(src):

    return cv2.cvtColor(src, cv2.COLOR_RGBA2GRAY)



if __name__ == '__main__':
    # ルックアップテーブルの生成
    min_table = 50
    max_table = 205
    diff_table = max_table - min_table
    gamma1 = 0.75
    gamma2 = 1.5

    LUT_HC = np.arange(256, dtype='uint8')
    LUT_LC = np.arange(256, dtype='uint8')
    LUT_G1 = np.arange(256, dtype='uint8')
    LUT_G2 = np.arange(256, dtype='uint8')

    LUTs = []

    # 平滑化用
    average_square = (4, 4)

    # ハイコントラストLUT作成
    for i in range(0, min_table):
        LUT_HC[i] = 0

    for i in range(min_table, max_table):
        LUT_HC[i] = 255 * (i - min_table) / diff_table

    for i in range(max_table, 255):
        LUT_HC[i] = 255

    # その他LUT作成
    for i in range(256):
        LUT_LC[i] = min_table + i * (diff_table) / 255
        LUT_G1[i] = 255 * pow(float(i) / 255, 1.0 / gamma1)
        LUT_G2[i] = 255 * pow(float(i) / 255, 1.0 / gamma2)

    LUTs.append(LUT_HC)
    LUTs.append(LUT_LC)
    LUTs.append(LUT_G1)
    LUTs.append(LUT_G2)

    imageDir = sys.argv[1]
    files = os.listdir(sys.argv[1])

    for file_name in files:
        file_path = imageDir + file_name
        file_type = os.path.splitext(os.path.basename(file_path))[1]

        if(file_type != ".jpg" and file_type != ".png"):
            continue

        # 画像の読み込み
        img_src = cv2.imread(file_path, 1)
        trans_img = []
        trans_img.append(img_src)

        # LUT変換
        for i, LUT in enumerate(LUTs):
            trans_img.append(cv2.LUT(img_src, LUT))

        # 平滑化
        trans_img.append(cv2.blur(img_src, average_square))

        # ヒストグラム均一化
        trans_img.append(equalizeHistRGB(img_src))

        # ノイズ付加
        trans_img.append(addGaussianNoise(img_src))
        trans_img.append(addSaltPepperNoise(img_src))

        # グレースケール変換
        # trans_img.append(rgbaToGray(img_src))

        # 反転
        flip_img = []
        for img in trans_img:
            flip_img.append(cv2.flip(img, 1))


        basename = os.path.splitext(os.path.basename(file_path))[0]
        img_src.astype(np.float64)
        print(len(trans_img))
        print(len(flip_img))


        cv2.imwrite("my_train_data/JPEGImages/" + basename + ".jpg", img_src)
        shutil.copy("workLabels/" + basename + ".txt", "my_train_data/labels/" + basename + ".txt")

        for i, img in enumerate(trans_img):
            cv2.imwrite("my_train_data/JPEGImages/" + basename + "_" + str(i) + ".jpg", img)
            shutil.copy("workLabels/" + basename + ".txt", "my_train_data/labels/" + basename + "_" + str(i) + ".txt")

        for i, img in enumerate(flip_img):
            file_index = i + len(trans_img)
            cv2.imwrite("my_train_data/JPEGImages/" + basename + "_" + str(file_index) + ".jpg", img)
            teacher_data = []
            with open("./workLabels/" + basename + ".txt") as f:
                for line in f:
                    data = line.split(" ")
                    if (len(data) < 5):
                        break
                    teacher_data.append( data[0] + " " + str(1 - float(data[1])) + " " + data[2] + " " + data[3] + " " + data[4] )

            with open("./my_train_data/labels/" + basename + "_" + str(file_index) + ".txt", "w") as f:
                file_index = i + len(trans_img)
                for line in teacher_data:
                    f.write(line)
