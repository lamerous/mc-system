# host_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox

class HostDialog(QDialog):
    def __init__(self, current_host="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка MQTT хоста")
        self.setMinimumWidth(350)  
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Введите новый хост брокера:")
        self.host_edit = QLineEdit()
        self.host_edit.setText(current_host)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.label)
        layout.addWidget(self.host_edit)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_host(self):
        return self.host_edit.text().strip()