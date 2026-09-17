from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class AlertCard(QFrame):
    def __init__(self, text, time, critical=False):
        super().__init__()
        self.setObjectName("Card")
        color = "#d92d20" if critical else "#d97706"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #fff7f5;
                border: 1px solid #f3c7c2;
                border-left: 5px solid {color};
                border-radius: 8px;
            }}
            QLabel {{ color: #17212b; border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 9, 10, 9)
        layout.setSpacing(4)
        message_label = QLabel(f"<b>{text}</b>")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #7f1d1d; font-size: 11px;")
        layout.addWidget(message_label)
        time_lbl = QLabel(time)
        time_lbl.setStyleSheet("color: #9a5b55; font-size: 10px; font-weight: 600;")
        layout.addWidget(time_lbl)
