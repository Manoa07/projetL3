from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel

class StatCard(QFrame):
    def __init__(self, title, value, color="#4facfe"):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1a1c2e;
                border: 1px solid #2d2f41;
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{ border: none; background: none; }}
        """)
        layout = QVBoxLayout(self)
        val_label = QLabel(value)
        val_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7a7c8c; font-size: 11px;")
        layout.addWidget(val_label)
        layout.addWidget(title_label)