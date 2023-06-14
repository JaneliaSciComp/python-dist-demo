from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMenuBar, QMenu, QSlider, QWidget
from PySide6.QtGui import QAction, QColor, QImage, QPixmap
from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot

# PyQt6 uses slightly different syntax, which could be avoided as follows:
# from PyQt6.QtCore import pyqtSignal as Signal, pyqtSlot as Slot

import numpy as np
import platform
import sys

IMAGE_WIDTH = 700
IMAGE_HEIGHT = 700

class Worker(QRunnable):
    # Only a subclass of QObject can have signals.  QRunnable is not such a subclass,
    # so it uses an instance of this class to send its signal.
    class Signaler(QObject):
        finished = Signal(QPixmap)
                      
    def __init__(self, image_array, threshold):
        super().__init__()
        self.image_array = image_array
        self.threshold = threshold
        self.signaler = Worker.Signaler()

    def run(self):
        # These NumPy operations are efficient.
        a1 = self.image_array > self.threshold
        a2 = a1.astype(np.uint8)
        a3 = a2 * 255
        new_image = QImage(a3.data, a3.shape[0], a3.shape[1], QImage.Format_Grayscale8)
        new_pixmap = QPixmap.fromImage(new_image)
        self.signaler.finished.emit(new_pixmap)
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo 2")

        self.setup_window()
        self.setup_menus()
        self.setup_threshold()
        self.setup_image()

    def setup_window(self):
        main = QWidget(self)
        self.layout = QHBoxLayout()
        main.setLayout(self.layout)
        self.setCentralWidget(main)

    def setup_menus(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        self.open_action = QAction("&Open...", self)
        self.open_action.triggered.connect(self.file_open)
        file_menu.addAction(self.open_action)

        if platform.system() != "Darwin":
            self.quit_action = QAction("&Quit", self)
            self.quit_action.triggered.connect(self.close)
            file_menu.addAction(self.quit_action)

    @Slot()
    def file_open(self):
        file_path, _ = QFileDialog.getOpenFileName(self, filter="Image Files (*.png *.jpg *.bmp)")
        if file_path != "":
            image = QImage()
            if image.load(file_path):
                self.set_image(image)

    def setup_image(self):
        self.image_label = QLabel()
        self.set_image(None)
        self.layout.addWidget(self.image_label)

    def set_image(self, image):
        if image == None:
            image_scaled = QImage(IMAGE_WIDTH, IMAGE_HEIGHT, QImage.Format_RGB888)
            image_scaled.fill(QColor("darkCyan"))
        else:
            image_scaled = image.scaled(IMAGE_WIDTH, IMAGE_HEIGHT)
        # 1 byte per pixel
        image_scaled = image_scaled.convertToFormat(QImage.Format_Grayscale8)
        bits = image_scaled.constBits()
        self.image_array = np.array(bits).reshape(IMAGE_WIDTH, IMAGE_HEIGHT, 1)
        self.apply_threshold(self.threshold_slider.value())

    def show_pixmap(self, pixmap):
        self.image_label.setPixmap(pixmap)

    def setup_threshold(self):
        self.threshold_slider = QSlider(Qt.Vertical)
        self.threshold_slider.setValue(50)
        self.threshold_slider.valueChanged.connect(self.threshold_changed)
        self.layout.addWidget(self.threshold_slider)
        self.threshold_being_applied = None
        self.threshold_to_apply = None

    @Slot(int)
    def threshold_changed(self, value):
        threshold = int(value / 100 * 255)
        self.apply_threshold(threshold)

    def apply_threshold(self, threshold):
        if not self.threshold_being_applied:
            self.threshold_being_applied = threshold
            # To keep the main UI thread fully responsive, do the work on another thread.
            pool = QThreadPool.globalInstance()
            worker = Worker(self.image_array, threshold)
            # This signal will trigger this slot back on the main UI thread when the work is done.
            worker.signaler.finished.connect(self.worker_finished)
            pool.start(worker)
        elif abs(threshold - self.threshold_being_applied) > 5:
            # If the slider moves while the working is processing, save the slider value to be applied
            # when the worker is done.  This approach seems to work better if it used only when the
            # slider has moved more than a little bit.
            self.threshold_to_apply = threshold

    @Slot(QPixmap)
    def worker_finished(self, new_pixmap):
        self.show_pixmap(new_pixmap)
        self.threshold_being_applied = None
        if self.threshold_to_apply:
            # Apply the last value that the slider produced while waiting for the worker.
            threshold = self.threshold_to_apply
            self.threshold_to_apply = None
            self.apply_threshold(threshold)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()