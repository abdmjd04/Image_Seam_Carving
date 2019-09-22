from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget, QVBoxLayout
import sys
import os
import desginFull
import cv2
import atexit
import os
import errno
import numpy as np


class ScribbleArea(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.scribbling = False
        self.myPenWidth = 10
        self.color = QColor(20, 200, 20, 40)
        self.myPenColor = self.color
        self.image = QtGui.QImage()
        self.lastPoint = QtCore.QPoint()
        self.paint = False
        self.setGeometry(QtCore.QRect(0, 0, 550, 550))
        self.setMinimumSize(QtCore.QSize(550, 550))
        self.setMaximumSize(QtCore.QSize(550, 550))
        self.setText("")
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setObjectName("imageView")
        self.myPos = []

    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        # self.resizeImage(visibleImage, size())

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False

    def resize2(self, pixmap1):
        """
        Takes an image and returns a resized image, 
        but the aspect ratio is the same. 
        this function is used just so we can show 
        the image properly in the ImageView widget.
        Because there are images with dimantions bigger
        than the ImageView.
        The threshold used is 550, so if the image is 
        bigger (and bigger means one of its dimantions is 
        bigger than the threshold) the method will resize 
        the big dimantion to 550 and the small dimantion
        to somthing so the aspect ratio is the same.

        """
        if(pixmap1.width() < 550 and pixmap1.height() < 550):
            return pixmap1
        else:

            if(pixmap1.width() > pixmap1.height()):
                pixmap1 = pixmap1.scaledToWidth(550)
                return pixmap1

            elif(pixmap1.width() <= pixmap1.height()):
                pixmap1 = pixmap1.scaledToHeight(550)
                return pixmap1

    def openImage(self, fileName):
        loadedImage = QtGui.QImage()
        if not loadedImage.load(fileName):
            return False

        pixmap = QPixmap.fromImage(loadedImage)
        loadedImage = self.resize2(pixmap).toImage()
        self.image = loadedImage
        self.setPixmap(QPixmap.fromImage(self.image))
        self.xSh = int((550 - QPixmap.fromImage(self.image).width()) / 2)
        self.ySh = int((550 - QPixmap.fromImage(self.image).height()) / 2)
        self.shift = QtCore.QPoint(self.xSh, self.ySh)
        # self.myPosX = []
        # self.myPosY = []
        self.myPos = []
        self.update()
        return True

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.pos() - self.shift
            self.scribbling = True
            print(event.pos)

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos() - self.shift)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos() - self.shift)
            self.scribbling = False
            if(self.paint == True):
                self.saveImage("./images/jaafer", 'png')

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pixmap = QPixmap.fromImage(self.image)
        self.xSh = int((550 - QPixmap.fromImage(self.image).width()) / 2)
        self.ySh = int((550 - QPixmap.fromImage(self.image).height()) / 2)
        self.shift = QtCore.QPoint(self.xSh, self.ySh)
        painter.drawPixmap(QtCore.QPoint(self.xSh, self.ySh), pixmap)
        painter.drawPixmap(QtCore.QPoint(self.xSh, self.ySh), pixmap)

    def drawLineTo(self, endPoint):
        if(self.paint == True):
            painter = QtGui.QPainter(self.image)
            painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                                      QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
            painter.drawLine(self.lastPoint, endPoint)
            self.myPos.append(self.lastPoint)
            self.myPos.append(endPoint)

            rad = self.myPenWidth / 2 + 2
            self.update(QtCore.QRect(self.lastPoint, endPoint).normalized(
            ).adjusted(-rad, -rad, +rad, +rad))
            self.lastPoint = QtCore.QPoint(endPoint)
            self.update()

    def setPaint(self, canPaint):
        self.paint = canPaint

    def getMyPos(self):
        # return self.myPosX, self.myPosY
        return self.myPos


