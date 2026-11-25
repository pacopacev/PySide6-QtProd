import sys
from global_model import GlobalModel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QLabel, QLineEdit
)


class RegisterPage(QWidget):
    def __init__(self, stacked_widget=None):
        super().__init__()
        
        print("in register user")
        
        # self.stacked_widget = stacked_widget
        
        # self.register_window_layout = QVBoxLayout(stacked_widget)
        # add_user_title_label = QLabel("Add User", self)
        # add_user_title_label.setAlignment(Qt.AlignCenter)
        # add_user_title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #000000; border: none;")
        # self.register_window_layout.addWidget(add_user_title_label)