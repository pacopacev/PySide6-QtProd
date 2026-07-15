from PySide6 import QtWidgets
from PySide6.QtWidgets import QFileDialog, QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt


class Button(QtWidgets.QPushButton):
    def __init__(self, parent=None, text = None):
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet("""QPushButton {background-color: #4A90E2; 
                                           color: white; 
                                           font-size: 13px; 
                                           font-weight: bold; 
                                           border-radius: 5px; 
                                           padding: 5px 13px;
                                           } QPushButton:hover {
                background-color: #357ABD;  
            }""")
        
class QHSeparationLine(QtWidgets.QFrame):
    def __init__(self, parent=None, color = None):
        super().__init__(parent)
        self.setFixedHeight(2)  # Височина на линията
        if color is not None:
            self.setStyleSheet(f"background-color: {color};")
        else:
            self.setStyleSheet("background-color: #000000;")  # Цвят на линията

        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        
        
        return
    
    
    
class FileUploadWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.init_ui()
        return

    def init_ui(self):
        layout = QHBoxLayout()

        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button)

        # self.file_label = QLabel("No file selected")
        # layout.addWidget(self.file_label)
        
        self.edit_field = QtWidgets.QLineEdit()
        self.edit_field.setPlaceholderText("No file selected")
        self.edit_field.setReadOnly(True)
        
        self.edit_field.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 5px;")
        layout.addWidget(self.edit_field)

        self.setLayout(layout)

    def upload_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_path, _ = file_dialog.getOpenFileName(self, "Select File")

        if file_path:
            self.edit_field.setText(file_path)
            self.file_path = file_path
            
    def get_file_path(self):
        return self.file_path
    
    
    def clear_file_path(self):
        self.edit_field.setText("No file selected")
        self.file_path = None
            
