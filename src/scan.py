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
    def __init__(self, page, time_label=None, work_station_label=None, operator_label=None, data_list=None, label=None, entry=None, print_label_button=None, central_widget=None, inspected_qty=None, passed_qty=None, failed_qty=None):
        super().__init__()
        self.page = page
        self.time_label = time_label
        self.work_station_label = work_station_label
        self.operator_label = operator_label
        self.data_list = data_list
        self.label = label
        self.computer_name = socket.gethostname()
       
       
        self.central_widget = central_widget
        
        self.inspected_qty = inspected_qty
        self.passed_qty = passed_qty
        self.failed_qty = failed_qty
        
        
        # Пускаме си таймера за часа
        self.timer = QTimer(self)
        
        self.timer.timeout.connect(self.update_time)
        

        self.entry = entry
        self.print_label_button = print_label_button
        if self.print_label_button:
            self.print_label_button.clicked.connect(self.clear_scan)

        self.timer.start(1000)

        self.update_time()
        self.set_work_station()
        
        

        # Use the provided entry if available; otherwise create one parented to the page
        if self.entry:
            self.entry.returnPressed.connect(self.barcode_scanned)
            print("Using provided QLineEdit for barcode scanning.")
        else:
            print("No QLineEdit provided. Creating a new one for barcode scanning.")
            # parent the QLineEdit to the page (a QWidget) instead of this QObject
            self.entry = q.QLineEdit(self.page)
            self.entry.hide()
            self.entry.returnPressed.connect(self.barcode_scanned)
    

    def clear_qty_fields(self):
            self.inspected_qty.clear()
            self.passed_qty.clear()
            self.failed_qty.clear()
            self.db_id = None  # Reset the db_id when clearing the fields
    
    
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
            # ПОПРАВКА: SELECT-ът пак отваря транзакция в psycopg2 — без commit/rollback
            # тя остава отворена ("idle in transaction") и може да блокира бъдещ ALTER TABLE / DDL.
            g_model.conn.commit()
        except Exception as e:
            print(f"Грешка при дърпане на оператор: {e}")
            # ПОПРАВКА: при грешка транзакцията пак остава отворена — правим rollback.
            g_model.conn.rollback()
            
    def getLastScannedJobOrderID(self):
        self.station_id = self.get_station_id()
        print(self.station_id)
        g_model = self.page.stacked_widget.model
        if g_model.conn is None:
            return

        if self.data_list is not None:
            self.data_list.clear()

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
            # ПОПРАВКА: затваряме тази read-only транзакция, за да не стои връзката
            # "idle in transaction" и да не държи ключалки върху station_scans.
            g_model.conn.commit()
                   
        except Exception as e:
            print(f"Грешка при извличане на поръчките: {e}") # Винаги принтирай грешката в try-except, за да знаеш ако нещо се счупи!
            # ПОПРАВКА: rollback, за да не остане връзката закачена в средата на транзакция при грешка.
            g_model.conn.rollback()
        
    
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
            # ПОПРАВКА: същия риск от "idle in transaction" — затваряме след четенето.
            # ЗАБЕЛЕЖКА: и двата пътя с `return result[0]` по-горе прескачат този ред,
            # затова този commit се изпълнява само по пътя "станция не е намерена". Виж бележката под кода.
            g_model.conn.commit()
        except Exception as e:
            print(f"Грешка при извличане на станциите: {e}")
            g_model.conn.rollback()
            
    def refresh_data_list(self):
        
        print("refresh_data_list")
        self.data_list.clear()
        
    
    def clear_scan(self):
        if self.entry:
            self.entry.clear()
            self.entry.setFocus()
        if self.label:
            self.label.setText("BARCODE: ИЗЧАКВА СКАНИРАНЕ...")
            self.clear_qty_fields()
        if self.print_label_button:
            self.print_label_button.setEnabled(False)
    def reset_ui(self):
        self.central_widget.setStyleSheet("background-color: #0047AB;")
        self.label.setText("BARCODE: ИЗЧАКВА СКАНИРАНЕ...")
        self.clear_scan()
    def barcode_scanned(self):
        inspected_qty = self.inspected_qty.text().strip() if self.inspected_qty else ""
        passed_qty = self.passed_qty.text().strip() if self.passed_qty else ""
        failed_qty = self.failed_qty.text().strip() if self.failed_qty else ""
        
        if not self.check_corect_input_qty(inspected_qty, passed_qty, failed_qty):
            q.QMessageBox.warning(self.page, "Внимание!", "Моля, въведете правилно количество за ОБЩО, OK и NOK.")
            return

        to_record_to_database = True

        print("Баркод сканиран")
        raw_barcode = self.entry.text().strip()
        barcode = raw_barcode.removeprefix("#")
        print(f"Сканиран баркод: {barcode}")

        if not barcode.isascii() or not barcode.isdigit():
            q.QMessageBox.warning(self.page, "Невалиден баркод", "Баркодът трябва да съдържа само цифри и може да започва с #.")
            if self.entry:
                self.entry.clear()
                self.entry.setFocus()
            return
        
      
        
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
                text = f"Баркодът: {barcode} вече е сканиран"
            else:
                text = f"Сканиран е баркод: {barcode}"
            self.label.setText(text)
            self.label.show()
            
            if self.print_label_button:
                self.print_label_button.setEnabled(True)
            
            
            if to_record_to_database: 
                self.record_scan_to_db(barcode, inspected_qty, passed_qty, failed_qty)
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
                    # ПОПРАВКА: това е точно заявката, която открихме "idle in transaction"
                    # за над 3 часа и блокира ALTER TABLE по-рано. Затваряме я преди да върнем резултат.
                    g_model.conn.commit()
                    return True
                else:
                    print(f"Баркодът {barcode} е нов")
                    g_model.conn.commit()
                    return False
        except Exception as e:    
            print(f"Грешка при проверка на баркодите: {e}")
            g_model.conn.rollback()
    def record_scan_to_db(self, barcode, inspected_qty, passed_qty, failed_qty):
        g_model = self.page.stacked_widget.model
        if g_model.conn is None:
            return
        try:
            with g_model.conn.cursor() as cursor:
                query = """
                INSERT INTO station_scans (job_order_id, station_id, scanned_at, user_id, inspected_qty, passed_qty, failed_qty)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (barcode, self.get_station_id(), datetime.now(), g_model.get_user_id(), inspected_qty, passed_qty, failed_qty))
                g_model.conn.commit()
                
        except Exception as e:    
            print(f"Грешка при записване на сканираните баркoдове: {e}")
            # ПОПРАВКА: при неуспешен insert, правим rollback вместо да оставим транзакцията отворена.
            g_model.conn.rollback()
            return
        self.refresh_data_list()
        self.getLastScannedJobOrderID()
        
    def check_corect_input_qty(self, inspected_qty, passed_qty, failed_qty):
        try:
            quantities = tuple(int(value) for value in (inspected_qty, passed_qty, failed_qty))
        except (TypeError, ValueError):
            quantities = ()

        is_valid = len(quantities) == 3 and all(value >= 0 for value in quantities) and sum(value != 0 for value in quantities) >= 2
        if not is_valid:
            self.inspected_qty.clear()
            self.passed_qty.clear()
            self.failed_qty.clear()
            if self.entry:
                self.entry.clear()
        return is_valid
        
    