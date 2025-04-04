from ultralytics import YOLO

class YOLOv8Classifier:
    def __init__(self, model_path: str):
        # Load the YOLOv8 classification model
        self.model = YOLO(model_path)

    def classify(self, image):
        """
        Run inference on the provided image.

        Args:
            image: Image array (e.g., from OpenCV)

        Returns:
            The raw results from the YOLO model.
        """
        results = self.model(image)
        return results
