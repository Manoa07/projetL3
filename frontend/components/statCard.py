from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class StatCard(QFrame):
    def __init__(self, title, value, color="#2e9d68"):
        super().__init__()
        self.setObjectName("Card")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: 1px solid #e4e9ef;
                border-radius: 14px;
                padding: 16px;
            }}
            QLabel {{ border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        val_label = QLabel(value)
        val_label.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {color};")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #718096; font-size: 11px; letter-spacing: 0.4px;")
        layout.addWidget(val_label)
        layout.addWidget(title_label)
