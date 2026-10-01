import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import PySide6.QtWidgets as q
from PySide6.QtWidgets import QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut


# Импортиране на външните модули
from dash_page import DashPage
from scan_page import ScanPage
from add_product_page import AddProductPage
from global_model import GlobalModel  
from utils.version import Version



class LoginPage(q.QWidget):
    """Цялата логин форма се отделя в собствен чист уиджет, за да не чупи основния прозорец."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Пазим връзка към MainWindow за базата данни
        
        
        layout = q.QVBoxLayout(self)
        layout.setContentsMargins(10, 200, 10, 10)
        layout.setSpacing(30)
        
        title_label = q.QLabel("LOGIN", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; border: none;")
        layout.addWidget(title_label)
        
        # Синият контейнер
        self.container = q.QFrame()
        self.container.setStyleSheet("""
            QFrame {
                border: 2px solid #4A90E2;
                border-radius: 8px;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.container, alignment=Qt.AlignCenter)
        
        form_layout = q.QVBoxLayout(self.container)
        form_layout.setSpacing(20) 
        form_layout.setContentsMargins(50, 50, 50, 50)
         
        username_layout = q.QHBoxLayout()
        password_layout = q.QHBoxLayout() 
        button_layout = q.QHBoxLayout()
        button_layout.setContentsMargins(10, 15, 0, 0)
        
        self.username = q.QLabel("Username:", self)
        self.username.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #333;")
        self.username.setFixedWidth(80)
        
        self.password = q.QLabel("Password:", self)
        self.password.setStyleSheet("border: none; font-size: 14px; font-weight: bold; color: #333;")
        self.password.setFixedWidth(80)
        
        self.username_edit = q.QLineEdit(self)
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setStyleSheet("font-size: 14px; padding: 5px;")
        self.username_edit.setFixedWidth(200)  
        
        self.password_edit = q.QLineEdit(self)
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(q.QLineEdit.Password)
        self.password_edit.setStyleSheet("font-size: 14px; padding: 5px;")
        self.password_edit.setFixedWidth(200)
        
        username_layout.addWidget(self.username)
        username_layout.addWidget(self.username_edit)
        username_layout.addStretch()
        
        password_layout.addWidget(self.password)
        password_layout.addWidget(self.password_edit)
        password_layout.addStretch()
        
        self.login_button = q.QPushButton("Login", self)
        self.login_button.setStyleSheet("""
            QPushButton {
                font-size: 16px; font-weight: bold; background-color: #4A90E2; color: white; border-radius: 5px; padding: 10px; border: none;
            }
            QPushButton:hover { background-color: #357ABD; }
        """)                                    
        self.login_button.setFixedWidth(100)
        self.login_button.setCursor(Qt.PointingHandCursor)  
        self.login_button.clicked.connect(lambda: self.main_window.login(self.username_edit.text(), self.password_edit.text()))
        
        button_layout.addStretch()
        button_layout.addWidget(self.login_button)
        button_layout.addStretch()
        
        form_layout.addLayout(username_layout)
        form_layout.addLayout(password_layout)
        form_layout.addLayout(button_layout)
        
        layout.addStretch()
        
        # Версия на дъното
        version_layout = q.QHBoxLayout()
        layout.addLayout(version_layout)
        
        
        version = Version(1, 1, 0)  # Примерна версия
        version_label = version.version_label
        version_layout.addStretch()
        version_layout.addWidget(version_label)
        
        


