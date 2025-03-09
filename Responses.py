from src.DetectTable import TableDetection
from src.utils.NonMaximumSuppression import non_max_suppression
from  src.RecogniseStucture import TableStuctureRecognisation
from  src.RecogniseStuctureYOLO import TableStuctureRecognisation as yolo
from src import config as cfg
from PIL import Image , ImageDraw
import torch
from torchvision.ops import nms
from src.utils.OcrFromImage import OcrFromTableImage
from src.utils.GetCoordinateByRow import GetCoordinateByRow
from src.utils.GetData import GetDataFromCroppedImage
from src.utils.processing import postprocessing
import pandas as pd
import io
import json
import re 
from datetime import datetime
from dateutil import parser

class main():

    def __init__(self):
        self.desired_format = "%d %B %Y"
        self.get_coordinate_cls = GetCoordinateByRow()
        self.ocr_model = OcrFromTableImage()
        self.table_detection = TableDetection()
        self.stucture_recognisation = TableStuctureRecognisation()
        self.stucture_recognisation_yolo = yolo()
        self.get_data = GetDataFromCroppedImage()
        self.post_processing = postprocessing()

    # Function to convert dates
    def convert_to_datetime(self,date_str):
        try:
            # Parse the date string into a datetime object
            return parser.parse(date_str)
        except ValueError:
            return None
    
    def extract_dates_from_header(self, cropped_img):
        column_header = self.ocr_model.recognize(cropped_img, type=None)
        print(column_header)

        column_header =  self.post_processing.extract_dates(column_header)
        column_header=  [self.convert_to_datetime(date) for date in column_header]
        column_header = [dt for dt in column_header if dt is not None]
        column_header = sorted(column_header, reverse=True)
        column_header = [dt.strftime(self.desired_format) for dt in column_header]
        return column_header
    

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
    
    def recognise_stucture_yolo(self, cropped_table):
        results , img_width = self.stucture_recognisation_yolo.recognise(cropped_table)
        cells = self.stucture_recognisation_yolo.outputs_to_objects(results=results, img_width=img_width)
        return cells
    


    def merge_dicts(self,data_list):
        # Create an empty dictionary to hold the merged data
        merged_data = {}

        # Iterate over each dictionary in the input list
        for data in data_list:
            # Iterate over each key in the current dictionary
            for key, value in data.items():
                if key not in merged_data:
                    # If the key is not already in merged_data, initialize it with an empty list
                    merged_data[key] = []
                
                # Extend the list for this key with the values from the current dictionary
                merged_data[key].extend(value)
        
        return merged_data

    def get_json(self,image_content, csv = False):
        image = Image.open(io.BytesIO(image_content)).convert("RGB")
         # image = Image.open(image_content).convert("RGB")

        # image = Image.open(image_content).convert("RGB")

        cells = self.recognise_stucture(image) # recognise table stucture 
        table_cell = [cell for cell in cells if cell['label'] == "table"]       
        table_bbox = table_cell[0]['bbox']
        cropped_table =  image.crop(table_bbox)
        
        cells = self.recognise_stucture_yolo(cropped_table=cropped_table) # recognise table stucture 

        # column header 
        columns_data = [cell for cell in cells if cell['label']=='header']
        # print(columns_data)
        column_header_bbox = columns_data[0]['bbox']
        column_header_cropped_img = cropped_table.crop(column_header_bbox)
        column_header_cropped_img.save("image/header.png")
        
        column_header = self.extract_dates_from_header(cropped_img=column_header_cropped_img)
        if len(column_header)>2:
            column_header= column_header[:2]
            # column_header = column_header[:2]

        print("DATES->", column_header)
        # input("!!!!")

        cell_coordinates =  self.get_coordinate_cls.get_cordinate(cells)
        self.get_data.draw_bounding_boxes(cropped_table , cell_coordinates)
    
        rows =  self.get_data.get_df_from_table_image(cropped_table , cell_coordinates,save=True) # after run this line it will save csv file to the directory

        # store in  the dataframe
        data = pd.DataFrame(rows)
        shape =data.shape
        # print(data)
        print("----------")
        columns_name = self.post_processing.process_columns(column_header=column_header, shape=shape) 
        # print(columns_name)
        # input("!!!")
        data.columns = columns_name
        if csv: 
            data.to_csv("data.csv")

        data =data.dropna(how="all")
        col = data.columns
        
        particular = data[col[0]].tolist()
        year1 =  data[col[-2]].tolist()
        year2 =  data[col[-1]].tolist()

        return {"particulars" : particular,
         column_header[-2]: year1,
         column_header[-1]: year2
         }
    

    def get_response(self,files):
        final_dict = {}
        total_dict =[]
        print("---------------")
        for file in files:
            content =  file.read()
            dict_ =self.get_json(content)
            total_dict.append(dict_)
        final_dict = self.merge_dicts(total_dict)
        return final_dict
    

if __name__=="__main__":
    main_cls = main() # main class

    files = ['/home/aiml/CredirScoring/table_data/tables/beximco1.png', '/home/aiml/CredirScoring/table_data/tables/beximco2.png', '/home/aiml/CredirScoring/table_data/tables/beximco3.png']
    # files = ['table_data/tables/gp2.png']
    final_dict = {}
    total_dict =[]
    for file in files:
        dict_ =main_cls.get_json(file)
        total_dict.append(dict_)

    final_dict = main_cls.merge_dicts(total_dict)
    
    
    # Save dictionary as JSON file
    with open('result.json', 'w') as json_file:
        json.dump(final_dict, json_file, indent=4)