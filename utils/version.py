
import datetime
from PySide6 import QtWidgets as q



class Version(q.QWidget):
    def __init__(self, major, minor, patch):
        super().__init__()
        self.major = major
        self.minor = minor
        self.patch = patch
        
        
        self.build_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.version_label = q.QLabel(f"Version {self.major}.{self.minor}.{self.patch} build ({self.build_date})", self)
        self.version_label.setStyleSheet("font-size: 12px; color: #777; border: none;")
        
        

