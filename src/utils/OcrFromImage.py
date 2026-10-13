import numpy as np
import requests
from PIL import Image
from io import BytesIO
from tqdm.auto import tqdm
import pandas as pd 
import src.config as cfg
from src.utils.ValidateString import ValidateString
import re


class OcrFromTableImage():
    def __init__(self):
        self.validation_model = ValidateString()

    def ocr(self, cropped_image, cell):
        cell_image = np.array(cropped_image.crop(cell["cell"]))
        result =  self.recognize(np.array(cell_image))
        # validation = self.validation_model.validate(result.strip().lower())
        return result
    
    def extract_and_check_format_notes(self, s):

        # Find patterns that match floating numbers with one or two decimal places
        match = re.search(r'\d{1,2}\.\d{1,2}', s)
        if match:
            # Extract the floating number
            number = match.group()
            return True, float(number)
        return False, None
    

    def filter_number(self, input_string):
        # Remove commas, spaces, and dots
        cleaned_string = re.sub(r'[,\.\s]', '', input_string)
        # Extract numbers from the cleaned string
        numbers = re.findall(r'\d+', cleaned_string)
        # Join all the numbers to return a single string of numbers
        result = ''.join(numbers)
        # check is it number or not
        if result.isdigit():
            return True, result
        else:
            return False, None 



        
    def recognize(self,cell_image,type="buffered"):

        if type=="buffered":
            
            image = Image.fromarray(cell_image)
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            buffered.seek(0)

        elif type=="pil":
            buffered = BytesIO()
            cell_image.save(buffered, format="JPEG")
            buffered.seek(0)

        # Send the image to the OCR API
        url = "http://192.168.10.38:4000/ocr/"  # Use the correct port number
        files = {'file': ("image.jpg", buffered, "image/jpeg")}
        try:
            response = requests.post(url, files=files)
        except requests.RequestException as e:
            return f"Error sending to OCR API {e}"

        # Check if the request was successful
        if response.status_code == 200:
            ocr_result = response.json().get('text')
            return ocr_result
        else:
            return f"Error: {response.status_code} - {response.text}"

    def get_df_from_table_image(self , cropped_image ,  coordinates):

        df =[]
        received =[]


        for idx , row in enumerate(tqdm(coordinates)):

            row_text = []
        
            if len(row['cells']) == 4:
                # condition to check each row contain 4 values like particular , notes, date1 , date2  
                index = self.ocr(cropped_image=cropped_image,cell=row['cells'][0]) # OCR from cropped image
            
                validation_index = self.validation_model.validate(index.strip().lower()).lower()  # check index name is valid or not 
            
                if validation_index == "yes" and index not in received:
                    
                    received.append(index)
                    print(index.strip().lower())
                    ############## index #############
                    row_text.append(index.strip().lower())
                    # cropped_image.crop(row['cells'][1]["cell"]).save("cropped_image/{}_1.png".format(idx))
                    ###########   notes  ############
                    notes = self.ocr(cropped_image=cropped_image,cell=row['cells'][1])
                    res_note, number_note = self.extract_and_check_format_notes(notes)

                    if res_note == True:
                        print(number_note)
                        row_text.append(number_note)
                        
                    else:
                        row_text.append("")
                    
                    ################# year 1 ################
                    yr1 = self.ocr(cropped_image=cropped_image,cell=row['cells'][2])
                    # cropped_image.crop(row['cells'][2]["cell"]).save("cropped_image/{}_2.png".format(idx))
                    res_yr1 , number_yr1 = self.filter_number(yr1)

                    if res_yr1 == True:
                        # row_text.append(number_yr1)
                        row_text.append(number_yr1)
                        print(number_yr1)
                        
                    else:
                        row_text.append("")
                    
                    ############ year 2 ###########
                    
                    yr2 = self.ocr(cropped_image=cropped_image,cell=row['cells'][3])
            
                    # cropped_image.crop(row['cells'][3]["cell"]).save("cropped_image/{}_3.png".format(idx))
                    res_yr2 , number_yr2 =self.filter_number(yr2)

                    if res_yr2 == True:
                        # row_text.append(yr2)
                        row_text.append(number_yr2)
                        print(number_yr2)
                        
                    else:
                        row_text.append("")

                else:
                    print(f"{index} ------ is not valid index")

            elif len(row['cells']) < 4:
                index = self.ocr(cropped_image=cropped_image,cell=row['cells'][0]) # OCR from cropped image

                validation_index = self.validation_model.validate(index.strip().lower()).lower()  # check index name is valid or not 

                if validation_index == "yes" and index not in received:
                    
                    received.append(index)
                    print(index.strip().lower())
                    ########### index ############
                    row_text.append(index.strip().lower())
                    ############### year 1##############
                    yr1 = self.ocr(cropped_image=cropped_image,cell=row['cells'][1])
                    # cropped_image.crop(row['cells'][1]["cell"]).save("cropped_image/{}_2.png".format(idx))
                    res_yr1 , number_yr1 = self.filter_number(yr1)

                    if res_yr1 == True:
                        # row_text.append(number_yr1)
                        row_text.append(number_yr1)
                        print(number_yr1)
                        
                    else:
                        row_text.append("")
                    
                    ################ year 2  ###############
        
                    yr2 = self.ocr(cropped_image=cropped_image,cell=row['cells'][2])
            
                    # cropped_image.crop(row['cells'][2]["cell"]).save("cropped_image/{}_3.png".format(idx))
                    res_yr2 , number_yr2 =self.filter_number(yr2)

                    if res_yr2 == True:
                        # row_text.append(yr2)
                        row_text.append(number_yr2)
                        print(number_yr2)
                        
                    else:
                        row_text.append("")

            df.append(row_text)
        return df






