from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSpinBox, QDialogButtonBox

class PortDialog(QDialog):
    def __init__(self, current_port=1883, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка MQTT порта")
        self.setMinimumWidth(350)
        layout = QVBoxLayout()
        
        self.label = QLabel("Введите новый порт брокера:")
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(current_port)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.label)
        layout.addWidget(self.port_spin)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_port(self):
        return self.port_spin.value()