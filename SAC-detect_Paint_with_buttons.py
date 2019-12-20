from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QLabel()
        '''виджет для отображения холста'''
        canvas = QPixmap(400, 300)
        #self.clr = None
        self.r = 200
        self.g = 0
        self.b = 0
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.printButtonRed()
        self.printButtonBlue()
        self.printButtonGreen()
        self.b1.clicked.connect(self.red_color)
        self.b2.clicked.connect(self.blue_color)
        self.b3.clicked.connect(self.green_color)
        self.last_x, self.last_y = None, None

        '''переменные для хранение предыдущих точек для отрисовки линий'''

    def printButtonRed(self):
        self.b1 = QPushButton(self)
        self.b1.resize(25,25)
        self.b1.move(375,275)
        self.b1.setStyleSheet("background-color: red")

    def printButtonBlue(self):
        self.b2 = QPushButton(self)
        self.b2.resize(25,25)
        self.b2.move(375,250)
        self.b2.setStyleSheet("background-color: blue")

    def printButtonGreen(self):
        self.b3 = QPushButton(self)
        self.b3.resize(25,25)
        self.b3.move(375,225)
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

    def mouseMoveEvent(self, e):
        if self.last_x is None:
            self.last_x = e.x()
            self.last_y = e.y()
            '''находим начальные точки'''
            return

        painter = QPainter(self.label.pixmap())
        pen = QPen()
        pen.setWidth(3)
        '''устанавливаем ширину ручки'''
        pen.setColor(QColor(self.r, self.g, self.b))
        '''присваиваем ручке цвет'''
        painter.setPen(pen)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        '''рисуем линию от начальной до нынешней точки в единицу времени'''
        painter.end()
        '''закрываем принтер'''
        self.update()
        '''обновляем окно'''

        self.last_x = e.x()
        self.last_y = e.y()
        '''теперь наши конечные точки станут начальными для следующей линии'''

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None
        '''при отпускании клавиши мыши присваиваем начальным позициям none'''


def main(argv):
    app = QApplication(argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main(sys.argv)
