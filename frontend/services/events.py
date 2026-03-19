# events.py
from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    # Signal envoyé quand la base de données change (ajout ou présence validée)
    data_changed = pyqtSignal()

# Instance unique pour toute l'application
global_signals = AppSignals()