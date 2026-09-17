from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from components.cameraView import CameraView
from services.videoThread import VideoThread


class LiveView(QWidget):
    def __init__(self, alert_callback):
        super().__init__()
        self.alert_callback = alert_callback

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel("<b style='color:#247a50; font-size:18px;'>SURVEILLANCE EN DIRECT</b>")
        )

        grid = QGridLayout()
        self.cam1 = CameraView("SALLE EXAMEN A", "Identification & Posture")
        cameras = [
            self.cam1,
            CameraView("SALLE EXAMEN B", "Reconnaissance Faciale"),
            CameraView("COULOIR 1", "Comptage"),
            CameraView("ENTRÉE", "Vérification"),
        ]
        grid.addWidget(cameras[0], 0, 0)
        grid.addWidget(cameras[1], 0, 1)
        grid.addWidget(cameras[2], 1, 0)
        grid.addWidget(cameras[3], 1, 1)
        self.cams = cameras
        layout.addLayout(grid)

        self.thread = VideoThread(0)
        self.thread.change_pixmap_signal.connect(self.cam1.update_frame)
        self.thread.alert_signal.connect(self.alert_callback)
        self.thread.start()

    def stop_camera(self):
        if self.thread is not None:
            try:
                self.thread.change_pixmap_signal.disconnect()
                self.thread.alert_signal.disconnect()
            except TypeError:
                pass
            if self.thread.isRunning():
                self.thread.stop()
            self.thread = None
        self.cam1.clear_view()
