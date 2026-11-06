import sys
from global_model import GlobalModel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QLabel, QLineEdit
)

HEADERS = ["Id", "Name","Type_id","MA_code","Description","is_assembly","Created_at","Updated_at","Created_by","Alt_name",]

class ListProductPage(QWidget):
    def __init__(self, stacked_widget=None):
        super().__init__()
        
        self.txt =""
        
     
        self.setWindowTitle("QTableWidget example")
        self.resize(650, 400)

        # --- table setup ---
        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)               # all columns stretch
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)   # barcode fits content

        # --- buttons ---
        btn_add = QPushButton("Add row")
        btn_del = QPushButton("Delete selected")
        self.btn_get = QPushButton("Search")
        self.search_field_label = QLabel("Search...", self)
        self.search_field = QLineEdit(self)
        btn_add.clicked.connect(lambda: self.add_row("Station 1", "0000000000", 0, 0, 0))
        btn_del.clicked.connect(self.delete_selected)
        self.btn_get.clicked.connect(self.search_text)

        buttons = QHBoxLayout()
        buttons.addWidget(self.search_field_label)
        buttons.addWidget(self.search_field)
        buttons.addWidget(self.btn_get)
        # buttons.addWidget(btn_add)
        # buttons.addWidget(btn_del)
        # buttons.addWidget(btn_get)
        buttons.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)
        layout.addLayout(buttons)

        # react to edits and double clicks
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.cellDoubleClicked.connect(
            lambda r, c: print(f"Double click: row={r}, col={c}")
        )
        self.get_product_list()
        
    def search_text(self):
                
        self.txt = self.search_field.text()
        
        self.get_product_list()
    
        
        
        
    def get_product_list(self):
        g_model = GlobalModel()
        search_text = '%10.21.73069A%' 
        
        if self.txt:
            search_text = self.txt
            
            
             
        if g_model.conn is None:
            print("Database connection is not established.")
            return
        try:
            with g_model.conn.cursor() as cursor:
                query = """
                SELECT * FROM products 
                WHERE ma_number ILIKE %s 
                ORDER BY created_at DESC;
                """
                cursor.execute(query, (search_text,))
                result = cursor.fetchall()  # fetch all results
                
                # if result and search_text:
                #     for row in result:
                #         self.table.removeRow()
                #         return
                if result:
                    for row in result:
                        self.add_row(*row)
                        # print(row[1])
                
                    
        except Exception as e:
            print(f"Error executing query: {e}")
            
    def add_row(self, id,name,type_id,ma_number,description,is_assembly,created_at,updated_at,created_by,alt_name):
        self.table.setSortingEnabled(False)  # avoid rows jumping while filling
        self.table.blockSignals(True)        # don't fire itemChanged while filling

        r = self.table.rowCount()
        self.table.insertRow(r)

        values = [id,name,type_id,ma_number,description,is_assembly,created_at,updated_at,created_by,alt_name]
        for c, v in enumerate(values):
            item = QTableWidgetItem()
            # setData with a number (not str) makes sorting numeric instead of alphabetical
            if isinstance(v, int):
                item.setData(Qt.DisplayRole, v)
                item.setTextAlignment(Qt.AlignCenter)
            else:
                item.setText(str(v))
            # make Station and Barcode read-only, numbers editable
            if c < 2:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, c, item)

        self.color_nok(r)

        self.table.blockSignals(False)
        self.table.setSortingEnabled(True)

    def color_nok(self, row):
        """Highlight the NOK cell red if NOK > 0."""
        item = self.table.item(row, 4)
        if item is None:
            return
        nok = item.data(Qt.DisplayRole)
        try:
            nok = int(nok)
        except (TypeError, ValueError):
            nok = 0
        item.setBackground(QColor("#ffb3b3") if nok > 0 else QColor(0, 0, 0, 0))

    def on_item_changed(self, item):
        if item.column() == 4:
            self.color_nok(item.row())

    def delete_selected(self):
        rows = sorted({i.row() for i in self.table.selectedItems()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def get_data(self):
        """Return all rows as a list of tuples."""
        data = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.data(Qt.DisplayRole) if item else None)
            data.append(tuple(row))
        return data

    def print_data(self):
        for row in self.get_data():
            print(row)

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     w = TableExample()
#     w.show()
#     sys.exit(app.exec())

