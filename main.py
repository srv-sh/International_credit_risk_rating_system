from src.DetectTable import TableDetection
from src.utils.NonMaximumSuppression import non_max_suppression
from  src.RecogniseStucture import TableStuctureRecognisation
from src import config as cfg
from PIL import Image , ImageDraw
import torch
from torchvision.ops import nms
from src.utils.OcrFromImage import OcrFromTableImage
from src.utils.GetCoordinateByRow import GetCoordinateByRow
import pandas as pd
import json
import re 

class main():

    def __init__(self):
        self.get_coordinate_cls = GetCoordinateByRow()
        self.ocr_model = OcrFromTableImage()
        self.table_detection = TableDetection()
        self.stucture_recognisation = TableStuctureRecognisation()

    def extract_dates(self, text):
        print(text)
        # Regular expression to match dates in various formats
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',      # Matches formats like 12/31/2023, 31-12-2023
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',        # Matches formats like 2023/12/31, 2023-12-31
            r'\b\d{1,2}[ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[ ]\d{2,4}\b',  # Matches 1 Jan 2023, 01 Jan 23, 1 Jan 2023
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[ ]\d{1,2},[ ]\d{4}\b',  # Matches Jan 1, 2023
            r'\b\d{1,2}[ ](?:January|February|March|April|May|June|July|August|September|October|November|December)[ ]\d{4}\b',  # Matches 30 June 2023
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)[ ]\d{1,2},[ ]\d{4}\b', # Matches June 30, 2023
            r'\b\d{4}\b'
        ]
    
        # Combine all the patterns into one
        combined_pattern = '|'.join(date_patterns)
        
        # Find all matches in the text
        dates = re.findall(combined_pattern, text)
        
        return dates


    def draw_image(self, cropped_table, columns_data):    
        cropped_table_visual = cropped_table.copy()
        draw = ImageDraw.Draw(cropped_table_visual)
        for i , cell in enumerate(columns_data):
            box = cell['bbox']
            draw.rectangle(box, outline="red")
        cropped_table_visual.save("image/table_nms.png")

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

    def merge_dicts(self,dict_list):
        # Initialize final dictionary
        final_dict = {
            "particulars": [],
            "2023": [],
            "2022": []
        }

        # Iterate over each dictionary in the list
        for d in dict_list:
            # Merge "particulars" list
            if "particulars" in d:
                final_dict["particulars"].extend(d["particulars"])  # Flatten and merge

            # Merge "2023" list
            if "2023" in d:
                final_dict["2023"].extend(d["2023"])  # Flatten and merge

            # Merge "2022" list
            if "2022" in d:
                final_dict["2022"].extend(d["2022"])  # Flatten and merge

        return final_dict
    

    def get_json(self,image_path):
        image = Image.open(image_path).convert("RGB")
            # cropped_table = main_cls.detect_table(image=image) # detect table and crop table
        cells = self.recognise_stucture(image) # recognise table stucture 
        table_cell = [cell for cell in cells if cell['label'] == "table"]
        print(table_cell)       
        table_bbox = table_cell[0]['bbox']
        cropped_table =  image.crop(table_bbox)
        
        cells = self.recognise_stucture(cropped_table=cropped_table) # recognise table stucture 

        # column header 
        columns_data = [cell for cell in cells if cell['label']=='table column header']
        # print(columns_data)
        column_header_bbox = columns_data[0]['bbox']
        column_header_cropped_img = cropped_table.crop(column_header_bbox)
        
        column_header = self.ocr_model.recognize(column_header_cropped_img, type="pil")
        column_header =  self.extract_dates(column_header)
        #########################
        if len(column_header) > 2:
            column_header = column_header[1:]
        #########################
        # row values 
        cell_coordinates =  self.get_coordinate_cls.get_cordinate(cells)
        rows =  self.ocr_model.get_df_from_table_image(cropped_table , cell_coordinates) # after run this line it will save csv file to the directory
        
        # store in  the dataframe
        data = pd.DataFrame(rows)
        shape =data.shape
        # print("-------", shape , "--------")
        if shape[1] == 3 :
            column_header.insert(0,"Particulars")
            print(column_header)
        elif shape[1] == 4:
            column_header.insert(0,"Particulars")
            column_header.insert(1,"Notes")
            print(column_header)
        data.columns = column_header
        data =data.dropna(how="all")
        
        col = data.columns
        print(col)
        particular = data[col[0]].tolist()
        year1 =  data[col[-2]].tolist()
        year2 =  data[col[-1]].tolist()

        return {"particulars" : particular,
         column_header[-2]: year1,
         column_header[-1]: year2
         }
    

if __name__=="__main__":
    main_cls = main() # main class
    files = ['table_data/tables/gp2.png']
    # files = ['table_data/tables/gp2.png']
    final_dict = {}
    total_dict =[]
    for file in files:
        dict_ =main_cls.get_json(file)
        total_dict.append(dict_)
    # Merge all dictionaries into one
    final_dict = main_cls.merge_dicts(total_dict)
    
    
    # Save dictionary as JSON file
    with open('result.json', 'w') as json_file:
        json.dump(final_dict, json_file, indent=4)