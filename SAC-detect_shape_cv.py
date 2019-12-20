from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui  import QPainter, QBrush, QPen, QColor, QImage, QMouseEvent
from PyQt5.QtCore import Qt
import sys
import enum

import cv2
import numpy as np

class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        peri   = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        # print("approx: " + str(approx))
        alen = len(approx)
        if alen == 3:
            return "triangle";
        elif alen == 4:
            return "square"
        elif alen == 5:
            return "pentagon"
        elif alen > 5:
            return "circle"
        else:
            return "unknown"

class State(enum.Enum):
    SHOW = 0
    DRAW = 1

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title  = "Assisted drawing"
        self.top    = 100
        self.left   = 150
        self.width  = 500
        self.height = 500
        self.last_x = None
        self.last_y = None
        self.state  = State.SHOW
        self.initWindow()
        self.overlayImage = QImage(self.width, self.height, QImage.Format_ARGB32)
        self.mainImage    = QImage(self.width, self.height, QImage.Format_RGB32)
        self.drawShape()

    def initWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()

    def drawShape(self):
        painter = QPainter()
        painter.begin(self.overlayImage)
        pen = QPen()
        pen.setWidth(8)
        pen.setColor(QColor(0, 255, 0))
        painter.setPen(pen)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        # painter.drawEllipse(40, 40, 200, 200)
        painter.end()

    def mouseMoveEvent(self, event):
        print("x: " + str(event.x()) + "; y: " + str(event.y()))
        if self.last_x is None:
            self.last_x = event.x()
            self.last_y = event.y()
            '''находим начальные точки'''
            return

        painter = QPainter(self.overlayImage)
        pen = QPen()
        pen.setWidth(8)
        pen.setColor(QColor(0, 255, 0))
        painter.setPen(pen)
        painter.drawLine(self.last_x, self.last_y, event.x(), event.y())
        painter.end()
        self.update()
        self.last_x = event.x()
        self.last_y = event.y()
        self.repaint()

    def mousePressEvent(self, event):
        self.last_x = event.x()
        self.last_y = event.y()
        self.state = State.DRAW

    def mouseReleaseEvent(self, event):
        img     = self.qImageToMat(self.overlayImage)
        gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gray    = cv2.convertScaleAbs(gray)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh  = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
        contours, hier    = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # print(cnts)
        sd      = ShapeDetector()
        for c in contours:
            shape = sd.detect(c)
            if shape == "unknown":
                continue
            m = cv2.moments(c)
            if m["m00"] == 0.0:
                continue
            print(m)
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            cv2.drawContours(img, [c], -1, (255, 0, 0), 2)
            cv2.putText(img, shape, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            # cv2.imshow("Image", img)
            # cv2.waitKey(0)
        height, width, channel = img.shape
        self.mainImage = QImage(img.data, width, height, img.strides[0], QImage.Format_ARGB32)
        # print(self.overlayImage)
        self.state = State.SHOW
        self.repaint()

    def qImageToMat(self, img):
        img    = img.convertToFormat(QImage.Format_RGB32)
        width  = img.width()
        height = img.height()
        ptr    = img.bits()
        ptr.setsize(img.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        return arr

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        if self.state == State.SHOW:
            painter.drawImage(0, 0, self.mainImage)
        else:
            painter.drawImage(0, 0, self.overlayImage)

        # painter.drawImage(0, 0, self.overlayImage)
        painter.end()

def main(argv):
    app = QApplication(argv)
    window = Window()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)


#  LocalWords:  artyom poptsov gmail


# 23 december 15 
# прислать до 27 декабря описание проекта
        # aprc2@yandex.ru
