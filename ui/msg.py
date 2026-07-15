from PySide6 import QtWidgets
from PySide6.QtGui import QIcon
import os


os.path.join(os.path.dirname(__file__), "..", "..", "assets", "favicon.ico")
# adjust the number of ".." based on where msg.py sits relative to assets/

class WarningMessageBox(QtWidgets.QMessageBox):
    def __init__(self, title, message, icon=QtWidgets.QMessageBox.Warning, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(icon)  # message icon: Warning / Critical / Information / Question
        self.setWindowIcon(QIcon("../assets/favicon.ico"))  # titlebar icon (optional)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)