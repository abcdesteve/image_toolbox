import sys

import numpy
from PIL import Image, ImageEnhance, ImageFilter, ImageQt, ImageSequence
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import addon
from ui_adjust import Ui_adjust
from ui_gui import Ui_gui

color_mode_map = {'二值化': 'L', '1': '1', 'L': 'L', 'HSV': 'HSV',
                  'RGBA': 'RGBA', 'CMYK': 'CMYK', 'YCbCr': 'YCbCr'}


class Adjust(QMainWindow, Ui_adjust):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.render.clicked.connect(self.mapping)
        self.reset_1.clicked.connect(self.r1)
        self.reset_2.clicked.connect(self.r2)
        self.reset_3.clicked.connect(self.r3)
        self.reset_4.clicked.connect(self.r4)
        self.brightness_reset.clicked.connect(self.rb)
        self.contrast_reset.clicked.connect(self.rc)
        self.slider_1.valueChanged.connect(self.value_update)
        self.slider_2.valueChanged.connect(self.value_update)
        self.slider_3.valueChanged.connect(self.value_update)
        self.slider_4.valueChanged.connect(self.value_update)
        self.contrast_slider.valueChanged.connect(self.value_update)
        self.brightness_slider.valueChanged.connect(self.value_update)

        global color_mode_map
        self.color_mode_map = color_mode_map

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def mapping(self):
        global img, window
        try:
            if type(img[-1]) == list:
                img.append(list(map(self.change, img[-1])))
            else:
                img.append(self.change(img[-1]))
        except Exception as e:
            QMessageBox.warning(self, '警告', f'调色时发生未知错误\n{e}')
        finally:
            window.updateImage()

    def change(self, img):
        global window
        try:
            height, width = img.height, img.width
            img = numpy.array(img.convert('RGBA')).reshape([height, width, 4])
            if self.invert.isChecked():
                temp = img[:, :, 3]
                img = numpy.array(255)-img
                img[:, :, 3] = temp
            img = numpy.array(Image.fromarray(numpy.uint8(img)).convert(
                self.color_mode_map[window.color_mode.currentText()]))
            # uint & int 转换时保证不超限则不改变数据 uint8(255)==>int16(255) int8超限
            img = numpy.int32(img)
            img += numpy.array([self.slider_1.value(), self.slider_2.value(),
                               self.slider_3.value(), self.slider_4.value()][:([1, 1, 1, 3, 4, 4, 3][window.color_mode.currentIndex()])])
            img[img < 0] = 0
            img[img > 255] = 255
            img = Image.fromarray(numpy.uint8(
                img), self.color_mode_map[window.color_mode.currentText()])
            img = ImageEnhance.Contrast(img).enhance(
                self.contrast_slider.value()/100)
            img = ImageEnhance.Brightness(img).enhance(
                self.brightness_slider.value()/100)

        except Exception as e:
            QMessageBox.warning(self, '警告', f'未打开文件或文件损坏\n{e}')

        finally:
            return img

    def show(self):
        try:
            for i in range(4):
                [self.label_1, self.label_2, self.label_3,
                    self.label_4][i].setText('  偏移量：')
            if type(img[-1]) == list:
                temp = img[-1][0]
            else:
                temp = img[-1]
            replace = self.color_mode_map[temp.mode]
            for i in range(len(replace)):
                [self.label_1, self.label_2, self.label_3,
                    self.label_4][i].setText(f'{replace[i]} 偏移量：')
            self.value_update()
            super().show()
        except:
            QMessageBox.warning(self, '警告', '请先进行图片处理')

    def r1(self):
        self.slider_1.setValue(0)

    def r2(self):
        self.slider_2.setValue(0)

    def r3(self):
        self.slider_3.setValue(0)

    def r4(self):
        self.slider_4.setValue(0)

    def rb(self):
        self.brightness_slider.setValue(100)

    def rc(self):
        self.contrast_slider.setValue(100)

    def value_update(self):
        self.label_1.setText(self.label_1.text()[
                             :6]+str(self.slider_1.value()))
        self.label_2.setText(self.label_2.text()[
                             :6]+str(self.slider_2.value()))
        self.label_3.setText(self.label_3.text()[
                             :6]+str(self.slider_3.value()))
        self.label_4.setText(self.label_4.text()[
                             :6]+str(self.slider_4.value()))
        self.contrast_label.setText(f'对比度：{self.contrast_slider.value()}%')
        self.brightness_label.setText(
            f'亮度：{self.brightness_slider.value()}%')


