from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import *
from kivy.loader import Loader
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel

import copy
import cv2
import sys
import os
import fcntl


class Common:
    # please set class of image
    image_categories = [
        ("2", "sticky"),
        ("3", "heart"),
        ("4", "clock"),
        ("5", "thema"),
        ("6", "idea"),
        ("7", "ai"),
        ("8", "cookie_heart"),
        ("9", "cookie_clock"),
        ("10", "cookie_thema"),
        ("11", "cookie_idea"),
        ("12", "cookie_ai"),
    ]

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

        self.drawTeacherData()
        with self.canvas:
            Color(0, 1, 1)
            Line(rectangle=(
                self._touch_down_point.x,
                self._touch_down_point.y,
                self._touch_move_point.x - self._touch_down_point.x,
                self._touch_move_point.y - self._touch_down_point.y
            ))


    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def on_key_down(self, keyboard, keycode, text, modifiers):
        print(keycode)

        if keycode[1] == 'd':
            self.drawTeacherData()
            return

        if keycode[1] == 'z':
            self.deleteLastLine()
            return

        if keycode[1] == 'c':
            self.canvas.clear()
            return

        for category in Common.image_categories:
            print keycode[1],category[0]
            if(keycode[1] == category[0]):
                self.saveTeacherData(category)
                return

        if keycode[1] == 'r':
            self.saveTeacherData(Common.image_categories[6])
            return

        if keycode[1] == 't':
            self.saveTeacherData(Common.image_categories[7])
            return

        if keycode[1] == 'y':
            self.saveTeacherData(Common.image_categories[8])
            return

        if keycode[1] == 'u':
            self.saveTeacherData(Common.image_categories[9])
            return

        if keycode[1] == 'i':
            self.saveTeacherData(Common.image_categories[10])
            return


    def saveTeacherData(self, __category):
        if (self._touch_down_point == []):
            return

        category_id = __category[0]
        teacher_data = category_id + " " + \
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

    def deleteLastLine(self):
        lines = []
        with open(Common.label_file_path) as f:
            for line in f:
                lines.append(line)

        with open(Common.label_file_path, 'w') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            for i in range(0, len(lines) - 1):
                f.write(lines[i])

        self.drawTeacherData()

    def drawTeacherData(self):
        self.canvas.clear()

        print Common.label_file_path
        if (os.path.isfile(Common.label_file_path) != True):
            return

        with open(Common.label_file_path) as f:
            for line in f:
                data = line.split(" ")
                if (len(data) < 5):
                    return
                x = float(data[1])
                y = 1.0 - float(data[2])
                w = float(data[3])
                h = float(data[4])
                with self.canvas:
                    rectX = (x - (w / 2.0)) * Common.image_width
                    rectY = (y - (h / 2.0)) * Common.image_height
                    rectWidth = w * Common.image_width
                    rectHeight = h * Common.image_height
                    Line(rectangle=(rectX, rectY, rectWidth, rectHeight), width=3)

                    label = CoreLabel()
                    label.text = "missing"
                    for category in Common.image_categories:
                        category_id =  category[0]
                        if(category_id == data[0]):
                            label.text = category[1]

                    label.font_size = 20
                    label.refresh()
                    text = label.texture
                    textX = int(rectX + rectWidth / 2 - text.size[0] / 2)
                    textY = int(rectY + rectHeight / 2 - text.size[1] / 2)
                    Rectangle(size=text.size, pos=(textX, textY), texture=text)


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
