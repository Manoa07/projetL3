import argparse
import os
import sys
import time
from pathlib import Path

import cv2
from ultralytics import YOLO


DEFAULT_MODEL = "yolov8n.pt"
DEFAULT_CONF = 0.25


def load_model(model_path: str = DEFAULT_MODEL, device: str = "cpu", conf: float = DEFAULT_CONF) -> YOLO:
    if not Path(model_path).exists():
        raise FileNotFoundError(f"Modèle introuvable : {model_path}")
    model = YOLO(model_path)
    # Assure on utilise le bon device si la version de la librairie supporte model.to()
    try:
        model = model.to(device)
    except Exception:
        pass
    model.overrides = {"conf": conf}
    return model


def detect_frame(model: YOLO, frame):
    results = model(frame)
    annotated = results[0].plot()
    return results[0], annotated


def run_camera(model: YOLO, device_index: int = 0, window_name: str = "YOLOv8 Surveillance"):
    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        raise RuntimeError(f"Impossible d'ouvrir la camera {device_index}.")

    print("Appuyez sur 'q' pour quitter.")
    fps_avg = []
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Erreur lecture camera.")
                break

            start = time.time()
            _, annotated = detect_frame(model, frame)
            fps = 1.0 / (time.time() - start + 1e-6)
            fps_avg.append(fps)
            cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow(window_name, annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if fps_avg:
            print(f"FPS moyen: {sum(fps_avg)/len(fps_avg):.1f}")


def run_image(model: YOLO, input_path: str, output_path: str = None):
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Image introuvable : {input_path}")

    img = cv2.imread(input_path)
    if img is None:
        raise RuntimeError(f"Impossible de lire l'image : {input_path}")

    results, annotated = detect_frame(model, img)
    print(f"Nombre d'objets détectés : {len(results.boxes)}")
    if output_path:
        cv2.imwrite(output_path, annotated)
        print(f"Image annotée enregistrée: {output_path}")
    else:
        cv2.imshow("Détection image", annotated)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def evaluate_image(model: YOLO, image_path: str):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image introuvable ou illisible: {image_path}")
    results = model(image)
    return len(results[0].boxes), [x.cls for x in results[0].boxes]


def optimize_model(model: YOLO, output_dir: str = "optimized", formats=("onnx", "engine")):
    out_folder = Path(output_dir)
    out_folder.mkdir(parents=True, exist_ok=True)
    exported = []
    for f in formats:
        try:
            result = model.export(format=f)
            print(f"Modèle exporté en {f}: {result}")
            exported.append(result)
        except Exception as exc:
            print(f"Erreur export {f}: {exc}")
    return exported


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Prototype détection objets YOLOv8")
    parser.add_argument("--mode", choices=["camera", "image", "test", "optimize"], default="camera", help="Mode d'exécution")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Fichier de poids YOLO")
    parser.add_argument("--device", default="cpu", help="Device YOLO (cpu ou cuda)")
    parser.add_argument("--conf", type=float, default=DEFAULT_CONF, help="Seuil de confiance")
    parser.add_argument("--camera", type=int, default=0, help="Index caméra")
    parser.add_argument("--input", help="Fichier image d'entrée pour mode image/test")
    parser.add_argument("--output", help="Fichier image annotée de sortie pour mode image")
    parser.add_argument("--output-dir", default="optimized", help="Dossier sortie optimisation")
    return parser.parse_args(argv)


def main():
    args = parse_args()

    if not Path(args.model).exists():
        print(f"Erreur: modèle non trouvé : {args.model}")
        sys.exit(1)

    model = load_model(args.model, device=args.device, conf=args.conf)

    if args.mode == "camera":
        run_camera(model, device_index=args.camera)
    elif args.mode == "image":
        if not args.input:
            raise ValueError("--input requis pour mode image")
        run_image(model, args.input, args.output)
    elif args.mode == "test":
        if not args.input:
            raise ValueError("--input requis pour mode test")
        n, classes = evaluate_image(model, args.input)
        print(f"Test détection: {n} boîtes, classes: {classes}")
    elif args.mode == "optimize":
        optimize_model(model, output_dir=args.output_dir)
    else:
        raise ValueError(f"Mode inconnu : {args.mode}")


if __name__ == "__main__":
    main()