class MainWindow(q.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.model = GlobalModel()
        
        self.user_id = None  
        self.setWindowTitle("Flowbit")
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
        self.setWindowIcon(QIcon("../assets/favicon.ico"))
        
        # --- СЪЗДАВАНЕ НА ГОЛЯМОТО МЕНЮ ТУК ---
        self.file_menu = self.menuBar().addMenu("Menu")
        
        
        go_to_login_action = self.file_menu.addAction("Go to Login Page")
        go_to_login_action.triggered.connect(self.go_back_to_login)
        
        exit_action = self.file_menu.addAction("Exit")
        exit_action.triggered.connect(q.QApplication.quit)
        
        
        
        self.scan_menu = self.menuBar().addAction("Scan product")
        self.scan_menu.triggered.connect(self.show_scan_page)
        
        
        self.product_menu = self.menuBar().addMenu("Product")
        
        self.product_action = self.product_menu.addAction("Add product")
        self.product_action.triggered.connect(self.show_add_product_page)
        
        list_products_action = self.product_menu.addAction("List products")
        

        
        # Скриваме го първоначално за логин екрана
        self.menuBar().setVisible(False)
        
        # Основен контейнер (Стек), който запълва целия прозорец
        self.pages_container = QStackedWidget()
        self.setCentralWidget(self.pages_container)
        
        # Създаваме страниците вътре в стека
        self.login_page = LoginPage(self)   # Индекс 0
        self.dash_page = DashPage(self)     # Индекс 1
        self.scan_page = ScanPage(self)     # Индекс 2
        self.product_page = AddProductPage(self)  # Индекс 3
        
        self.pages_container.addWidget(self.login_page)
        self.pages_container.addWidget(self.dash_page)
        self.pages_container.addWidget(self.scan_page)
        self.pages_container.addWidget(self.product_page)
        
        # По подразбиране отваряме логин формата
        self.pages_container.setCurrentIndex(0)
        
        # Бърз изход с Escape
        self.shortcut_escape = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut_escape.activated.connect(q.QApplication.quit)
        
        

    def login(self, username, password):
        if self.model.conn is None:
            q.QMessageBox.warning(self, "Connection Error", "Failed to connect to the database.")
            return
            
        if username and password:
            with self.model.conn.cursor() as cur: 
                cur.execute("SELECT * FROM users WHERE first_name = %s AND password = %s", (username, password))
                data = cur.fetchone()
                
                if data:
                    # print(f"Login successful! User ID: {data[0]}")
                    self.model.set_user_id(data[0])
                    # print(f"User ID {self.model.user_id} е записан в GlobalModel")
                    # Показваме фиксираното меню горе
                    self.menuBar().setVisible(True)
                    # Превключваме на DashPage (Индекс 1)
                    self.pages_container.setCurrentIndex(1)
                else:
                    self.show_login_warning()
        else:
            self.show_login_warning()

    def show_login_warning(self):
        q.QMessageBox.warning(self, "Login Failed", "Invalid credentials.")
        self.login_page.username_edit.clear()
        self.login_page.password_edit.clear()

    def show_scan_page(self):
        # Превключваме на ScanPage (Индекс 2)
        if self.pages_container.currentIndex() != 0: # Само ако сме логнати
            self.scan_page.scan.get_user_info()
            self.scan_page.scan.getLastScannedJobOrderID()
            self.pages_container.setCurrentIndex(2)
            if self.scan_page.scan.entry:
                self.scan_page.scan.entry.setFocus()
    
    def show_add_product_page(self):
        # Превключваме на AddProductPage (Индекс 3)
        if self.pages_container.currentIndex() != 0: # Само ако сме логнати
            self.pages_container.setCurrentIndex(3)

    def go_back_to_login(self):
        # Рестартираме изгледа изцяло
        self.menuBar().setVisible(False)
        self.login_page.username_edit.clear()
        self.login_page.password_edit.clear()
        self.pages_container.setCurrentIndex(0) # Връща на логин страницата
    
    
    def closeEvent(self, event):
        reply = q.QMessageBox.question(
            self, 'Изход', 'Сигурни ли сте, че искате да излезете?',
            q.QMessageBox.Yes | q.QMessageBox.No, q.QMessageBox.No
        )
        if reply == q.QMessageBox.Yes:
            event.accept() 
        else:
            event.ignore() 
    

app = q.QApplication([])
window = MainWindow() 
window.showMaximized()

app.exec()