class Main(QMainWindow, Ui_gui):
    def __init__(self):
        global img
        super().__init__()
        self.setupUi(self)
        self.adjust = Adjust()

        self.choose.clicked.connect(self.open_file)
        self.render.clicked.connect(self.process)
        self.save.clicked.connect(self.save_file)
        self.open_adjust.clicked.connect(self.adjust.show)
        img = []
        self.recycle = []
        self.filters = [
            ImageFilter.BLUR,
            ImageFilter.CONTOUR,
            ImageFilter.DETAIL,
            ImageFilter.EDGE_ENHANCE,
            ImageFilter.EDGE_ENHANCE_MORE,
            ImageFilter.EMBOSS,
            ImageFilter.FIND_EDGES,
            ImageFilter.GaussianBlur,
            ImageFilter.SHARPEN,
            ImageFilter.SMOOTH,
            ImageFilter.SMOOTH_MORE,
            ImageFilter.UnsharpMask
        ]

        global color_mode_map
        self.color_mode_map = color_mode_map

        self.show()

    def open_file(self):
        global img
        path = QFileDialog.getOpenFileName(
            caption='打开图片', filter='*.jpg *.png *.bmp *.gif;;*.jpg;;*.png;;*.bmp;;*.gif')[0]
        if path:
            if img:
                flag = 1
            else:
                flag = 2
            for i in range(flag):
                if path[-4:] == '.gif':
                    # 打开gif为特殊格式 用seek跳转 此处转为列表
                    img.append([temp.convert('RGBA') for temp in list(
                        ImageSequence.Iterator(Image.open(path)))])
                    self.width_limit.setValue(img[-1][0].width)
                    self.height_limit.setValue(img[-1][0].height)
                else:
                    img.append(Image.open(path))
                    self.width_limit.setValue(img[-1].width)
                    self.height_limit.setValue(img[-1].height)
            self.path.setText(path)
            self.updateImage()

        else:
            QMessageBox.warning(self, '警告', '请重新选择图片文件')

    def process(self):
        global img
        try:
            if type(img[-1]) == list:
                if self.color_mode.currentIndex() == 0:  # 二值化模式
                    lis = list
                    for temp in img[-1]:
                        temp = temp.resize(
                            (self.width_limit.value(), self.height_limit.value()))
                        temp = numpy.array(temp.convert('L')).reshape(
                            [self.height_limit.value(), self.width_limit.value()])  # array中先列后行
                        temp[temp <= 127] = 0
                        temp[temp > 127] = 255
                        temp = Image.fromarray(numpy.uint8(temp), 'L')
                        lis.append(temp)
                    img.append(lis)
                else:
                    img.append([temp.resize((self.width_limit.value(), self.height_limit.value())).convert(
                        self.color_mode.currentText()) for temp in img[-1]])
            else:
                if self.color_mode.currentIndex() == 0:  # 二值化模式
                    temp = img[-1]
                    temp = temp.resize(
                        (self.width_limit.value(), self.height_limit.value()))
                    temp = numpy.array(temp.convert('L')).reshape(
                        [self.height_limit.value(), self.width_limit.value()])  # array中先列后行
                    temp[temp <= 127] = 0
                    temp[temp > 127] = 255
                    temp = Image.fromarray(numpy.uint8(temp), 'L')
                    img.append(temp)
                else:
                    img.append(img[-1].resize((int(self.width_limit.text()), int(
                        self.height_limit.text()))).convert(self.color_mode.currentText()))

            mode = self.filter_mode.currentIndex()
            if mode != 0:
                if mode == 14:
                    if type(img[-1]) == list:
                        img.append(list(map(addon.char, img.pop(-1))))
                    else:
                        img.append(addon.char(img.pop(-1)))
                elif mode == 13:
                    if type(img[-1]) == list:
                        img.append(list(map(addon.sketch, img.pop(-1))))
                    else:
                        img.append(addon.sketch(img.pop(-1)))
                else:
                    if type(img[-1]) == list:
                        img.append([temp.filter(self.filters[mode-1])
                                    for temp in img.pop(-1)])
                    else:
                        img.append(img.pop(-1).filter(self.filters[mode-1]))
            self.updateImage()
        except Exception as e:
            QMessageBox.warning(self, '警告', f'请先打开一张图片\n{e}')

    def save_file(self):
        global img
        try:
            if len(img) < 2:
                QMessageBox.warning(self, '警告', '请先进行图片处理')
                return
            path = QFileDialog.getSaveFileName(
                caption='保存图片', filter='*.jpg *.png *.bmp *.gif;;*.jpg;;*.png;;*.bmp;;*.gif')[0]
            if path:
                if type(img[-1]) == list:
                    if path[-3:] == 'gif':
                        img[-1][0].save(
                            path, append_images=img[-1][1:], save_all=True, loop=0)
                    elif path[-3:] == 'jpg' and img[-1][0].mode == 'RGBA':
                        img[-1][0].convert('RGB').save(path)
                    else:
                        img[-1][0].save(path)
                else:
                    if path[-3:] == 'jpg' and img[-1].mode == 'RGBA':
                        img[-1].convert('RGB').save(path)
                    else:
                        img[-1].save(path)
            else:
                QMessageBox.warning(self, '警告', '请先重新选保存位置')
        except Exception as e:
            QMessageBox.warning(
                self, '警告', f'请检查图像格式\n\njpg --> 二值化(L) 1 L HSV RGB(RGBA自动转换) CMYK YCbCr\npng bmp gif --> L RGBA\n\n{e}')

    def updateImage(self):
        global img
        try:
            if type(img[-2]) == list:
                self.before.setPixmap(QPixmap.fromImage(
                    ImageQt.ImageQt(img[-2][0].convert('RGBA'))))
            else:
                self.before.setPixmap(QPixmap.fromImage(
                    ImageQt.ImageQt(img[-2].convert('RGBA'))))
            if type(img[-1]) == list:
                self.after.setPixmap(QPixmap.fromImage(
                    ImageQt.ImageQt(img[-1][0].convert('RGBA'))))
            else:
                self.after.setPixmap(QPixmap.fromImage(
                    ImageQt.ImageQt(img[-1].convert('RGBA'))))
        except Exception as e:
            QMessageBox.warning(self, '警告', f'更新图像时发生未知错误\n{e}')

    def keyPressEvent(self, event):
        global img
        try:
            if event.key() == Qt.Key_F1:
                self.updateImage()
            if event.key() == Qt.Key_F2:
                self.recycle.append(img.pop(-1))
                self.updateImage()
            if event.key() == Qt.Key_F3:
                img.append(self.recycle.pop(-1))
                self.updateImage()
        except Exception as e:
            QMessageBox.warning(self, '警告', f'请先进行图像处理\n{e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec_())
