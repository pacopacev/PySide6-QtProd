import PySide6.QtWidgets as q
from PySide6.QtCore import Qt  
from PySide6.QtGui import QIcon
from scan import Scan
from global_model import GlobalModel

class ScanPage(q.QMainWindow):
    def __init__(self, stacked_widget=None):
        super().__init__()
        
        
     
        self.stacked_widget = stacked_widget
     
        self.db_id = None
        
        # self.setWindowTitle("Test Page")
        print("ScanPage initialized")
        
        # Централен уиджет
        central_widget = q.QWidget()
        central_widget.setStyleSheet("background-color: #0047AB;")
        self.setCentralWidget(central_widget)
        
        # Основен layout за самия прозорец
        main_window_layout = q.QVBoxLayout(central_widget)
        main_window_layout.setAlignment(Qt.AlignCenter) 
        main_window_layout.setContentsMargins(0, 0, 0, 0) 
        
        button_layout = q.QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        
        right_layout = q.QVBoxLayout()
        right_layout.setSpacing(8)
        right_layout.setContentsMargins(10, 10, 10, 0)
        
        
        left_layout = q.QVBoxLayout()
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setAlignment(Qt.AlignCenter)
        
        combo_layout = q.QHBoxLayout()
        combo_layout.setSpacing(8)
        combo_layout.setContentsMargins(10, 10, 10, 10)
        combo_layout.addLayout(left_layout)
        combo_layout.addLayout(right_layout)
        
        main_window_layout.addLayout(combo_layout)
        main_window_layout.addLayout(button_layout)
        
        
        
        
        
        self.label_last_scanned = q.QLabel("Последно сканирани работни поръчки:", self)
        self.label_last_scanned.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        right_layout.addWidget(self.label_last_scanned)
        
        self.data_list = q.QListWidget(self)
        # self.data_list.setFixedHeight(500)
        self.data_list.setFixedWidth(398)
        self.data_list.setSpacing(1)
        self.data_list.setStyleSheet("""
    QListWidget {
        background-color: white;
        border: 2px solid #0047AB;
        border-radius: 5px;
    }
    QListWidget::item {
        padding-top: 2px;     /* Намали или увеличи тези пиксели */
        padding-bottom: 2px;  /* за да контролираш разстоянието */
        margin: 0px;          /* Премахва външното разстояние */
    }
    QListWidget::item:selected {
        background-color: #0047AB;
        color: white;
    }
""")
        self.data_list.itemClicked.connect(self.on_item_clicked)
        
        
            
            
        right_layout.addWidget(self.data_list)
        

