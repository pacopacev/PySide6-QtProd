import PySide6.QtWidgets as q
from PySide6.QtCore import Qt, QTimer, QEvent  
from PySide6.QtGui import QIcon
from scan import Scan
from PySide6 import QtGui
from global_model import GlobalModel
import time
from print import PrintLabel

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
        main_window_layout.setContentsMargins(8, 8, 8, 8)
        
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
        
        qty_layout = q.QHBoxLayout()
        qty_layout.setSpacing(8)
        qty_layout.setContentsMargins(4, 4, 4, 4)
        qty_layout.setAlignment(Qt.AlignCenter)
        
        
        
        combo_layout = q.QHBoxLayout()
        combo_layout.setSpacing(8)
        combo_layout.setContentsMargins(10, 10, 10, 10)
        combo_layout.addLayout(left_layout, 3)
        combo_layout.addLayout(right_layout, 2)
        
        main_window_layout.addLayout(combo_layout)
        main_window_layout.addLayout(button_layout)
        
        
        
        
        
        
        
        
        self.label_last_scanned = q.QLabel("Последно сканирани работни поръчки:", self)
        self.label_last_scanned.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        right_layout.addWidget(self.label_last_scanned)
        
        self.data_list = q.QListWidget(self)
        # self.data_list.setFixedHeight(500)
        self.data_list.setMinimumWidth(180)
        self.data_list.setSizePolicy(q.QSizePolicy.Policy.Expanding, q.QSizePolicy.Policy.Expanding)
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
        self.data_list.itemDoubleClicked.connect(self.on_item_clicked_show_info)
        
        
            
            
        right_layout.addWidget(self.data_list)
        



        
        self.work_station_label = q.QLabel("", self)
        self.work_station_label.setStyleSheet("font: Arial; font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px; margin-bottom: 10px;")
        self.work_station_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.work_station_label)
        
        self.operator_label = q.QLabel("Оператор: ", self)
        self.operator_label.setStyleSheet("font: Arial; font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px; margin-top: 10px;")
        self.operator_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.operator_label)
        
        
        self.qty_label = q.QLabel("Количества по поръчка:", self)
        self.qty_label.setStyleSheet("font: Arial; font-size: 30px; font-weight: bold; color: white; margin-bottom: 10px; margin-top: 10px;")
        self.qty_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.qty_label)
        
        
        
        self.inspected_qty = q.QLineEdit()
        self.inspected_qty.setValidator(QtGui.QIntValidator(0, 999999, self.inspected_qty))
        self.inspected_qty.setPlaceholderText("Общо Кол.")
        self.inspected_qty.setStyleSheet("background-color: #ffffff; font-size: 24px; border-radius: 3px;")  # Розов фон")
        self.inspected_qty.setMinimumWidth(0)
        self.inspected_qty.setSizePolicy(q.QSizePolicy.Policy.Expanding, q.QSizePolicy.Policy.Fixed)
        self.inspected_qty.setEchoMode(q.QLineEdit.EchoMode.Normal)  # Направете полето само за четене, ако е необходимо
        

        self.passed_qty = q.QLineEdit()
        self.passed_qty.setValidator(QtGui.QIntValidator(0, 999999, self.passed_qty))
        self.passed_qty.setPlaceholderText("OK Кол.")
        self.passed_qty.setStyleSheet("background-color: #ffffff; font-size: 24px; color: green; border-radius: 3px;")  # Светлозелен фон
        self.passed_qty.setMinimumWidth(0)
        self.passed_qty.setSizePolicy(q.QSizePolicy.Policy.Expanding, q.QSizePolicy.Policy.Fixed)
        self.passed_qty.setEchoMode(q.QLineEdit.EchoMode.Normal)
          # Направете полето само за четене, ако е необходимо
                
        self.failed_qty = q.QLineEdit()
        self.failed_qty.setValidator(QtGui.QIntValidator(0, 999999, self.failed_qty))
        self.failed_qty.setPlaceholderText("NOK Кол.")
        self.failed_qty.setStyleSheet("background-color: #ffffff; font-size: 24px; color: red; border-radius: 3px;")  # Розов фон
        self.failed_qty.setMinimumWidth(0)
        self.failed_qty.setSizePolicy(q.QSizePolicy.Policy.Expanding, q.QSizePolicy.Policy.Fixed)
        self.failed_qty.setEchoMode(q.QLineEdit.EchoMode.Normal)  # Направете полето само за четене, ако е необходимо
          # Направете полето само за четене, ако е необходимо

        qty_layout.addStretch()
        qty_layout.addWidget(self.inspected_qty)
        qty_layout.addWidget(self.passed_qty)
        qty_layout.addWidget(self.failed_qty)
        
        qty_layout.addStretch()
        
        left_layout.addLayout(qty_layout)
        
        
        self.label = q.QLabel("BARCODE: ИЗЧАКВА СКАНИРАНЕ...", self)
        self.label.setStyleSheet("font: Arial; font-size: 30px; font-weight: bold; color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.label)
        
        
        self.time_label = q.QLabel("00:00:00", self)
        self.time_label.setStyleSheet("font: Arial; font-size: 30px; font-weight: bold; color: white; margin-top: 16px;")
        self.time_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.time_label)
        
        
        
        help_label = q.QLabel("Натисни ESC за изход | Press ESC to exit", self)
        help_label.setStyleSheet("font: Arial; font-size: 13px; font-weight: normal; color: white; margin-top: 16px;")
        help_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(help_label)
        
        
        
         
        
        back_button = q.QPushButton("LOG\nOUT", self)
        delete_scan_button = q.QPushButton("DELETE\n SCAN", self)
        print_label_button = q.QPushButton("ПЕЧАТ НА ЕТИКЕТ\nPRINT LABEL", self)
        print_label_button.setEnabled(True)
        print_label_button.setToolTip("Печат на етикет за избраната сканирана поръчка\nPrint label for the selected scanned order")
        print_label_button.clicked.connect(self.print_label)

        button_layout.addStretch()
        # ПОПРАВКА: Изтрита е излишната скоба отдолу
        # button_layout.addWidget(delete_scan_button)
        # ПОПРАВКА: Изтрита е излишната скоба отдолу
        back_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 5px 10px;
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
                font-size: 16px;
                font-weight: bold;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;  
            }
        """)
        
        print_label_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357ABD;  
            }
        """)
        back_button.setMinimumSize(90, 70)
        back_button.setMaximumSize(130, 100)
        
        
        delete_scan_button.setMinimumSize(90, 70)
        delete_scan_button.setMaximumSize(130, 100)
        delete_scan_button.clicked.connect(self.delete_scan)
        
        print_label_button.setMinimumWidth(70)
        # print_label_button.setMinimumHeight(70)
        
        # print_label_button.setFixedWidth(130)
        print_label_button.setMinimumHeight(70)
        print_label_button.setMaximumHeight(100)
        
        button_layout.addWidget(print_label_button)
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

        self.scan = Scan(self, self.time_label, self.work_station_label, self.operator_label, self.data_list, self.label, entry=entry, print_label_button=print_label_button, central_widget=central_widget, inspected_qty=self.inspected_qty, passed_qty=self.passed_qty, failed_qty=self.failed_qty)
        
        self.quantity_focus_timer = QTimer(self)
        self.quantity_focus_timer.setSingleShot(True)
        self.quantity_focus_timer.setInterval(700)
        self.quantity_focus_timer.timeout.connect(self.focus_scan_entry_if_quantities_set)
        for quantity_field in (self.inspected_qty, self.passed_qty, self.failed_qty):
            quantity_field.installEventFilter(self)
            quantity_field.editingFinished.connect(self.focus_scan_entry_if_quantities_set)
            quantity_field.textEdited.connect(self.schedule_scan_entry_focus)
        self.scan.entry.setFocus()

        self.scan.refresh_data_list()
    
    def showEvent(self, event):
        super().showEvent(event)
        if hasattr(self, 'scan') and self.scan.entry:
            self.scan.entry.setFocus()

    def hideEvent(self, event):
        super().hideEvent(event)
        if hasattr(self, 'scan') and self.scan.entry:
            self.scan.entry.clearFocus()

    def focus_scan_entry_if_quantities_set(self):
        quantity_fields = (self.inspected_qty, self.passed_qty, self.failed_qty)
        if all(field.text().strip() for field in quantity_fields):
            self.scan.entry.setFocus()

    def schedule_scan_entry_focus(self):
        self.quantity_focus_timer.start()

    def eventFilter(self, watched, event):
        quantity_fields = (self.inspected_qty, self.passed_qty, self.failed_qty)
        if (
            watched in quantity_fields
            and event.type() == QEvent.Type.KeyPress
            and event.text() == "#"
        ):
            self.scan.entry.setFocus()
            self.scan.entry.insert("#")
            return True
        return super().eventFilter(watched, event)

    def go_back(self):
        self.data_list.clear()
        self.scan.getLastScannedJobOrderID()
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
        # print(type(self.db_id))
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
                    # ПОПРАВКА: при неуспешен DELETE транзакцията остава отворена без rollback -
                    # добавяме го тук, за да не увисне връзката "idle in transaction"
                    # (същия проблем, заради който по-рано увисна ALTER TABLE за 3+ часа).
                    g_model.conn.rollback()
                else:
                    return
    def print_label(self):
        print("Print label button clicked")
        if self.db_id == None:
            q.QMessageBox.warning(self, "Предупреждение!", "Няма избрано съдържание за печат.")
            return
        g_model = GlobalModel()
        if g_model.conn is None:
            print("Database connection is not established.")
            return
        
        try:
            with g_model.conn.cursor() as cursor:
                query = """
            select ss.job_order_id, pr.ma_number, COALESCE(pr."name", '-'),jo.price_offer_num,  ss.inspected_qty, ss.passed_qty, ss.failed_qty, usr.first_name
            FROM station_scans ss
            LEFT JOIN job_orders jo ON jo.job_order_number = CAST(ss.job_order_id AS TEXT)
            left join products pr on pr.id = jo.product_id
            left join users usr on usr.id = ss.user_id
            WHERE ss.id = %s """
                cursor.execute(query, (self.db_id,))
                result = cursor.fetchone()
                if result:
                    product = result[2]
                    ma = result[1]
                    qty = result[4]
                    job = result[0]
                    barcode = f"{product}-{ma}-{job}-{qty}"
                    pon = result[3]
                    copies = 1
                    date = time.strftime("%d.%m.%Y")
                    
                    printer = PrintLabel()
                    printer.print_label(product, ma, qty, job, barcode, pon, copies, date)
                else:
                    q.QMessageBox.warning(self, "Грешка", f"Сканираното съдържание с ID {self.db_id} не е намерено.")
        except Exception as e:
            q.QMessageBox.critical(self, "Грешка", f"Грешка при печат на етикета: {e}")
    
    
        
        
        
        
        
        

            
    def on_item_clicked(self, item):
    # PySide automatically passes the clicked QListWidgetItem into this function
    # Now you can grab the custom ID you saved earlier!
        db_id = item.data(Qt.ItemDataRole.UserRole) # Use Qt.UserRole if on PySide2
        if db_id:
            self.db_id = db_id
            print(f"Selected scan with DB ID: {self.db_id}")
            
    
                   
    def on_item_clicked_show_info(self, item):
        g_model = GlobalModel()
        db_id = item.data(Qt.ItemDataRole.UserRole) # Use Qt.UserRole if on PySide2
        if db_id:
            self.db_id = db_id
            try:
                with g_model.conn.cursor() as cursor:
                    query = """
                select ss.job_order_id, pr.ma_number, COALESCE(pr."name", '-'),jo.price_offer_num,  ss.inspected_qty, ss.passed_qty, ss.failed_qty, usr.first_name
FROM station_scans ss
LEFT JOIN job_orders jo ON jo.job_order_number = CAST(ss.job_order_id AS TEXT)
left join products pr on pr.id = jo.product_id
left join users usr on usr.id = ss.user_id
WHERE ss.id = %s """
                # ПОПРАВКА: Подаваме динамично текущата станция вместо твърдото число 4
                    cursor.execute(query, (self.db_id,))
                    cursor.connection.commit()
                    if cursor.rowcount > 0:
                        result = cursor.fetchone()  
                        lines = [
                            f"Information for scan ID: {self.db_id}",
                            "",
                            f"Поръчка №: {result[0]}",
                            f"Продукт код: {result[1]}",
                            f"Продукт име: {result[2]}",
                            f"Оферта №: {result[3]}",
                            f"Общо кол.: {result[4]}",
                            f"ОK. кол.: {result[5]}",
                            f"NOK кол.: {result[6]}",
                            f"Обработен от: {result[7]}",
                        ]
                        q.QMessageBox.information(self, "Детайли по поръчката...", "\n".join(lines))
                            
                    else:
                        q.QMessageBox.warning(self, "Грешка", f"Сканираното съдържание с ID {self.db_id} не е намерено.")
            except Exception as e:
                q.QMessageBox.critical(self, "Грешка", f"Грешка при изтриване на сканираното съдържание: {e}")
                    # ПОПРАВКА: при неуспешен DELETE транзакцията остава отворена без rollback -
                    # добавяме го тук, за да не увисне връзката "idle in transaction"
                    # (същия проблем, заради който по-рано увисна ALTER TABLE за 3+ часа).
                g_model.conn.rollback()
            else:
                return
    