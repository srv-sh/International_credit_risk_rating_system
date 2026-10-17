from paddleocr import PaddleOCR
import json
import base64
import numpy as np 
import pickle
from .utils.ImageJsonUtils import imageUtils


class getOCR():
    def __init__(self):
        self.ocr_model = PaddleOCR(
                        use_doc_orientation_classify=False, # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
                        use_doc_unwarping=False, # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
                        use_textline_orientation=False, # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
                    )
    
        self.image_utils  = imageUtils()
    
        
    def predict(self, cropped_image):
        result = self.ocr_model.predict(cropped_image)
        texts = result[0]['rec_texts']
        probabilities = result[0]['rec_scores']
        boxes = result[0]['rec_boxes']
        cropped_image_json = self.image_utils.im2json(cropped_image)
        dist_response  ={'cropped_image' : cropped_image_json, 'texts': texts, 'probabilities': probabilities , 'boxes': boxes }
        return dist_response


