import torch
import base64
import urllib.request

from io import BytesIO
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

import pandas as pd
import json
from io import StringIO
import re

from olmocr.data.renderpdf import render_pdf_to_base64png
from olmocr.prompts import build_finetuning_prompt
from olmocr.prompts.anchor import get_anchor_text
import sys
sys.path.append("/workspace/CreditScoring-refined-/src")
import config as cfg
from utils.SaveAsPDF import imageToPdf


class getTableFromImage():
    def __init__(self):
        self.model_path =  cfg.model_path
        self.processor_path = cfg.processor_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(self.model_path,torch_dtype = torch.bfloat16).to(self.device).eval()
        self.processor = AutoProcessor.from_pretrained(self.processor_path, use_fast=True)
        self.img2pdf = imageToPdf()
        self.url = ""
    
    def extract_year(self,date_string):
        # Use regular expression to find a 4-digit number (which would represent the year)
        match = re.search(r'\b\d{4}\b', date_string)
        if match:
            return match.group(0)  # Return the found year
        
        return None  # If no year is found
    
    def clean_number(self,number_string):
        # Remove commas and extra spaces from the number
        cleaned_number = number_string.replace(',', '').strip()
        cleaned_number = cleaned_number.strip('**')  # Remove parentheses
        if cleaned_number.startswith('(') and cleaned_number.endswith(')'):
            cleaned_number = '-' + cleaned_number.strip('()')
        return cleaned_number
    
    def clean_text(self,text_string):
        cleaned_text = text_string.strip()
        cleaned_text = cleaned_text.strip('**')
        return cleaned_text
    
    def cre_between_num(self,number_string):
            if re.search(r'[^0-9,.()\s]', number_string):  # If any invalid character is found
                print("Character detected",number_string)
                return True  # Return None or an error message
            else:
                return False

    

    def get_text_to_df(self,text_output):
        json_string = text_output[0]
        data = json.loads(json_string)
        text = data['natural_text']
        table_match = re.search(r"(\|.*?\|\n)(?:\|.*?\|\n)*", text, re.DOTALL)
        if table_match:
            markdown_table = table_match.group(0)
            # Remove separator row (which contains only dashes)
            markdown_table = "\n".join([line for line in markdown_table.split("\n") if not re.match(r"^\|\s*-+\s*\|", line)])

            # Read the Markdown table into a Pandas DataFrame
            df = pd.read_csv(StringIO(markdown_table), sep="|", engine="python", skipinitialspace=True)

            # Clean column names
            df.columns = [col.strip() for col in df.columns]
            
            # Drop empty first and last column caused by leading/trailing "|"
            df = df.iloc[:, 1:-1]

            # Strip spaces from all values
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

            # Display DataFrame
            return df
        else:
            print("No Markdown table found in the text.")


    def get_image_data_base64(self,image):
        self.pdf_path = self.img2pdf.save_pdf(image)
        self.url = self.pdf_path
        image_base64 = render_pdf_to_base64png(self.pdf_path, 1, target_longest_image_dim=1024)
        return image_base64

    def get_prompt(self):
        anchor_text = get_anchor_text(self.pdf_path, 1, pdf_engine="pdfreport", target_length=4000)
        prompt = build_finetuning_prompt(anchor_text)
        return prompt
    
    def get_list_from_data(self,text):
        lines = text.split("\n")
        particulars = []
        year1 =[]
        year2 =[]
        for line in lines:
            # print(line.count('|'))
            if line.count('|') == 4:
                sub_lines = line.split('|')
                sub_lines= sub_lines[1:-1]
                part = self.clean_text(sub_lines[0])
                yr1 = self.clean_number(sub_lines[1])
                yr2 = self.clean_number(sub_lines[2])
                if part.count('-') > 5 :#or self.cre_between_num(yr1) or self.cre_between_num(yr2):
                    pass
                else:
                    particulars.append(part)
                    year1.append(yr1)
                    year2.append(yr2)
            elif line.count('|') == 5:
                sub_lines = line.split('|')
                sub_lines= sub_lines[1:-1]
                part = self.clean_text(sub_lines[0])
                yr1 = self.clean_number(sub_lines[2])
                yr2 = self.clean_number(sub_lines[3])
                if part.count('-') > 5 : #or self.cre_between_num(yr1) or self.cre_between_num(yr2):
                    pass
                else:
                    particulars.append(part)
                    year1.append(yr1)
                    year2.append(yr2)
        return particulars , year1 , year2
                


    def get_table_data(self,image):
        image_base_64 =  self.get_image_data_base64(image)
        prompt = self.get_prompt()
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base_64}"}},
                ],
            }
        ]
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

        main_image = Image.open(BytesIO(base64.b64decode(image_base_64)))
        inputs = self.processor(
                            text=[text],
                            images=[main_image],
                            padding=True,
                            return_tensors="pt",
                        )
        inputs = {key: value.to(self.device) for (key, value) in inputs.items()}

        # Generate the output
        output = self.model.generate(
                    **inputs,
                    temperature=0.8,
                    max_new_tokens=3000,
                    num_return_sequences=1,
                    do_sample=True,
                )
        # Decode the output
        prompt_length = inputs["input_ids"].shape[1]
        new_tokens = output[:, prompt_length:]
        text_output = self.processor.tokenizer.batch_decode(new_tokens, skip_special_tokens=True)
        
        json_string = text_output[0]
        data = json.loads(json_string)
        text = data['natural_text']
        particulars , year1, year2 = self.get_list_from_data(text)
        print(particulars[0],year1[0],year2[0])
        column1 , column2 =  year1[0] , year2[0] # self.extract_year(year1[0]) , self.extract_year(year2[0]) 
        
        columns =[column1, column2]
        # print(columns)
        return particulars[1:] , year1[1:] , year2[1:] , columns , self.url, prompt, data
        # print(text_output)
        # df = self.get_text_to_df(text_output)
        # return df
    


if __name__ == "__main__":
    cls = getTableFromImage()
    image = Image.open("/workspace/CreditScoring-refined-/data/gp/gp2.png").convert("RGB")
    data = cls.get_table_data(image)
    data.to_csv("data.csv",index =False)
    