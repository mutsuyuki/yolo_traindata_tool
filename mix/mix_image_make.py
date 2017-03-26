# -*- coding:utf-8 -*-
from PIL import Image
import random
import os

background_dir = "./mix_background/"
object_dir = "./mix_object/"
file_prefix = "mix_hubyu_"
background_width = 640

for i in range(3000):

    file_path_text = './my_train_data/labels/' + file_prefix + str(i) + '.txt'
    file_path_img = './my_train_data/JPEGImages/' + file_prefix + str(i) + '.jpg'

    background_files = os.listdir(background_dir)
    background_file_name = background_files[random.randint(1, len(background_files) - 1)]  # index 0 is .DS_Store
    background_image = Image.open(background_dir + background_file_name)
    background_image = background_image.resize((
        background_width,
        int(background_image.size[1] * background_width / background_image.size[0])
    ))
    if (os.path.isfile(file_path_text)):
        os.remove(file_path_text)

    width = random.randint(85, 110)
    with open(file_path_text, 'a') as f:

        object_num = random.randint(int(background_width / width) - 1, int(background_width / width) + 1)
        for s in range(object_num):
            object_files = os.listdir(object_dir)
            object_file_name = object_files[random.randint(1, len(object_files) - 1)]  # index 0 is .DS_Store
            object_image = Image.open(object_dir + object_file_name)

            edit_object = Image.new('RGBA', (object_image.size[0] * 2, object_image.size[1] * 2), (255, 255, 255, 0))
            edit_object.paste(object_image, (int(object_image.size[0] / 2), int(object_image.size[1] / 2)))
            edit_object = edit_object.rotate(random.randint(0, 360))
            height = int(edit_object.size[1] * width / edit_object.size[0])
            edit_object = edit_object.resize((int(width * random.uniform(0.92,1.08)), int(height * random.uniform(0.92,1.08))))

            # layer1と同じ大きさの画像を全面透過で作成
            c = Image.new('RGBA', background_image.size, (255, 255, 255, 0))
            sticky_x = int(float(s) / float(object_num) * background_width) + random.randint(-10, 20)
            sticky_y = random.randint(0, background_image.size[1] - height)
            c.paste(edit_object, (sticky_x, sticky_y), edit_object)
            background_image = Image.alpha_composite(background_image, c)

            teacher_data = object_file_name.split("_")[0] + " " + \
                           str((sticky_x + (edit_object.size[0] / 2.0)) / background_image.size[0]) + " " + \
                           str((sticky_y + (edit_object.size[1] / 2.0)) / background_image.size[1]) + " " + \
                           str(float(edit_object.size[0]) / background_image.size[0] * 0.6) + " " + \
                           str(float(edit_object.size[1]) / background_image.size[1] * 0.6) + "\n"
            f.write(teacher_data)


    background_image.save(file_path_img, 'JPEG', quality=95)
