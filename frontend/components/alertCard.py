from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class AlertCard(QFrame):
    def __init__(self, text, time, critical=False):
        super().__init__()
        color = "#e74c3c" if critical else "#f39c12"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #252836;
                border-left: 4px solid {color};
                border-radius: 4px;
                padding: 10px;
                margin-bottom: 5px;
            }}
            QLabel {{ color: white; border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>{text}</b>"))
        time_lbl = QLabel(time)
        time_lbl.setStyleSheet("color: #7a7c8c; font-size: 10px;")
        layout.addWidget(time_lbl)