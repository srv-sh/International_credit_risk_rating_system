from src.DetectTable import TableDetection
from src.utils.NonMaximumSuppression import non_max_suppression
from  src.RecogniseStucture import TableStuctureRecognisation
from src import config as cfg
from PIL import Image , ImageDraw
import torch

class main():
    def __init__(self):
        self.table_detection = TableDetection()
        self.stucture_recognisation = TableStuctureRecognisation()
    
    def detect_table(self, image):
        w , h = image.size
        outputs =  self.table_detection.detect(image=image)
        objects = self.table_detection.outputs_to_objects(outputs, image.size)
        tokens = cfg.tokens
        detection_class_thresholds = cfg.detection_class_thresholds
        crop_padding =  cfg.crop_padding
        tables_crops = self.table_detection.objects_to_crops(image, tokens, objects, detection_class_thresholds, crop_padding )
        cropped_table = tables_crops[0]['image'].convert("RGB")
        return cropped_table
    
    def recognise_stucture(self,cropped_table):
        outputs = self.stucture_recognisation.recognise(croped_image=cropped_table)
        cells = self.stucture_recognisation.outputs_to_objects(outputs=outputs, img_size=cropped_table.size)
        return cells
    

if __name__=="__main__":
    main_cls = main()
    image = Image.open("/home/aiml/CredirScoring/envoyTex_sheets/balance_sheet.png").convert("RGB")
    cropped_table = main_cls.detect_table(image=image)
    cells = main_cls.recognise_stucture(cropped_table)
    detected_rows = [cell['bbox'] for cell in cells if cell['label']=='table row']
    scores = [cell['score'] for cell in cells if cell['label']=='table row']
    nms_indices =non_max_suppression(detected_rows,scores,iou_threshold=0.1)
    final_rows = [detected_rows[i] for i in nms_indices]
    print(len(cells))
    print(len(detected_rows))
    print(len(final_rows))
    # print()



    cropped_table_visual = cropped_table.copy()
    draw = ImageDraw.Draw(cropped_table_visual)

    for i , box in enumerate(final_rows):
        # box = cell['bbox']
        draw.rectangle(box, outline="red")
    cropped_table_visual.save("image/table_nms.png")









