
import datetime
from PySide6 import QtWidgets as q



class Version(q.QWidget):
    def __init__(self, major, minor, patch, change_log=None):
        super().__init__()
        self.major = major
        self.minor = minor
        self.patch = patch
        self.change_log = change_log
        
        
        self.build_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.version_label = q.QLabel(f"Version {self.major}.{self.minor}.{self.patch} build ({self.build_date})", self)
        self.version_label.setStyleSheet("font-size: 12px; color: #777; border: none;")
        self.version_label.setToolTip(f"Build date: {self.change_log if self.change_log else 'No change log available.'}")
        
        

