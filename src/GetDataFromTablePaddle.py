from .GetTableFromImage import getTableOnly
from .GetOCRFromPaddle import getOCR
from .GetTableStucture import getStucture
from .GetResponseFromLLM import GetResponseFromOpenAI
from .  import config as cfg
import numpy as np
import pandas as pd
# from allinone import allinone


class getData():

    def __init__(self, provider=None):
        self.table_detection_class = getTableOnly()
        self.ocr_model = getOCR()
        self.llm_model = GetResponseFromOpenAI(provider=provider)
        

    def intersection(self,box_1, box_2):
        return [box_2[0], box_1[1], box_2[2], box_1[3]]

    def iou(self,box_1, box_2):
        x_1 = max(box_1[0], box_2[0])
        y_1 = max(box_1[1], box_2[1])
        x_2 = min(box_1[2], box_2[2])
        y_2 = min(box_1[3], box_2[3])

        inter = max((x_2 - x_1), 0) * max((y_2 - y_1), 0)
        if inter == 0:
            return 0

        box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
        box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

        return inter / float(box_1_area + box_2_area - inter)
           
    def convert_to_markdown(self, lines , method = 'cluster'):
        if method == 'cluster':
            horiz_lines = lines['horiz_lines']
            vert_lines = lines['vert_lines']
            boxes = lines['boxes']
            texts = lines['texts']

            out_array = [["" for _ in range(len(vert_lines))] for _ in range(len(horiz_lines))]

            # Sort vertical lines by their x1 coordinate
            unordered_boxes = [line[0] for line in vert_lines]
            ordered_boxes = np.argsort(unordered_boxes)

            # Populate out_array
            for i in range(len(horiz_lines)):
                for j in range(len(vert_lines)):
                    # get the grid cell bounding box
                    resultant = self.intersection(horiz_lines[i], vert_lines[ordered_boxes[j]])

                    for b in range(len(boxes)):
                        the_box = boxes[b]
                        if self.iou(resultant, the_box) > 0.15:
                            out_array[i][j] = texts[b]

            out_array = np.array(out_array)
            out_array_df = pd.DataFrame(out_array)
            # print(out_array_df)
            out_array_markdown =  out_array_df.to_markdown(index= False)
            return out_array_markdown

        if method == 'normal':
            unordered_boxes = []
            
            horiz_boxes = lines['horiz_boxes']
            vert_boxes = lines['vert_boxes']
            sorted_horiz_lines = lines['sorted_horiz_lines']
            sorted_vert_lines = lines['sorted_vert_lines']
            boxes = lines['boxes']
            texts = lines['texts']
            
            out_array = [["" for i in range(len(sorted_vert_lines))] for j in range(len(sorted_horiz_lines))]

            for i in sorted_vert_lines:
                unordered_boxes.append(vert_boxes[i][0])
            
            ordered_boxes = np.argsort(unordered_boxes)
            for i in range(len(sorted_horiz_lines)):
                for j in range(len(sorted_vert_lines)):
                    resultant = self.intersection(horiz_boxes[sorted_horiz_lines[i]], vert_boxes[sorted_vert_lines[ordered_boxes[j]]])

                    for b in range(len(boxes)):
                        the_box = boxes[b]  # no nested indexing needed
                        if self.iou(resultant, the_box) > 0.1:
                            out_array[i][j] = texts[b]
            
            out_array = np.array(out_array)
            out_array_df = pd.DataFrame(out_array)

            out_array_markdown =  out_array_df.to_markdown(index= False)
            # print(out_array_markdown)
            return out_array_markdown



        # self.structure_recognisation = getStucture()

    def get_stucture_data(self, image_path, base_64 = True):
        cropped_table = self.table_detection_class.detect(image_path, base_64)
        ocr_info = self.ocr_model.predict(cropped_image=cropped_table)
        self.structure_recognisation = getStucture(ocr_information=ocr_info)
        all_info = self.structure_recognisation.boxes_from_image(method=cfg.method)
        
        # markdown = allinone(all_info)
        incorrect_markdown =  self.convert_to_markdown(all_info, method= cfg.method)
        print(incorrect_markdown)
        # correct_markdown

        correct_markdown = self.llm_model.get_response(incorrect_markdown)
        # correct_markdown = correct_markdown[~correct_markdown.apply(lambda row: row.astype(str).str.match(r'^-+$')).any(axis=1)]
        print(correct_markdown)
        text = ocr_info['texts']
        bbox = ocr_info['boxes']
        
        image = ocr_info['cropped_image']

        return {
                "incorrect_markdown" : incorrect_markdown,
                "correct_markdown":  correct_markdown, 
                "image":image,
                "text": text,
                "bbox" : bbox }
        




if __name__ == "__main__":
    get_data_cls = getData()
    get_data_cls.get_stucture_data("/home/sourav/workspace/CreditScoring-refined-/data/tables/bashundhara3.png", base_64 = False)




