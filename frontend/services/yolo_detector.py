import os
from pathlib import Path

import cv2


class YoloDetector:
    """Optional YOLO detector used to annotate the existing video pipeline."""

    def __init__(self, model_path=None, confidence=0.25, device=None):
        from ultralytics import YOLO

        self.model_path = self._resolve_model_path(model_path)
        self.confidence = confidence
        self.device = device or os.getenv("YOLO_DEVICE")
        self.model = YOLO(str(self.model_path))

    @staticmethod
    def _resolve_model_path(model_path=None):
        if model_path:
            candidate = Path(model_path).expanduser()
            if candidate.exists():
                return candidate.resolve()
            raise FileNotFoundError(f"Modele YOLO introuvable : {candidate}")

        project_root = Path(__file__).resolve().parents[2]
        candidates = (
            project_root / "frontend" / "models" / "weights" / "yolov8n.pt",
            project_root / "frontend" / "models" / "weights" / "yolov8m.pt",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError("Aucun poids YOLO trouve dans le projet")

    def annotate(self, frame):
        prediction_kwargs = {
            "source": frame,
            "conf": self.confidence,
            "verbose": False,
        }
        if self.device:
            prediction_kwargs["device"] = self.device

        result = self.model.predict(**prediction_kwargs)[0]
        annotated = result.plot()
        detections = []
        for box, class_id, confidence in zip(
            result.boxes.xyxy.tolist(),
            result.boxes.cls.tolist(),
            result.boxes.conf.tolist(),
        ):
            detections.append({
                "label": result.names[int(class_id)].lower(),
                "confidence": float(confidence),
                "box": [int(value) for value in box],
            })
        person_count = sum(1 for detection in detections if detection["label"] == "person")
        cv2.putText(
            annotated,
            f"YOLO personnes: {person_count}",
            (10, 58),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 200, 0),
            2,
        )
        return annotated, detections