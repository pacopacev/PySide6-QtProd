from datetime import datetime
import socket
import pandas as pd
import psycopg2
import os
import sys
from global_model import GlobalModel
from PySide6.QtCore import QObject, QTimer
import PySide6.QtWidgets as q
from PySide6.QtCore import Qt


class Scan(QObject):
    def __init__(self, page, time_label=None, work_station_label=None, operator_label=None, data_list=None, label=None, entry=None, clear_scan_button=None, central_widget=None):
        super().__init__()
        self.page = page
        self.time_label = time_label
        self.work_station_label = work_station_label
        self.operator_label = operator_label
        self.data_list = data_list
        self.label = label
        self.computer_name = socket.gethostname()
       
       
        self.central_widget = central_widget
        
        
        # Пускаме си таймера за часа
        self.timer = QTimer(self)
        
        self.timer.timeout.connect(self.update_time)
        

        self.entry = entry
        self.clear_scan_button = clear_scan_button
        if self.clear_scan_button:
            self.clear_scan_button.clicked.connect(self.clear_scan)

        self.timer.start(1000)

        self.update_time()
        self.set_work_station()

        # Use the provided entry if available; otherwise create one parented to the page
        if self.entry:
            self.entry.returnPressed.connect(self.barcode_scanned)
        else:
            # parent the QLineEdit to the page (a QWidget) instead of this QObject
            self.entry = q.QLineEdit(self.page)
            self.entry.hide()
            self.entry.returnPressed.connect(self.barcode_scanned)

    
    
    
    def update_time(self):
        self.time_now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        if self.time_label:
            self.time_label.setText(self.time_now)
            
    def set_work_station(self):
        if self.work_station_label:
            self.work_station_label.setText(f"Работна станция: {self.computer_name}")

    def get_user_info(self):
        # Взимаме споделения модел от MainWindow през страницата
        g_model = self.page.stacked_widget.model
        
        # Взимаме ID-то през ГЕТЪРА
        user_id = g_model.get_user_id()
        print(f"Поискано инфо за станция. Гетърът върна User ID: {user_id}")
        
        if not user_id:
            if self.operator_label:
                self.operator_label.setText("Оператор: Няма логнат потребител")
            return
            
        try:
            with g_model.conn.cursor() as cursor:
                cursor.execute("SELECT first_name FROM users WHERE id = %s", (user_id,))
                result = cursor.fetchone()
                if result and self.operator_label:
                    self.operator_label.setText(f"Оператор: {result[0]}")

                    print(f"Името '{result[0]}' е успешно изписано на екрана!")
        except Exception as e:
            print(f"Грешка при дърпане на оператор: {e}")
            
    def getLastScannedJobOrderID(self):
        self.station_id = self.get_station_id()
        print(self.station_id)
        g_model = self.page.stacked_widget.model
        if g_model.conn is None:
            return

        # Проверка: Ако станцията още не е заредена, използваме user_id като резервен вариант
        current_station = self.station_id if self.station_id else self.user_id
        if not current_station:
            print("Няма намерена станция или логнат потребител.")
            return

        try:
            with g_model.conn.cursor() as cursor:
                # query = """
                #     SELECT id, job_order_id, scanned_at FROM station_scans
                #     WHERE station_id = %s and scanned_at >= (CURRENT_DATE - INTERVAL '3 days')
                #     ORDER BY scanned_at DESC
                # """
                
                query = """
                    SELECT id, job_order_id, scanned_at FROM station_scans
                    WHERE station_id = %s
                    ORDER BY scanned_at DESC
                """
                # ПОПРАВКА: Подаваме динамично текущата станция вместо твърдото число 4
                cursor.execute(query, (current_station,))
                result = cursor.fetchall()
                
                if result:
                    for i in result:
                        
                        display_text = f"Поръчка ID: {i[1]} | Сканирано на: {i[2].strftime('%d.%m.%Y %H:%M')}"
                        item = q.QListWidgetItem(display_text)
                        item.setData(Qt.ItemDataRole.UserRole, i[0])
                        self.data_list.addItem(item)
                        # print(item.data(Qt.ItemDataRole.UserRole))
                        
                        
                        
                        
                else:
                    print(f"Няма намерени сканирания за последните 3 дни за станция {current_station}")
                current_item = self.data_list.currentItem()
                   
        except Exception as e:
            print(f"Грешка при извличане на поръчките: {e}") # Винаги принтирай грешката в try-except, за да знаеш ако нещо се счупи!
        
    
    def get_station_id(self):
        g_model = self.page.stacked_widget.model
        if g_model.conn is None:
            return

        try:
            with g_model.conn.cursor() as cursor:
                query = """
                    SELECT id FROM production_stations
                    WHERE computer_name = %s """
                # ПОПРАВКА: Подаваме динамично текущата станция вместо твърдото число 4
                cursor.execute(query, (self.computer_name,))
                result = cursor.fetchone()
                
                if result:
                    return result[0]
                else:
                    print(f"Няма намерена станция с име {self.computer_name}")
        except Exception as e:
            print(f"Грешка при извличане на станциите: {e}")
            
    def refresh_data_list(self):
        
        print("refresh_data_list")
        self.data_list.clear()
        
    
    def clear_scan(self):
        if self.entry:
            self.entry.clear()
            self.entry.setFocus()
        if self.label:
            self.label.setText("BARCODE: ИЗЧАКВА СКАНИРАНЕ...")
        if self.clear_scan_button:
            self.clear_scan_button.setEnabled(False)
    def reset_ui(self):
        self.central_widget.setStyleSheet("background-color: #0047AB;")
        self.label.setText("BARCODE: ИЗЧАКВА СКАНИРАНЕ...")
        self.clear_scan()
    def barcode_scanned(self):
        
        to_record_to_database = True
        
        print("Баркод сканиран")
        # Use .text() instead of .get()
        barcode = self.entry.text().strip()
        
      
        
        if barcode:
            status_barocode = self.checkBArcodeIfExists(barcode)
            if status_barocode:
                
                self.central_widget.setStyleSheet("background-color: #FF0000;")
                # self.label.setText(f"Баркодът: {barcode} вече е сканиран")
                self.timer.singleShot(2000, lambda: self.reset_ui())
                to_record_to_database = False
                
            
            self.clear_scan()
            
            
            # print(f"Сканиран е баркод: {barcode}")
            if to_record_to_database == False:
                self.label.setText(f"Баркодът: {barcode} вече е сканиран")
            else:
                text = f"Сканиран е баркод: {barcode}"
            self.label.setText(text)
            self.label.show()
            
            if self.clear_scan_button:
                self.clear_scan_button.setEnabled(True)
            
            
            if to_record_to_database: 
                self.record_scan_to_db(barcode)
            self.timer.singleShot(2000, lambda: self.clear_scan())
            
    def checkBArcodeIfExists(self, barcode):
        g_model = self.page.stacked_widget.model
        if g_model.conn is None:
            return
        try:
            with g_model.conn.cursor() as cursor:
                query = """
                SELECT id FROM station_scans
                WHERE job_order_id = %s
                """
                cursor.execute(query, (int(barcode),))
                result = cursor.fetchone()
                
                if result:
                    print(f"Баркодът {barcode} вече е сканиран")
                    return True
                else:
                    print(f"Баркодът {barcode} е нов")
                    return False
        except Exception as e:    
            print(f"Грешка при проверка на баркодите: {e}")
    def record_scan_to_db(self, barcode):
        g_model = self.page.stacked_widget.model
        if g_model.conn is None:
            return
        try:
            with g_model.conn.cursor() as cursor:
                query = """
                INSERT INTO station_scans (job_order_id, station_id, scanned_at, user_id)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (barcode, self.get_station_id(), datetime.now(), g_model.get_user_id(), ))
                g_model.conn.commit()
                
        except Exception as e:    
            print(f"Грешка при записване на сканираните баркоди: {e}")
        self.refresh_data_list()
        self.getLastScannedJobOrderID()
        
    
        
    
              
    