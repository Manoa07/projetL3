import os

from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from components.cameraView import CameraView
from services.videoThread import VideoThread


class LiveView(QWidget):
    def __init__(self, alert_callback):
        super().__init__()
        self.alert_callback = alert_callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(
            QLabel("<b style='color:#243447; font-size:18px;'>SURVEILLANCE EN DIRECT</b>")
        )

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
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

        self.threads = []
        camera_names = [
            "SALLE EXAMEN A",
            "SALLE EXAMEN B",
            "COULOIR 1",
            "ENTRÉE",
        ]
        sources = self._camera_sources()
        for camera_index, source in enumerate(sources[:len(cameras)]):
            thread = VideoThread(source, camera_names[camera_index])
            thread.change_pixmap_signal.connect(cameras[camera_index].update_frame)
            thread.alert_signal.connect(self.alert_callback)
            thread.start()
            self.threads.append(thread)

    @staticmethod
    def _camera_sources():
        configured = os.getenv("CAMERA_SOURCES", "1,0")
        sources = []
        for value in configured.split(","):
            value = value.strip()
            if not value:
                continue
            try:
                sources.append(int(value))
            except ValueError:
                sources.append(value)
        return sources or [0]

    def stop_camera(self):
        for thread in self.threads:
            try:
                thread.change_pixmap_signal.disconnect()
                thread.alert_signal.disconnect()
            except TypeError:
                pass
            if thread.isRunning():
                thread.stop()
        self.threads.clear()
        for camera in self.cams:
            camera.clear_view()
