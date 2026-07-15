

import PySide6.QtWidgets as q
from PySide6.QtCore import Qt  
from PySide6.QtGui import QIcon
from scan_page import ScanPage
from add_product_page import AddProductPage
from PySide6.QtWidgets import QStackedWidget




class DashPage(q.QMainWindow):
    def __init__(self, stacked_widget=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Test Page")
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")

        self.scan_page = ScanPage()
        self.addProduct_page = AddProductPage()
        
        # Централен уиджет
        central_widget = q.QWidget()
        self.setCentralWidget(central_widget)
        
        # 1. ПОПРАВКА: Основен layout за самия прозорец, който ще държи контейнера
        main_window_layout = q.QVBoxLayout(central_widget)
        main_window_layout.setAlignment(Qt.AlignCenter) # Центрира синята кутия в екрана
        main_window_layout.setContentsMargins(0, 0, 0, 0) # Премахваме външните отстояния на главния layout
        main_window_layout.addStretch()
        
        
        bottom_button_layout = q.QHBoxLayout()
        main_window_layout.addLayout(bottom_button_layout)
        bottom_button_layout.setContentsMargins(10, 10, 10, 10)
        
        label_exit = q.QLabel("Press ESC for Exit", self)
   
        bottom_button_layout.addWidget(label_exit)
        bottom_button_layout.addStretch()
        
        
       
        
    def go_back(self):
        # Връщаме се към първата страница (Login Page), която е на индекс 0 в стеката
        stacked_widget = self.parent()
        if stacked_widget:
            stacked_widget.setCurrentIndex(0)
           
            
    def show_scan_page(self):
        print("Show scan page")
        if self.stacked_widget:
            print("Show scan page1")
            self.stacked_widget.setCurrentIndex(2)
    def add_product(self):
        print("Show add product page")
        if self.stacked_widget:
            print("Show add product page1")
            self.stacked_widget.setCurrentIndex(3)
    

        
        
      
        
        
        
