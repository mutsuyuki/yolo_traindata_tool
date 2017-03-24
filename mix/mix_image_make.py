# -*- coding:utf-8 -*-
from PIL import Image
import random
import os
from increase_image import *

image_class = "3"
background_dir = "./mix_background/"
sticky_dir = "./mix_heart/"
file_prefix = "mix_heart_"
background_width = 600

for i in range(3000):

    file_path_text = './my_train_data/labels/' + file_prefix + str(i) + '.txt'
    file_path_img = './my_train_data/JPEGImages/' + file_prefix + str(i) + '.jpg'

    background = Image.open(background_dir + str(random.randint(0, 9)) + '.png')
    background = background.resize((
        background_width,
        int(background.size[1] * background_width / background.size[0])
    ))
    if (os.path.isfile(file_path_text)):
        os.remove(file_path_text)

    width = random.randint(35, 220)
    with open(file_path_text, 'a') as f:

        sticky_num = random.randint(int(background_width / width) - 1, int(background_width / width) + 1)
        for s in range(sticky_num):
            sticky = Image.open(sticky_dir + str(random.randint(0, 9)) + '.png')

            edit_sticky = Image.new('RGBA', (sticky.size[0] * 2, sticky.size[1] * 2), (255, 255, 255, 0))
            edit_sticky.paste(sticky, (int(sticky.size[0] / 2), int(sticky.size[1] / 2)))

            edit_sticky = edit_sticky.rotate(random.randint(-15, 15))
            height = int(edit_sticky.size[1] * width / edit_sticky.size[0])
            edit_sticky = edit_sticky.resize((width, height))

            # layer1と同じ大きさの画像を全面透過で作成
            c = Image.new('RGBA', background.size, (255, 255, 255, 0))
            sticky_x = int(float(s) / float(sticky_num) * background_width ) + random.randint(0, 30)
            sticky_y = random.randint(0, background.size[1] - height)
            c.paste(edit_sticky, (sticky_x, sticky_y), edit_sticky)
            background = Image.alpha_composite(background, c)

            teacher_data = image_class + " " + \
                           str((sticky_x + (edit_sticky.size[0] / 2.0)) / background.size[0]) + " " + \
                           str((sticky_y + (edit_sticky.size[1] / 2.0)) / background.size[1]) + " " + \
                           str(float(edit_sticky.size[0]) / background.size[0] * 0.6) + " " + \
                           str(float(edit_sticky.size[1]) / background.size[1] * 0.6) + "\n"
            f.write(teacher_data)


    if(random.randint(0,100) < 10):
        background = background.convert('L')

    background.save(file_path_img, 'JPEG', quality=95)
