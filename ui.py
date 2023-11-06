import sys
import cv2
import torch
from PyQt5.QtWidgets import QMainWindow, QApplication,QFileDialog
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QPixmap,QImage
from PyQt5.QtCore import QTimer
Ui_MainWindow, QMainWindow = loadUiType('main_window.ui')
def convert2Qimage(img):
    height,width,channel =img.shape
    return QImage(img,width,height,width*channel,QImage.Format_RGB888)
class mainwindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(mainwindow, self).__init__()
        self.setupUi(self)
        self.model=torch.hub.load(path="runs/train/exp28/weights/best.pt",source="local")
        self.timer=QTimer()
        self.timer.setInterval(100)
        self.bind_slots()
        self.video=None
    def image_pred(self,file_path):
        results=self.model(file_path)
        image=results.render()[0]
        return convert2Qimage(image)

    def open_image(self):
        print("点击了检测图片")
        file_path=QFileDialog.getOpenFileName(self,"./video_check/images/train",filter="*.jpg")
        if file_path[0]:
            pixmap= QPixmap(file_path[0])
            self.input.setPixmap(QPixmap(pixmap))
        #     self.output.setPixmap(QPixmap.fromImage(qimage))
        # print(file_path)
    def open_video(self):
        print("点击了检测视频")
        file_path = QFileDialog.getOpenFileName(self, dir="D:/Python/1.Python/Pycharm2021/yolov5-master/video_check/images/train",
                                                filter="*.mp4")
        if file_path[0]:
            file_path = file_path[0]
            self.video=cv2.VideoCapture(file_path)
        while True:
            ret,frame=video.read()
            if not ret:
                break
            frame =cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            qimage =self.video_pred(frame)
            self.input.setPixmap(QPixmap(convert2Qimage(frame)))
            self.output.setPixmap(QPixmap.fromImage(qimage))

    def video_pred(self, image):
        results = self.model(image)
        image = results.render()[0]
        return convert2Qimage(image)

    def bind_slots(self):
        self.image.clicked.connect(self.open_image)
        self.pushButton_2.clicked.connect(self.open_video)
        self.timer.timeout.connect(self.video_pred)
class mainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
if __name__=="__main__":
    app=QApplication(sys.argv)
    window =mainwindow()
    window.show()
    app.exec_()