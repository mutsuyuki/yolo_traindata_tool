from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.loader import Loader
from kivy.core.window import Window

import copy
import cv2
import sys
import os


class Common:
    # please set class of image
    image_class = "4"

    # init by program
    image_width = 0
    image_height = 0
    image_file_path = ""
    label_file_path = ""


class DrawInput(Widget):
    def __init__(self, **kwargs):
        super(DrawInput, self).__init__(**kwargs)
        self._touch_down_point = []
        self._touch_move_point = []
        self._prev_teacher_data = ""

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_key_down)

    def on_touch_down(self, touch):
        self._isFirstMove = True

    def on_touch_move(self, touch):

        if self._isFirstMove:
            self._touch_down_point = copy.copy(touch)
            self._isFirstMove = False

        self._touch_move_point = copy.copy(touch)

        self.canvas.clear()
        with self.canvas:
            Color(0, 1, 1)
            Line(rectangle=(
                self._touch_down_point.x,
                self._touch_down_point.y,
                self._touch_move_point.x - self._touch_down_point.x,
                self._touch_move_point.y - self._touch_down_point.y
            ))

        self.drawTeacherData()

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        print(keycode)
        if keycode[1] == 's':
            self.saveTeacherData()
        if keycode[1] == 'r':
            self.drawTeacherData()

    def saveTeacherData(self):
        if (self._touch_down_point == []):
            return

        teacher_data = Common.image_class + " " + \
                       str((self._touch_down_point.sx + self._touch_move_point.sx) / 2.0) + " " + \
                       str((1 - self._touch_down_point.sy + 1 - self._touch_move_point.sy) / 2.0) + " " + \
                       str(abs(self._touch_move_point.sx - self._touch_down_point.sx)) + " " + \
                       str(abs(self._touch_move_point.sy - self._touch_down_point.sy)) + "\n"

        if (self._prev_teacher_data == teacher_data):
            return

        with open(Common.label_file_path, 'a') as f:
            print(Common.label_file_path)
            print("teacher", teacher_data)
            f.write(teacher_data)

        self._prev_teacher_data = teacher_data
        self.drawTeacherData()

    def drawTeacherData(self):
        if (os.path.isfile(Common.label_file_path) != True):
            return

        with open(Common.label_file_path) as f:
            for line in f:
                data = line.split(" ")
                if(len(data) < 5):
                    return
                x = float(data[1])
                y = 1.0 - float(data[2])
                w = float(data[3])
                h = float(data[4])
                with self.canvas:
                    Line(rectangle=(
                        (x - (w / 2.0)) * Common.image_width,
                        (y - (h / 2.0)) * Common.image_height,
                        w * Common.image_width,
                        h * Common.image_height
                    ), width=3)


class DrawImage(Widget):
    def __init__(self, **kwargs):
        super(DrawImage, self).__init__(**kwargs)
        self.image = Image()
        self.add_widget(self.image)

    def loadImage(self, __path):
        loader = Loader.image(__path)
        loader.bind(on_load=self.setImage)

    def setImage(self, loader):
        self.image.texture = loader.image.texture
        self.image.size = self.image.texture_size


class MainApp(App):

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

        Window.size = (Common.image_width, Common.image_height)

        self._root = Widget()

        self._drawImage = DrawImage()
        self._drawImage.loadImage(Common.image_file_path)
        self._root.add_widget(self._drawImage)

        self._drawInput = DrawInput()
        self._root.add_widget(self._drawInput)


    def build(self):
        return self._root


if __name__ == "__main__":
    def makeCommon():
        Common.image_file_path = sys.argv[2]

        img = cv2.imread(Common.image_file_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            exit("Failed to load image file.")
        Common.image_height, Common.image_width = img.shape[:2]

        Common.label_file_path = sys.argv[1] + Common.image_file_path.split("/")[-1].split(".")[0] + ".txt"

    makeCommon()
    MainApp().run()
