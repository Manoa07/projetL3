from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class AlertCard(QFrame):
    def __init__(self, text, time, critical=False):
        super().__init__()
        self.setObjectName("Card")
        color = "#e74c3c" if critical else "#f39c12"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #fff8f5;
                border: 1px solid #f3d9d0;
                border-left: 4px solid {color};
                border-radius: 12px;
            }}
            QLabel {{ color: #253047; border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.addWidget(QLabel(f"<b>{text}</b>"))
        time_lbl = QLabel(time)
        time_lbl.setStyleSheet("color: #8994a8; font-size: 10px;")
        layout.addWidget(time_lbl)
