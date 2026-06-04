from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class AlertCard(QFrame):
    def __init__(self, text, time, critical=False):
        super().__init__()
        self.setObjectName("Card")
        color = "#e74c3c" if critical else "#f39c12"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1f2f;
                border: 1px solid #23283d;
                border-left: 4px solid {color};
                border-radius: 12px;
                padding: 12px;
            }}
            QLabel {{ color: #f4f7fb; border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        layout.addWidget(QLabel(f"<b>{text}</b>"))
        time_lbl = QLabel(time)
        time_lbl.setStyleSheet("color: #7a7c8c; font-size: 10px;")
        layout.addWidget(time_lbl)
