# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mine_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import argparse
import random
import sys

import cv2
import numpy as np
import torch
import torch.backends.cudnn as cudnn
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileDialog

from models.experimental import attempt_load
from utils.dataloaders import letterbox
from utils.general import check_img_size, non_max_suppression,scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device
from PyQt5.QtGui import QPixmap,QImage
from PyQt5 import QtCore, QtGui, QtWidgets

global counts  # 声明 count 是全局变量



class My_Ui(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(My_Ui, self).__init__(parent)
        self.setupUi(self)
        self.timer_video = QtCore.QTimer()
        self.init_slots()
        self.cap = cv2.VideoCapture()
        self.out = None
        self.num_stop = 1

        self.openfile_name_model=None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(950, 813)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.input = QtWidgets.QLabel(self.centralwidget)
        self.input.setGeometry(QtCore.QRect(60, 60, 401, 271))
        self.input.setScaledContents(True)
        self.input.setAlignment(QtCore.Qt.AlignCenter)
        self.input.setObjectName("input")
        self.output = QtWidgets.QLabel(self.centralwidget)
        self.output.setGeometry(QtCore.QRect(520, 60, 401, 271))
        self.output.setScaledContents(True)
        self.output.setAlignment(QtCore.Qt.AlignCenter)
        self.output.setObjectName("output")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(470, 100, 61, 201))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.image = QtWidgets.QPushButton(self.centralwidget)
        self.image.setGeometry(QtCore.QRect(80, 340, 341, 28))
        self.image.setObjectName("image")
        self.video1 = QtWidgets.QPushButton(self.centralwidget)
        self.video1.setGeometry(QtCore.QRect(560, 340, 341, 28))
        self.video1.setObjectName("video1")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(200, 370, 581, 251))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.camera = QtWidgets.QPushButton(self.centralwidget)
        self.camera.setGeometry(QtCore.QRect(290, 650, 381, 28))
        self.camera.setObjectName("camera")
        self.weight = QtWidgets.QPushButton(self.centralwidget)
        self.weight.setGeometry(QtCore.QRect(290, 690, 93, 28))
        self.weight.setObjectName("weight")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 740, 821, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.init = QtWidgets.QPushButton(self.centralwidget)
        self.init.setGeometry(QtCore.QRect(440, 690, 93, 28))
        self.init.setObjectName("init")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(570, 690, 93, 28))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.input.setText(_translate("MainWindow", "显示原始图片"))
        self.output.setText(_translate("MainWindow", "显示检测结果"))
        self.image.setText(_translate("MainWindow", "图片检测"))
        self.video1.setText(_translate("MainWindow", "视频检测"))
        self.label.setText(_translate("MainWindow", "摄像头检测"))
        self.camera.setText(_translate("MainWindow", "打开摄像头"))
        self.weight.setText(_translate("MainWindow", "选择权重"))
        self.label_2.setText(_translate("MainWindow", "TextLabel"))
        self.init.setText(_translate("MainWindow", "初始化"))
        self.pushButton.setText(_translate("MainWindow", "停止"))

    #打开权重文件
    def open_model(self):
        self.openfile_name_model,_=QFileDialog.getOpenFileName(self.weight,'runs/train/exp29/wights'',''*.pt')
        if not self.openfile_name_model:
            # 这定义了消息框上显示的按钮。在这种情况下，它只显示一个“Ok”按钮，允许用户关闭消息框
            QtWidgets.QMessageBox.warning(self,u"Warning",u"权重打开失败",buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            self.label_2.setText('所选weights文件地址为：'+str(self.openfile_name_model))

    #模型初始化
    def model_init(self):
        #创建了一个解析器对象。
        parser = argparse.ArgumentParser()
        parser.add_argument('--weights', nargs='+', type=str, default='video_check/best.pt',
                            help='model path(s)')
        parser.add_argument('--source', type=str, default='data/images', help='file/dir/URL/glob, 0 for webcam')
        parser.add_argument('--data', type=str, default='data/coco128.yaml', help='(optional) dataset.yaml path')
        parser.add_argument('--img-size', nargs='+', type=int, default=640,
                            help='inference size h,w')
        parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
        parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
        parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
        parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
        parser.add_argument('--view-img', action='store_true', help='show results')
        parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
        parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
        parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
        parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
        parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
        parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
        parser.add_argument('--augment', action='store_true', help='augmented inference')
        parser.add_argument('--visualize', action='store_true', help='visualize features')
        parser.add_argument('--update', action='store_true', help='update all models')
        parser.add_argument('--project', default='runs/detect', help='save results to project/name')
        parser.add_argument('--name', default='exp', help='save results to project/name')
        parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
        parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
        parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
        parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
        #解析命令行参数，并将结果存储在 self.opt 中。打印解析后的参数。
        self.opt = parser.parse_args()
        print(self.opt)
        #默认使用’--weights‘中的权重来进行初始化
        source,weights,view_img,save_txt,imgsz=self.opt.source,self.opt.weights,self.opt.view_img,self.opt.save_txt,self.opt.img_size
        #如果openfile_name_model不为空，则使用openfile_name_model权重进行初始化
        if self.openfile_name_model:
            weights=self.openfile_name_model

        self.device=select_device(self.opt.device)
        self.half=self.device.type!='cpu'

        #提高模型的运行效率。
        cudnn.benchmark = True

        #lode model
        #这将载入模型的权重，这些权重将用于后续的操作。
        self.model=attempt_load(
            weights,device=self.device)
        #获取模型中卷积层的最大步幅
        stride=int(self.model.stride.max())
        #这行代码使用 check_img_size 函数检查图像的大小（imgsz 变量），并根据步幅 stride 进行调整。这可能是确保输入图像的尺寸与模型的步幅兼容。
        self.imgsz=check_img_size(imgsz,s=stride)
        #根据需要将模型的精度设置为半精度。
        if self.half:
            self.model.half()

        #get names and colors
        self.names = self.model.module.names if hasattr(
            self.model,'module') else self.model.names
        self.colors = [[random.randint(0,255)
                        for _ in range(3)] for _ in self.names]
        print("model initaial done")
        QtWidgets.QMessageBox.information(self,u"!",u"模型初始化成功",buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)

    #绑定信号与槽
    def init_slots(self):
        self.image.clicked.connect(self.image_open)
        self.video1.clicked.connect(self.video_open)
        self.camera.clicked.connect(self.camera_open)
        self.weight.clicked.connect(self.open_model)
        self.pushButton.clicked.connect(self.finish_detect)
        #将其连接到了 show_video_frame 方法。这意味着在每次计时器 timer_video 超时时（达到设置的时间间隔），它会触发 show_video_frame 方法的执行
        self.timer_video.timeout.connect(self.show_video_frame)
        self.init.clicked.connect(self.model_init)
        #self.timer_video.timeout.clicked.connect(self.show_video_frame)

    #打开图片
    def image_open(self):
        self.label_2.setText('图片打开成功')
        name_list=[]
        img_name,_=QtWidgets.QFileDialog.getOpenFileName(
            self,"打开图片","","*.jpg;*.png;ALL Files(*)")
        self.label_2.setText("图片路径："+img_name)
        if not img_name:
            QtWidgets.QMessageBox.warning(self,u"Warring",u"打开图片失败",buttons=QtWidgets.QMessageBox.Ok,
                                          defaultButton=QtWidgets.QMessageBox.Ok)

        img = cv2.imread(img_name)
        print(img_name)
        showimg = img
        # 开始一个不记录梯度的上下文管理器。在此上下文中的操作不会被记录到计算图中，通常用于推断阶段，以减少内存消耗和加快计算。
        with torch.no_grad():
            # 将图像调整为适合模型输入大小的尺寸。函数将返回一个包含处理后图像的列表，[0] 取出列表中的第一个元素并将其赋值给 img
            img = letterbox(img, new_shape=self.opt.img_size)[0]
            # convert
            # bgr到rgb
            img = img[:, :, ::-1].transpose(2, 0, 1)
            # 将 NumPy 数组转换为 PyTorch 张量，并确保数据是按需连续存储的：img = np.ascontiguousarray(img)
            img = np.ascontiguousarray(img)
            # 将张量从 NumPy 转换为 PyTorch 格式并送入指定的设备（GPU 或 CPU）：img = torch.from_numpy(img).to(self.device)
            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.half else img.float()
            img /= 255.0  #对图像进行归一化操作，将像素值除以 255.0：img /= 255.0
            # 如果图像张量的维度为3，则通过 unsqueeze(0) 添加了一个维度，使其成为一个四维张量
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # self.img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            # self.img = cv2.resize(
            #     img, (640, 480), interpolation=cv2.INTER_AREA)
            # self.QtImg = QtGui.QImage(
            #     self.img.data, self.img.shape[1], self.img.shape[0], QtGui.QImage.Format_RGB32)
            # self.input.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
            # self.input.setScaledContents(True)  # 图片自适应大小

            #infenence
            #使用已加载的模型 self.model 对图像张量 img 进行预测。函数调用可能返回多个预测结果，但此处只取第一个预测结果并赋值给 pred 变量。
            pred = self.model(img,augment=self.opt.augment)[0]
            #Apply NMS
            pred = non_max_suppression(pred,self.opt.conf_thres,self.opt.iou_thres,
                                       classes=self.opt.classes,agnostic=self.opt.agnostic_nms)
            print(pred)

            #process datecrions
            # 这是一个迭代循环，遍历模型预测结果列表 pred。i 是索引，det 是每个预测结果。
            for i,det in enumerate(pred):
                #这个条件语句检查当前预测结果 det 是否存在且其长度不为零。如果满足条件，则执行以下操作
                if det is not None and len(det):
                    #rescale boxs from img_size to im0 size
                    # 这行代码将检测到的边界框坐标从输入图像大小（img.shape[2:]）调整到原始图像 showing 的大小。scale_coords 函数用于缩放和调整边界框的坐标
                    det[:, :4] = scale_coords(
                        img.shape[2:],det[:, :4],showimg.shape).round()
                    #迭代循环，遍历当前检测到的边界框。det 中每个元素包含一组坐标、置信度以及类别信息
                    for *xyxy,conf,cls in reversed(det):
                        #创建一个标签字符串，包含类别名称和对应的置信度值，准备用于在边界框周围进行标注
                        label = '%s %.2f' % (self.names[int(cls)],conf)
                        name_list.append(self.names[int(cls)])
                        # 这个函数用于在图像中绘制单个边界框。它使用 xyxy 变量中的坐标信息、showing 图像，label 作为标签信息，color 表示边界框颜色，line_thickness 表示边界框线条粗细。
                        plot_one_box(xyxy,showimg,label=label,
                                     color=self.colors[int(cls)],line_thickness=2)
        #保存经处理后的图像（在 showing 中）为名为 prediction.jpg 的图像文件
        cv2.imwrite('prediction.jpg', showimg)
        #这行代码将图像从 BGR 格式转换为 BGRA 格式，并将结果存储在 self.result 变量中。
        self.result = cv2.cvtColor(showimg,cv2.COLOR_BGR2BGRA)
        #调整 self.result 中的图像大小为 640x480 像素，使用的插值方法为 cv2.INTER_AREA，这是一种插值方法，适合缩小图像。
        self.result=cv2.resize(
            self.result,(640,480),interpolation=cv2.INTER_AREA)
        #创建了一个 Qt 图像对象 QtImg，将处理后的结果（self.result）转换为 Qt 支持的图像格式 QtGui.QImage.Format_RGB32
        self.QtImg=QtGui.QImage(
            self.result.data,self.result.shape[1],self.result.shape[0],QtGui.QImage.Format_RGB32)
        # 将 Qt 图像转换为可显示的图像，并使用 setPixmap() 方法将其设置为输出。
        self.output.setPixmap(QtGui.QPixmap.fromImage(self.QtImg))
        self.output.setScaledContents(True)  #图片自适应大小

    # 打开视频
    def video_open(self):
        video_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "打开视频", "", "*.mp4;;*.avi;;All Files(*)")
        self.label_2.setText("视频地址：" + video_name)
        #这行代码尝试打开指定路径的视频文件。self.cap 可能是一个视频捕获对象。flag 变量将会返回一个布尔值，表明视频是否成功打开。
        flag = self.cap.open(video_name)
        if flag == False:
            QtWidgets.QMessageBox.warning(
                self, u"Warning", u"打开视频失败", buttons=QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
        else:
            #创建一个视频写入对象 self.out，将预测结果写入一个名为 prediction.avi 的视频文件。
            # 视频的编解码器使用了 MJPG（Motion JPEG 编解码器）。帧率设置为 20，分辨率为视频原始宽高（通过 self.cap.get(3) 和 self.cap.get(4) 获取）
            self.out = cv2.VideoWriter('prediction.avi', cv2.VideoWriter_fourcc(
                *'MJPG'), 20, (int(self.cap.get(3)), int(self.cap.get(4))))
            self.timer_video.start(30)
            # 进行视频识别时，关闭其他按键点击功能
            self.video1.setDisabled(True)
            self.image.setDisabled(True)
            self.camera.setDisabled(True)
            self.init.setDisabled(True)
            self.weight.setDisabled(True)
            self.label.setScaledContents(True)


    # 显示视频帧
    def show_video_frame(self):
        name_list = []
        flag, img = self.cap.read()
        if img is not None:
            showimg = img
            with torch.no_grad():
                img = letterbox(img, new_shape=self.opt.img_size)[0]
                # Convert
                # BGR to RGB, to 3x416x416
                img = img[:, :, ::-1].transpose(2, 0, 1)
                img = np.ascontiguousarray(img)
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.half else img.float()  # uint8 to fp16/32
                img /= 255.0  # 0 - 255 to 0.0 - 1.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)
                # Inference
                pred = self.model(img, augment=self.opt.augment)[0]

                # Apply NMS
                pred = non_max_suppression(pred, self.opt.conf_thres, self.opt.iou_thres, classes=self.opt.classes,
                                           agnostic=self.opt.agnostic_nms)

                global total_counts
                global count1
                global count2
                global count3

                total_counts = 0
                count1 = 0
                count2 = 0
                count3 = 0

                #Process detections
                for i, det in enumerate(pred):  # detections per image
                    if det is not None and len(det):
                        # Rescale boxes from img_size to im0 size
                        det[:, :4] = scale_coords(
                            img.shape[2:], det[:, :4], showimg.shape).round()

                        # Write results
                        count3 = count2 - count1
                        count2 = count1
                        count1 = 0

                        if count3 > 0:
                            total_counts = total_counts + count3
                        else:
                            total_counts = total_counts

                        # Write results
                        for *xyxy, conf, cls in reversed(det):
                            count1 += 1
                            label = '%s %.2f' % (self.names[int(cls)], conf)
                            name_list.append(self.names[int(cls)])
                            self.label_2.setText(label)  # PyQT页面打印类别和置信度
                            plot_one_box(
                                xyxy, showimg, label=label, color=self.colors[int(cls)], line_thickness=2)
            self.out.write(showimg)
            show = cv2.resize(showimg, (640, 480))
            self.result = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(self.result.data, self.result.shape[1], self.result.shape[0],
                                     QtGui.QImage.Format_RGB888)
            self.output.setPixmap(QtGui.QPixmap.fromImage(showImage))
            # self.input.setPixmap(QtGui.QPixmap.fromImage(img))

            # cv2.putText(pred, f'Total detections: {total_counts}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
            #             (0, 255, 0), 2)
            lab = '%.2f' % (total_counts)
            self.label.setText(lab)

        else:
            self.timer_video.stop()
            self.cap.release()
            self.out.release()
            self.output.clear()

            # 视频帧显示期间，禁用其他检测按键功能
            self.video1.setDisabled(False)
            self.image.setDisabled(False)
            self.camera.setDisabled(False)
            self.init.setDisabled(False)
            self.weight.setDisabled(False)

        # 摄像头检测
    def camera_open(self):
        if not self.timer_video.isActive():
            # 默认使用第一个本地camera
            flag = self.cap.open(0)
            if flag == False:
                QtWidgets.QMessageBox.warning(
                    self, u"Warning", u"打开摄像头失败", buttons=QtWidgets.QMessageBox.Ok,
                    defaultButton=QtWidgets.QMessageBox.Ok)
            else:
                self.out = cv2.VideoWriter('prediction.avi', cv2.VideoWriter_fourcc(
                    *'MJPG'), 20, (int(self.cap.get(3)), int(self.cap.get(4))))
                self.timer_video.start(30)
                self.video1.setDisabled(True)
                self.image.setDisabled(True)
                self.init.setDisabled(True)
                self.weight.setDisabled(True)
                self.pushButton.setDisabled(True)
                # self.pushButton_finish.setDisabled(True)
                self.camera.setText(u"关闭摄像头")
        else:
            self.timer_video.stop()
            self.cap.release()
            self.out.release()
            self.label.clear()
            self.video1.setDisabled(False)
            self.image.setDisabled(False)
            self.init.setDisabled(False)
            self.weight.setDisabled(False)
            self.pushButton.setDisabled(False)
            # self.pushButton_finish.setDisabled(False)
            self.camera.setText(u"摄像头检测")
    #结束视频
    def finish_detect(self):
        self.cap.release()  # 释放video_capture资源
        self.out.release()  # 释放video_writer资源
        self.label.clear()  # 清空label画布
        # 启动其他检测按键功能
        self.video1.setDisabled(False)
        self.image.setDisabled(False)
        self.camera.setDisabled(False)
        self.init.setDisabled(False)
        self.weight.setDisabled(False)

        # 结束检测时，查看暂停功能是否复位，将暂停功能恢复至初始状态
        # Note:点击暂停之后，num_stop为偶数状态
        if self.num_stop % 2 == 0:
            self.pushButton_stop.setText(u'暂停')
            self.num_stop = self.num_stop + 1
            self.timer_video.blockSignals(False)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui=My_Ui()
    ui.show()
    sys.exit(app.exec_())