# 2. Добавяме елементи вътре

        # items_count = 100
        # for i in range(items_count):
        #     item = q.QListWidgetItem(f"Item {i}")
        #     self.data_list.addItem(item)

        
        self.work_station_label = q.QLabel("", self)
        self.work_station_label.setStyleSheet("font: Arial; font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px; margin-bottom: 10px;")
        self.work_station_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.work_station_label)
        
        self.operator_label = q.QLabel("Оператор: ", self)
        self.operator_label.setStyleSheet("font: Arial; font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px; margin-top: 10px;")
        self.operator_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.operator_label)
        
        
        
        self.label = q.QLabel("BARCODE: ИЗЧАКВА СКАНИРАНЕ...", self)
        self.label.setStyleSheet("font: Arial; font-size: 44px; font-weight: bold; color: white;")
        left_layout.addWidget(self.label)
        
        
        self.time_label = q.QLabel("00:00:00", self)
        self.time_label.setStyleSheet("font: Arial; font-size: 44px; font-weight: bold; color: white; margin-top: 34px;")
        self.time_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.time_label)
        
        
        
        help_label = q.QLabel("Натисни ESC за изход | Press ESC to exit", self)
        help_label.setStyleSheet("font: Arial; font-size: 13px; font-weight: normal; color: white; margin-top: 34px;")
        help_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(help_label)
        
        
        
         
        
        back_button = q.QPushButton("LOG\nOUT", self)
        delete_scan_button = q.QPushButton("DELETE\n SCAN", self)
        clear_scan_button = q.QPushButton("CLEAR\n SCAN", self)
        clear_scan_button.setEnabled(False)
        
        button_layout.addStretch()
        # ПОПРАВКА: Изтрита е излишната скоба отдолу
        # button_layout.addWidget(delete_scan_button)
        # ПОПРАВКА: Изтрита е излишната скоба отдолу
        back_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 21px;
                font-weight: bold;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;  
            }
        """)
        
        delete_scan_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 21px;
                font-weight: bold;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;  
            }
        """)
        
        clear_scan_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                font-size: 21px;
                font-weight: bold;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;  
            }
        """)
        back_button.setFixedWidth(130)
        back_button.setFixedHeight(130)
        
        
        delete_scan_button.setFixedWidth(130)
        delete_scan_button.setFixedHeight(130)
        delete_scan_button.clicked.connect(self.delete_scan)
        
        clear_scan_button.setFixedWidth(130)
        clear_scan_button.setFixedHeight(130)
        
        button_layout.addWidget(clear_scan_button)
        button_layout.addWidget(delete_scan_button)
        button_layout.addWidget(back_button)
        
        # button_layout.addStretch()
        back_button.clicked.connect(self.go_back)
        
        entry = q.QLineEdit(self)
        entry.setFixedSize(1, 1)
        entry.setStyleSheet("border: none; background: transparent; color: transparent;")
        entry.move(-100, -100)
        entry.setFocusPolicy(Qt.StrongFocus)
        entry.show()

        self.scan = Scan(self, self.time_label, self.work_station_label, self.operator_label, self.data_list, self.label, entry=entry, clear_scan_button=clear_scan_button, central_widget=central_widget)
        self.scan.entry.setFocus()
        self.scan.entry.grabKeyboard()

        self.scan.refresh_data_list()

    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'scan') and self.scan.entry:
            self.scan.entry.setFocus()
            self.scan.entry.grabKeyboard()

    def hideEvent(self, event):
        super().hideEvent(event)
        if hasattr(self, 'scan') and self.scan.entry:
            self.scan.entry.releaseKeyboard()

    def go_back(self):
        print("Going back to login from scan page")
        # Тъй като self.stacked_widget всъщност е MainWindow, 
        # викаме директно неговия готов метод за рестартиране и скриване на менюто
        if self.stacked_widget:
            self.stacked_widget.go_back_to_login()
            
    def delete_scan(self):
        if self.db_id == None:
            q.QMessageBox.warning(self, "Предупреждение!", "Няма избрано съдържание за изтриване.")
            return
        # self.triggered = True
        print(type(self.db_id))
        g_model = GlobalModel()
        if g_model.conn is None:
            return
        
        if self.db_id != None:
            confirm = q.QMessageBox.question(
                        self, 'Изтриване', 'Сигурни ли сте, че искате да изтриете сканираното съдържание?',
                        q.QMessageBox.Yes | q.QMessageBox.No, q.QMessageBox.No)
                        
            if confirm == q.QMessageBox.Yes:
                try:
                    with g_model.conn.cursor() as cursor:
                        query = """
                    DELETE FROM station_scans
                    WHERE id = %s """
                # ПОПРАВКА: Подаваме динамично текущата станция вместо твърдото число 4
                        cursor.execute(query, (self.db_id,))
                        cursor.connection.commit()
                        if cursor.rowcount > 0:
                    
                            print(f"Сканираното съдържание с ID {self.db_id} е изтрито.")
                            self.data_list.clear()
                            self.scan.getLastScannedJobOrderID()
                            
                        else:
                            print(f"Сканираното съдържание с ID {self.db_id} не е намерено.")
                except Exception as e:
                    print(f"Грешка при изтриване на сканираното съдържание: {e}")
                else:
                    return

        
        
        
        
        
        

            
    def on_item_clicked(self, item):
    # PySide automatically passes the clicked QListWidgetItem into this function
    # Now you can grab the custom ID you saved earlier!
        db_id = item.data(Qt.ItemDataRole.UserRole) # Use Qt.UserRole if on PySide2
        if db_id:
            self.db_id = db_id

       
       