class TestClass(QtWidgets.QMainWindow, desginFull.Ui_MainWindow):

    def __init__(self, parent=None):
        super(TestClass, self).__init__(parent)
        self.setupUi(self)
        self.fileName = ""
        self.initial()
        self.btnResize.clicked.connect(self.deleteSeamTest)
        self.btnErase.clicked.connect(self.eraseObject)
        self.btnMark.setCheckable(True)
        self.btnMark.toggled.connect(self.on_toggled)
        self.percentRadio.toggled.connect(
            lambda: self.btnstate(self.percentRadio))
        self.pixelRadio.toggled.connect(lambda: self.btnstate(self.pixelRadio))
        self.negetiveRadio.toggled.connect(
            lambda: self.btnstate(self.negetiveRadio))
        self.positiveRadio.toggled.connect(
            lambda: self.btnstate(self.positiveRadio))
        self.actionOpen.setShortcut('Ctrl+O')
        self.actionNew.setShortcut('Ctrl+N')
        self.actionOpen.triggered.connect(self.open)
        self.actionNew.triggered.connect(self.new)
        self.isPositive = True
        self.imageView = ScribbleArea(self.widget)

    def on_toggled(self, checked):
        if checked:
            print('update the base!')
            self.imageView.setPaint(True)
        elif not checked:
            print('no base updates allowed!')
            self.imageView.setPaint(False)

    def btnstate(self, b):

        image = QImage(self.fileName)
        pixmap = QPixmap.fromImage(image)

        if b.text() == "Percent":
            if b.isChecked() == True:
                self.widthInput.setValue(100)
                self.hightInput.setValue(100)

        if b.text() == "Positive":
            if b.isChecked() == True:
                self.isPositive = True

        if b.text() == "Negetive":
            if b.isChecked() == True:
                self.isPositive = False

        if b.text() == "Pixel":

            if b.isChecked() == True:
                if(image.isNull()):
                    self.widthInput.setValue(0)
                    self.hightInput.setValue(0)
                    return

                self.widthInput.setValue(pixmap.width())
                self.hightInput.setValue(pixmap.height())
            # else:
            # 	print b.text()+" is deselected"

    def getDims(self, img):
        """
        :::::::::
        """
        imHeight, imWidth = img.shape[:2]

        width = self.widthInput.value()
        height = self.hightInput.value()

        if(self.percentRadio.isChecked() == True):
            newWidth = imWidth - int(width * imWidth / 100)
            newHeight = imHeight - int(height * imHeight / 100)
            return newWidth, newHeight

        elif(self.pixelRadio.isChecked() == True):
            return imWidth - width, imHeight - height
        # else:
        # 	return imWidth - width, imHeight - height

    def prepMask(self, img):

        self.mask = np.ones_like(img) * 255
        if (self.energyBox.currentIndex() == 0):
            img = self.sobelEnergy(img)
        elif(self.energyBox.currentIndex() == 1):
            img = self.laplaceEnergy(img)

        markedPoses = self.markedArea()
        for obj in markedPoses:
            if (self.isPositive == False):
                cv2.circle(self.mask, (obj[0], obj[1]), 5, (0, 0, 0), -1)* -1000000

    def genrateEnergy(self, img):
        """
        Takes an image and returns the energy map 
        according to the choice in the drop down widget.

        """
        self.mask = np.ones_like(img) * 255
        if (self.energyBox.currentIndex() == 0):
            img = self.sobelEnergy(img)
        elif(self.energyBox.currentIndex() == 1):
            img = self.laplaceEnergy(img)

        markedPoses = self.markedArea()
        # maxEnergy = np.amax(img)
        for obj in markedPoses:
            if (self.isPositive == True):
                cv2.circle(img, (obj[0], obj[1]), 5, (255, 255, 255), -1)
                # cv2.circle(mask,(obj[0],obj[1]), 5, (255,255,255), -1)
            else:
                cv2.circle(img, (obj[0], obj[1]), 5, (0, 0, 0), -1)
                # cv2.circle(self.mask,(obj[0],obj[1]), 5, (0,0,0), -1)

            # img[obj[0], obj[1]] = 255
        return img

    def sobelEnergy(self, img):
        """
        Takes an image and returns the edge 
        magnitude using the Sobel transform.

        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        abs_sobel_x = cv2.convertScaleAbs(sobel_x)
        abs_sobel_y = cv2.convertScaleAbs(sobel_y)
        result = cv2.addWeighted(abs_sobel_x, 0.5, abs_sobel_y, 0.5, 0)
        return result

    def laplaceEnergy(self, img):
        """
        Takes an image and returns the edges
         of an image using the Laplace operator.

        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F)

    def new(self):
        """
        Creates a new file so you can open a new image.

        """
        self.initial()
        self.btnstate(self.percentRadio)
        self.btnstate(self.pixelRadio)

    def open(self):
        """
        Opens a file exeplorer so you can choose
        an image to open.

        """
        self.fileName, _ = QFileDialog.getOpenFileName(
            self, "Open File", QDir.currentPath() + "/images", "Images (*.png *.xpm *.jpg *jpeg)")
        if self.fileName:
            image = QImage(self.fileName)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer",
                                        "Cannot load %s." % self.fileName)
                return
            self.initial()

            pixmap = QPixmap.fromImage(image)
            self.sizeLabel.setText('{} x {}'.format(
                pixmap.width(), pixmap.height()))
            pixmap = self.resize1(pixmap)

            # self.imageView.setPixmap(pixmap)
            self.imageView.openImage(self.fileName)
            self.imageView.setAlignment(QtCore.Qt.AlignCenter)
            self.btnstate(self.percentRadio)
            self.btnstate(self.pixelRadio)

    def initial(self):
        """
        Initilazes all the windows and tabs so 
        the program is the same as if it's first opened.

        """

        self.imageView.setText(" ")
        self.imageView_2.setText(" ")
        self.imageView_3.setText(" ")
        self.imageView_4.setText(" ")
        self.sizeLabel.setText(" ")

    def resize1(self, pixmap1):
        """
        Takes an image and returns a resized image, 
        but the aspect ratio is the same. 
        this function is used just so we can show 
        the image properly in the ImageView widget.
        Because there are images with dimantions bigger
        than the ImageView.
        The threshold used is 550, so if the image is 
        bigger (and bigger means one of its dimantions is 
        bigger than the threshold) the method will resize 
        the big dimantion to 550 and the small dimantion
        to somthing so the aspect ratio is the same.

        """
        if(pixmap1.width() < 550 and pixmap1.height() < 550):
            return pixmap1
        else:

            if(pixmap1.width() > pixmap1.height()):
                pixmap1 = pixmap1.scaledToWidth(550)
                return pixmap1

            elif(pixmap1.width() <= pixmap1.height()):
                pixmap1 = pixmap1.scaledToHeight(550)
                return pixmap1

    def eraseObject(self):

        if (self.fileName and self.isPositive == False):

            img = cv2.imread(self.fileName)
            energyMap = self.genrateEnergy(img)
            energyMap1 = np.ones_like(img)*1000
            
            self.prepMask(img)

            markedPoses = self.markedArea()
            xRange = []
            for obj in markedPoses:
                xRange.append(obj[0])

            dx = max(xRange) - min(xRange) + 20

            print(dx)

            seamDraw = img
            seams = []
            seams2 = []

            imgRemove1 = img
            imgAdd1 = img
            phase1Img = img

            for i in range(abs(dx)):
                energies = self.cumulativeVerticalRemoval(
                ) + self.cumulativeVertical(self.genrateEnergy(imgRemove1))
                # energies1 = self.cumulativeVertical(self.genrateEnergy(img))
                seam = self.findVerticalSeam(energies)
                seams.append((seam, 1))
                imgRemove1 = self.removeVertical(imgRemove1, seam)
                self.mask = self.removeVertical(self.mask, seam)

            imgRemove2 = imgRemove1
            phase2Img = imgRemove1
            imgAdd2 = imgRemove1


            for obj, RorI in seams:

                self.drawSeam(seamDraw, obj, RorI)

            self.showImages(phase2Img, energyMap, seamDraw)

    def deleteSeamTest(self):
        """
        This method does all the steps in order,
        reads the original image and calculates the 
        energy map, and for vertical and horizontal
        direction and calls the cumulative map calculator
        function and the seam finding function, the seam
        removing fuction, and lastly draws the seams on 
        the image, and calls the showImages to show them.


        """

        if self.fileName:
            img = cv2.imread(self.fileName)
            energyMap = self.genrateEnergy(img)

            imHeight, imWidth = img.shape[:2]
            dx, dy = self.getDims(img)
            print(dy)
            print(dx)

            seamDraw = img
            seams = []
            indexes = []

            imgRemove1 = img
            imgAdd1 = img
            phase1Img = img

            # index = None
            # energies = self.cumulativeHorizontal(self.genrateEnergy(imgRemove1))
            # energies = self.cumulativeHorizontal(self.genrateEnergy(imgRemove1))
            # m = np.ma.masked_array(energies[:,imWidth-1])
            for i in range(abs(dy)):
                energies = self.cumulativeHorizontal(
                    self.genrateEnergy(imgRemove1))
                seam = self.findHorizontalSeam(energies)
                seams.append((seam, dy))
                # m.mask[index] = True
                # indexes.append(index)


                imgRemove1 = self.removeHorizontal(imgRemove1, seam)
                phase1Img = imgRemove1
                if(dy < 0):
                    imgAdd1 = self.insertHorizontal(imgAdd1, seam)
                    phase1Img = imgAdd1


            imgRemove2 = phase1Img
            imgAdd2 = phase1Img
            phase2Img = phase1Img

            for i in range(abs(dx)):
                energies = self.cumulativeVertical(
                    self.genrateEnergy(imgRemove2))
                seam = self.findVerticalSeam(energies)
                seams.append((seam, dx))
                imgRemove2 = self.removeVertical(imgRemove2, seam)
                phase2Img = imgRemove2
                if (dx < 0):
                    imgAdd2 = self.insertVertical(imgAdd2, seam)
                    imgRemove2 = imgAdd2
            print(phase2Img.shape)
            for obj, RorI in seams:
            	# print (obj)
            	self.drawSeam(seamDraw, obj, RorI)


            self.showImages(phase2Img, energyMap, seamDraw)


    def showImages(self, result, energy, seams):
        """
        Takes 3 images ( the result resized image, 
        the energy map, the image with the seams 
        drawn on it) and show these image in the
        ImageView corrsponding to each image.


        """
        cv2.imwrite('./images/output_image.png', result)
        self.fileName3 = "./images/output_image.png"
        result = QImage(self.fileName3)
        pixmap = QPixmap.fromImage(result)
        pixmap = self.resize1(pixmap)
        self.imageView_3.setPixmap(pixmap)

        cv2.imwrite('./images/energy_image.png', energy)
        self.fileName2 = "./images/energy_image.png"
        energy = QImage(self.fileName2)
        pixmap = QPixmap.fromImage(energy)
        pixmap = self.resize1(pixmap)
        self.imageView_2.setPixmap(pixmap)

        cv2.imwrite('./images/seams_image.png', seams)
        self.fileName4 = "./images/seams_image.png"
        seams = QImage(self.fileName4)
        pixmap = QPixmap.fromImage(seams)
        pixmap = self.resize1(pixmap)
        self.imageView_4.setPixmap(pixmap)

    def cumulativeVertical(self, energy):
        """
        Takes the energy map and calculates the 
        cumulative wieghts in the vertical direction.

        """
        height, width = energy.shape[:2]
        energies = np.zeros((height, width))

        for i in range(1, height):
            for j in range(width):
                left = energies[i - 1, j - 1] if j - 1 >= 0 else 1e6
                middle = energies[i - 1, j]
                right = energies[i - 1, j + 1] if j + 1 < width else 1e6

                energies[i, j] = energy[i, j] + min(left, middle, right)

        return energies

    def cumulativeVerticalRemoval(self):
        """
        Takes the energy map and calculates the 
        cumulative wieghts in the vertical direction.

        """
        height, width = self.mask.shape[:2]
        gray = cv2.cvtColor(self.mask, cv2.COLOR_BGR2GRAY)
        energies = np.zeros((height, width))

        for i in range(1, height):
            for j in range(width):
                left = energies[i - 1, j - 1] if j - 1 >= 0 else 1e6
                middle = energies[i - 1, j]
                right = energies[i - 1, j + 1] if j + 1 < width else 1e6

                energies[i, j] = gray[i, j] + min(left, middle, right)

        return energies

    def cumulativeHorizontal(self, energy):
        """
        Takes the energy map and calculates the 
        cumulative wieghts in the horizontal direction.

        """
        height, width = energy.shape
        energies = np.zeros((height, width))

        for j in range(1, width):
            for i in range(height):
                top = energies[i - 1, j - 1] if i - 1 >= 0 else 1e6
                middle = energies[i, j - 1]
                bottom = energies[i + 1, j - 1] if i + 1 < height else 1e6

                energies[i, j] = energy[i, j] + min(top, middle, bottom)

        return energies

    def findHorizontalSeam(self, energies):
        """
        Takes the cumulative map and calculates the 
        horizontal path according to the wieghts.

        """

        height, width = energies.shape[:2]
        previous = 0
        seam = []
        # index = np.argmin(m)


        for i in range(width - 1, -1, -1):

        	col = energies[:, i]
        	# m = np.ma.masked_array(col)

        	if i == width - 1:
        		previous = np.argmin(col)
        	else:
        		top = col[previous - 1] if previous - 1 >= 0 else 1e6
        		middle = col[previous]
        		bottom = col[previous + 1] if previous + 1 < height else 1e6
        		previous = previous + np.argmin([top, middle, bottom]) - 1
        	seam.append([i, previous])
        return seam


    def findVerticalSeam(self, energies):
        """
        Takes the cumulative map and calculates the 
        vertical path according to the wieghts.

        """
        height, width = energies.shape[:2]
        previous = 0
        seam = []

        for i in range(height - 1, -1, -1):
            row = energies[i, :]

            if i == height - 1:
                previous = np.argmin(row)
                seam.append([previous, i])
            else:
                left = row[previous - 1] if previous - 1 >= 0 else 1e6
                middle = row[previous]
                right = row[previous + 1] if previous + 1 < width else 1e6

                previous = previous + np.argmin([left, middle, right]) - 1
            seam.append([previous, i])

        return seam

    def drawSeam(self, img, seam, RorI):
        """
        Takes and image and a seam and draws the seam
        on the image. Here the seam can be vertical or
        horizontal.

        """
        if(RorI < 0):
            cv2.polylines(img, np.int32(
                [np.asarray(seam)]), False, (0, 255, 0))
        else:
            cv2.polylines(img, np.int32(
                [np.asarray(seam)]), False, (0, 0, 255))

    def removeHorizontal(self, img, seam):
        """
        Takes an image and a horizontal seam 
        and returns a new image with that seam
        removed.

        """
        # print(len(img.shape))
        if(len(img.shape) == 3):
            height, width, bands = img.shape
            removed = np.zeros((height - 1, width, bands), np.uint8)
        else:
            height, width = img.shape
            removed = np.zeros((height - 1, width))

        for x, y in (seam):
            removed[0:y, x] = img[0:y, x]
            removed[y:height - 1, x] = img[y + 1:height, x]

        return removed

    def insertHorizontal(self, img, seam):
        """
        Takes an image and a horizontal seam 
        and returns a new image with that seam
        removed.

        """

        height, width, bands = img.shape
        inserted = np.zeros((height + 1, width, bands), np.uint8)

        for x, y in (seam):
            inserted[0:y, x] = img[0:y, x]
            inserted[y, x] = img[y, x]
            inserted[y + 1:height + 1, x] = img[y:height, x]

        return inserted

    def removeVertical(self, img, seam):
        """
        Takes an image and a vertical seam 
        and returns a new image with that seam
        removed.

        """
        if(len(img.shape) == 3):
            height, width, bands = img.shape
            removed = np.zeros((height, width - 1, bands), np.uint8)
        else:
            height, width = img.shape
            removed = np.zeros((height, width - 1))

        # height, width, bands = img.shape
        # removed = np.zeros((height, width - 1, bands), np.uint8)

        for x, y in reversed(seam):
            removed[y, 0:x] = img[y, 0:x]
            removed[y, x:width - 1] = img[y, x + 1:width]

        return removed

    def insertVertical(self, img, seam):
        """
        Takes an image and a vertical seam 
        and returns a new image with that seam
        removed.

        """
        height, width, bands = img.shape
        inserted = np.zeros((height, width + 1, bands), np.uint8)

        for x, y in (seam):
            inserted[y, 0:x] = img[y, 0:x]
            inserted[y, x] = img[y, x]
            inserted[y, x + 1: width + 1] = img[y, x:width]

        return inserted

    def markedArea(self):
        markedPos = []
        for obj in self.imageView.getMyPos():
            markedPos.append([obj.x(), obj.y()])
        return markedPos


def exit_handler():
    """
    This method is triggerd when the program exist
    and remove the saved images in the process of
    the resizing.

    """
    print('My application is ending!')
    silentremove("./images/energy_image.png")
    silentremove("./images/output_image.png")
    silentremove("./images/seams_image.png")
    silentremove("./images/jaafer")


def silentremove(filename):
    """
    Takes a file diroctory and removes the file
    from the device.

    """
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


atexit.register(exit_handler)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = TestClass()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
