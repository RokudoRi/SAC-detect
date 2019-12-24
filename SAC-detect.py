from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtGui  import QPainter, QPen, QColor, QImage, QPolygon
from PyQt5.QtCore import QPoint
import sys
import enum
import cv2
import imutils
import numpy as np
from scipy.interpolate import splprep, splev

OPENCV_VERSION = cv2.__version__.split(".")[0]


class Shape(enum.Enum):
    UNKNOWN  = 0
    TRIANGLE = 1
    SQUARE   = 2
    PENTAGON = 3
    CIRCLE   = 4


class ShapeDetector:
    def __init__(self):
        pass

    def detect(self, c):
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        alen = len(approx)
        shape = Shape.UNKNOWN
        if alen == 3:
            shape = Shape.TRIANGLE
        elif alen == 4:
            shape = Shape.SQUARE
        elif alen == 5:
            shape = Shape.PENTAGON
        elif alen > 5:
            shape = Shape.CIRCLE
        print(alen)
        print(shape)
        return (shape, approx)


class State(enum.Enum):
    SHOW = 0
    DRAW = 1


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Assisted drawing"
        self.r, self.g, self.b = 0, 0, 0
        self.top = 100
        self.left = 150
        self.width = 500
        self.height = 500
        self.last_x = None
        self.last_y = None
        self.state = State.SHOW
        self.initWindow()
        self.overlayImage = QImage(self.width, self.height, QImage.Format_ARGB32_Premultiplied)
        self.mainImage = QImage(self.width, self.height, QImage.Format_RGB32)
        self.clearOverlayImage()
        self.clearMainImage()

    def initWindow(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.printButtonRed()
        self.printButtonBlue()
        self.printButtonGreen()
        self.b1.clicked.connect(self.red_color)
        self.b2.clicked.connect(self.blue_color)
        self.b3.clicked.connect(self.green_color)

        self.show()

    def printButtonRed(self):
        self.b1 = QPushButton(self)
        self.b1.resize(25,25)
        self.b1.move(self.width - 25, self.height - 25)
        self.b1.setStyleSheet("background-color: red")

    def printButtonBlue(self):
        self.b2 = QPushButton(self)
        self.b2.resize(25,25)
        self.b2.move(self.width - 25, self.height - 50)
        self.b2.setStyleSheet("background-color: blue")

    def printButtonGreen(self):
        self.b3 = QPushButton(self)
        self.b3.resize(25,25)
        self.b3.move(self.width - 25, self. height - 75)
        self.b3.setStyleSheet("background-color: green")

    def red_color(self):
        self.r = 200
        self.g = 0
        self.b = 0
        print('red')

    def blue_color(self):
        self.r = 0
        self.g = 0
        self.b = 200
        print('blue')

    def green_color(self):
        self.r = 0
        self.g = 200
        self.b = 0
        print('green')

    def clearOverlayImage(self):
        painter = QPainter()
        painter.begin(self.overlayImage)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        painter.end()

    def clearMainImage(self):
        painter = QPainter()
        painter.begin(self.mainImage)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        painter.end()

    def mouseMoveEvent(self, event):
        if self.last_x is None:
            self.last_x = event.x()
            self.last_y = event.y()
            return

        painter = QPainter(self.overlayImage)
        pen = QPen()
        pen.setWidth(8)
        pen.setColor(QColor(self.r, self.g, self.b))
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

    def smoothContour(self, contour):
        x, y = contour.T
        x = x.tolist()[0]
        y = y.tolist()[0]
        tck, u = splprep([x, y], u=None, s=5.0, per=1)
        u_new = np.linspace(u.min(), u.max(), 25)
        x_new, y_new = splev(u_new, tck, der=0)
        res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new, y_new)]
        return np.asarray(res_array, dtype=np.int32)

    def mouseReleaseEvent(self, event):
        img = self.qImageToMat(self.overlayImage)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.threshold(blurred, 1, 255, cv2.THRESH_BINARY)[1]

        if OPENCV_VERSION == "3":
            image, contours, hier = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        elif OPENCV_VERSION == "4":
            contours, hier = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        else:
            raise Exception("Unsupported OpenCV version: " + str(OPENCV_VERSION))

        sd = ShapeDetector()
        for c in contours:
            shape, approx = sd.detect(c)
            if shape == "unknown":
                continue
            m = cv2.moments(c)
            if m["m00"] == 0.0:
                continue
            # print(m)
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            painter = QPainter()
            pen = QPen()

            painter.begin(self.mainImage)
            pen.setWidth(8)
            pen.setColor(QColor(self.r, self.g, self.b))
            painter.setPen(pen)

            if shape == Shape.CIRCLE:
                painter.drawEllipse(cx, cy, 50, 50)
            elif shape == Shape.SQUARE:
                #x, y, width, height = cv2.boundingRect(c)
                painter.drawRect(cx, cy, 50, 50)
            elif shape == Shape.TRIANGLE:
                painter.drawPolygon(QPolygon(map(lambda x: QPoint(x[0][0], x[0][1]), approx)))

            painter.end()

        self.clearOverlayImage()
        self.state = State.SHOW
        self.repaint()

    def qImageToMat(self, img):
        img = img.convertToFormat(QImage.Format_RGB32)
        width = img.width()
        height = img.height()
        ptr = img.bits()
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

        painter.end()


def main(argv):
    app = QApplication(argv)
    window = Window()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
