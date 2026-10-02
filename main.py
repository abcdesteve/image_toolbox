from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PIL import Image, ImageFilter, ImageQt, ImageSequence
import sys
import char
import sketch
from ui_gui import Ui_gui

class Main(QMainWindow,Ui_gui):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.choose.clicked.connect(self.open_file)
        self.render.clicked.connect(self.process)
        self.save.clicked.connect(self.save_file)
        self.img=None
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

        self.show()

    def open_file(self):
        path=QFileDialog.getOpenFileName(caption='打开图片',filter='(*.jpg *.png *.bmp *.gif)')[0]
        if path:
            self.img=Image.open(path)
            if path[-4:] == '.gif':
                self.img = ImageSequence.Iterator(self.img)
                self.before.setPixmap(QPixmap.fromImage(
                    ImageQt.ImageQt(self.img[0].resize((360, 240)))))
                self.width_limit.setValue(self.img[0].width)
                self.height_limit.setValue(self.img[0].height)
            else:
                self.before.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(self.img.resize((360, 240)))))
                self.width_limit.setValue(self.img.width)
                self.height_limit.setValue(self.img.height)
            self.path.setText(path)

        else:
            QMessageBox.warning(self, '警告','请重新选择图片文件')

    def process(self):
        if self.img:            
            if self.path.text()[-4:] == '.gif':
                self.img = [temp.resize((self.width_limit.value(), self.height_limit.value())).convert(self.color_mode.currentText()) for temp in self.img]
            else:
                self.img = self.img.resize((int(self.width_limit.text()), int(self.height_limit.text()))).convert(self.color_mode.currentText())

            mode = self.filter_mode.currentIndex()
            if mode != 0:
                if mode<13:
                    if self.path.text()[-4:] == '.gif':
                        lis=[temp.filter(self.filters[mode-1]) for temp in self.img]
                        self.img=lis
                    else:
                        self.img=self.img.filter(self.filters[mode-1])
                elif mode == 13:
                    if self.path.text()[-4:] == '.gif':
                        lis=[sketch.sketch(temp) for temp in self.img]
                        self.img = lis
                    else:
                        self.img=sketch.sketch(self.img)
                else:
                    if self.path.text()[-4:] == '.gif':
                        lis = [char.char(temp) for temp in self.img]
                        self.img = lis
                    else:
                        self.img = char.char(self.img)
            if self.path.text()[-4:] == '.gif':
                self.after.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(self.img[0].resize((360, 240)))))
            else:
                self.after.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(self.img.resize((360, 240)))))
        else:
            QMessageBox.warning(self,'警告','请先打开一张图片')

    def save_file(self):
        if self.img:
            path = QFileDialog.getSaveFileName(caption='保存图片', filter='(*.png *.jpg *.bmp *.gif)')[0]
            if path:
                if self.path.text()[-4:] == '.gif':
                    if path[-4:] == '.jpg':
                        frame = self.img[0].convert('RGB')
                        frame.save(path)
                    elif path[-4:] == '.gif':
                        frame = [temp.convert('RGBA') for temp in self.img]
                        frame[0].save(path, append_images=self.img[1:], save_all=True, loop=0)
                    else:
                        frame = self.img[0].convert('RGBA')
                        frame.save(path)
                else:
                    if path[-4:] == '.jpg':
                        frame = self.img.convert('RGB')
                        frame.save(path)
                    else:
                        frame = self.img.convert('RGBA')
                        frame.save(path)
            else:
                QMessageBox.warning(self, '警告', '请先重新选保存位置')
        else:
            QMessageBox.warning(self, '警告', '请先进行图像处理')

    def keyPressEvent(self,event):
        if event.key()==Qt.Key_F1:
            try:
                if self.path.text()[-4:] == '.gif':
                    self.after.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(self.img[0].resize((360, 240)))))
                else:
                    self.after.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(self.img.resize((360, 240)))))
            except:
                QMessageBox.warning(self,'警告','请先进行图像处理')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec_())
