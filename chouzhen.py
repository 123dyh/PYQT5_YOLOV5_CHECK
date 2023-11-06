import cv2  #调用opencv库
import matplotlib.pyplot as plt
#调用Matplotlib库，他是一个用于创建图表、绘制图形和可视化数据的强大库
video =cv2.VideoCapture("./BVN.mp4")
#创建了一个名为 video 的视频捕获对象，用于打开和读取视频文件 "BVN.mp4"
ret,frame =video.read()
#从视频捕获对象 video 中读取一帧视频，并将该帧存储在 frame 变量中，ret 和 frame。ret 是一个布尔值，表示读取是否成功，如果成功读取帧，则为 True，否则为 False。frame 是一个包含帧像素数据的NumPy数组。
plt.imshow(frame)
#显示OpenCV中读取的视频帧
plt.imshow(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
#由于opencv读取图像采用的是BGR的通道顺序，使用此行代码可以将BRG改成RGB
num=0
#创建一个计数器，用于跟踪帧的数量。
save_step=30
#表示保存帧的间隔。在这个示例中，每隔30帧保存一帧
while True:  #无限循环，用于连续读取视频的帧
    ret,frame=video.read()
    if not ret:  #检查是否成功读取帧。如果 ret 为 False，表示已经读取到视频的末尾，循环会被终止，代码退出。
        break
    num+=1  #如果成功读取了一帧，计数器 num 会递增
    if num%save_step == 0:  #检查当前帧的编号是否是 save_step 的倍数。如果是，表示已经达到了保存帧的间隔。
        cv2.imwrite("./images/"+str(num)+".jpg",frame)
        #如果满足条件，就使用OpenCV的 imwrite() 函数将当前帧 frame 保存为JPEG图像文件。文件名根据当前帧的编号命名，保存在"./images/"目录下
