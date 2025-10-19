# Python imports
import sys

# Package imports
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Converter Tool")
        self.setFixedSize(QSize(400, 300))

        self.label = QLabel("Hello")
        # It is advised to get current font, update it, then
        # apply it back, to ensure font faced remains in keeping
        # with desktop conventions.
        font = self.label.font()
        font.setPointSize(30)
        self.label.setFont(font)
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        self.setCentralWidget(self.label)


# Only require one QApplication per application.
app = QApplication(sys.argv)

# In Qt, all top level widgets are windows (no parent,
# and not nested in another widget or layout).
window = MainWindow()
# By default, all widgets without parents (e.g. windows # are hidden until shown.
window.show()

# Start event loop
# Program will not advance past this point until event
# loop has stopped
app.exec()
