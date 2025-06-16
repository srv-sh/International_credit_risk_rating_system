from ultralytics import YOLO
import cv2
import os
import numpy as np

class getTableOnly():
    def __init__(self):
        self.checkpoint_path = '/home/sourav/workspace/CreditScoring-refined-/data/best.pt'
        self.model = YOLO(self.checkpoint_path)
    
    def detect(self, image, save=False):
        # Convert PIL image to OpenCV image (numpy array)
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        results = self.model(image)[0]
        for i, box in enumerate(results.boxes):
            class_id = int(box.cls[0])
            label = self.model.names[class_id]

            if label.lower() == 'table':  # Save only if class is 'table'
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                # Crop and save
                cropped = image[y1:y2, x1:x2]
                if save:
                    output_dir = "crops"
                    os.makedirs(output_dir, exist_ok=True)
                    crop_filename = f"{output_dir}/table_{i}_conf{conf:.2f}.jpg"
                    cv2.imwrite(crop_filename, cropped)
                    print(f"[INFO] Saved: {crop_filename}")

                return cropped

if __name__ == "__main__":
    get_table_cls = getTableOnly()
    cropped_image = get_table_cls.detect('/home/sourav/workspace/table_recognisation_model/data/idlc/ashraf_june233.png')
    print(cropped_image)

