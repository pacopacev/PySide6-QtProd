import PySide6.QtWidgets as q
from PySide6.QtWidgets import QProgressDialog
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon
from scan import Scan
from global_model import GlobalModel
from ui.gui import QHSeparationLine
from ui.gui import Button
from ui.gui import FileUploadWidget
from ui.msg import WarningMessageBox
from addProduct.full_import import import_full_production_data
import os


class AddProductPage(q.QMainWindow):
    def __init__(self, stacked_widget=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.file_upload_widget = FileUploadWidget()
        print("AddProductPage initialized")
        self.add_product = addProduct(self.file_upload_widget, self)

        # Централен уиджет
        central_widget = q.QWidget()
        central_widget.setStyleSheet("background-color: #f0f0f0;")
        self.setCentralWidget(central_widget)

        # Основен layout за самия прозорец
        main_window_layout = q.QVBoxLayout(central_widget)
        main_window_layout.setAlignment(Qt.AlignCenter)
        main_window_layout.setContentsMargins(3, 3, 3, 3)

        add_mass_product_layout = q.QHBoxLayout()
        add_mass_product_layout.setSpacing(8)
        # add_mass_product_layout.setContentsMargins(10, 10, 10, 10)
        
        single_product_layout = q.QVBoxLayout()
        single_product_layout.setSpacing(8)
        # single_product_layout.setContentsMargins(10, 10, 10, 10)

        main_window_layout.addLayout(add_mass_product_layout)
        main_window_layout.addLayout(single_product_layout)

        add_mass_product_title_label = q.QLabel("Add mass products", self)
        add_mass_product_title_label.setAlignment(Qt.AlignCenter)
        add_mass_product_title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #000000; border: none;")
        add_mass_product_layout.addWidget(add_mass_product_title_label)

        add_mass_product_layout.addStretch()
        add_mass_product_layout.addWidget(self.file_upload_widget)

        mass_upload_button = Button(text="Mass Upload\n from Excel")
        add_mass_product_layout.addWidget(mass_upload_button)

        mass_upload_button.clicked.connect(self.add_product.mass_upload_file)

        Horizontal_line_color = "#4A90E2"
        horizontal_devider = QHSeparationLine(color=Horizontal_line_color)
        main_window_layout.addWidget(horizontal_devider)
        
        single_product_layout = q.QVBoxLayout()

        main_window_layout.addStretch()


class addProduct():
    """Holds the mass-upload logic. Kept as a plain class (not a QWidget),
    but needs a reference to a real QWidget (parent_widget) to parent dialogs."""

    def __init__(self, file_upload_widget, parent_widget):
        self.file_upload_widget = file_upload_widget
        self.parent_widget = parent_widget
        self.progress = None
        self.worker = None
        self.file_path = None

    def mass_upload_file(self):
        self.file_path = self.file_upload_widget.get_file_path()
        if self.file_path is None:
            WarningMessageBox("Flowbit", "Please select a file before proceeding.").exec_()
            return

        file_extension = os.path.splitext(self.file_path)[1].lower()
        if file_extension not in (".xlsx", ".xls"):
            WarningMessageBox("Flowbit", "Invalid file type. Please upload an Excel file.").exec_()
            self.file_upload_widget.clear_file_path()
            return

        # min=0, max=0 => busy/indeterminate spinner (no known % progress from the import fn)
        self.progress = QProgressDialog("Importing file...", "", 0, 0, self.parent_widget)
        self.progress.setWindowTitle("Flowbit")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.show()

        self.worker = ImportWorker(self.file_path)
        self.worker.finished_import.connect(self.on_import_finished)
        self.worker.start()
        # No synchronous import call here — the worker thread handles it.

    def on_import_finished(self, status, error):
        self.progress.close()
        if status:
            print("Import successful")
            WarningMessageBox("Flowbit", "The file has been successfully imported.").exec_()
        else:
            print(f"Import failed: {error}")
            error_message = error.args[0] if isinstance(error, Exception) and error.args else str(error)
            WarningMessageBox("Flowbit", error_message).exec_()
        self.file_upload_widget.clear_file_path()


class ImportWorker(QThread):
    """Runs the Excel import on a background thread so the UI stays responsive."""

    progress_updated = Signal(int)          # emit % complete (only if import fn supports it)
    finished_import = Signal(bool, object)  # (success, error_or_none)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            # If import_full_production_data can report progress, pass a callback:
            # status, error = import_full_production_data(self.file_path, progress_callback=self.progress_updated.emit)
            status, error = import_full_production_data(self.file_path)
            self.finished_import.emit(status, error)
        except Exception as e:
            self.finished_import.emit(False, e)