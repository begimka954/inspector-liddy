class YOLODetector:
    # YOLOv8 nano. Fast, lightweight, occasionally wrong about a stapler.
    # Like most witnesses, it sees clearly and interprets loosely.
    def __init__(self):
        self.model = None
        self._load()

    def _load(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")  # nano -- Inspector Liddy travels light
        except Exception as e:
            print(f"YOLO refused to load: {e}. Inspector Liddy is working blind. She manages.")

    def detect(self, image_array):
        """RGB numpy array in. List of detection dicts out. Simple. She appreciates simple."""
        if self.model is None:
            return []

        results    = self.model(image_array, verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                label = self.model.names[int(box.cls)]
                conf  = float(box.conf)
                bbox  = box.xyxy[0].tolist()
                detections.append({
                    "class":      label,
                    "confidence": round(conf, 3),
                    "bbox":       bbox,
                })

        return detections

    def annotate(self, image_array, detections):
        """
        Draw bounding boxes on an RGB image.
        She marks what she has seen. Green because red felt presumptuous before the accusation.
        """
        import cv2
        img = image_array.copy()
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            label = det["class"]
            conf  = det["confidence"]
            cv2.rectangle(img, (x1, y1), (x2, y2), (100, 220, 130), 2)
            cv2.putText(
                img, f"{label} {conf:.2f}",
                (x1, max(y1 - 6, 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 220, 130), 1,
            )
        return img
