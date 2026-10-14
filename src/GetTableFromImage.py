import numpy as np

class getTableOnly():
    def __init__(self):
        pass

    def detect(self, image,base_64 = True ,  save=False):
        # No-crop mode: pass the original image through to OCR.
        if base_64:
            return np.array(image)
        return image

if __name__ == "__main__":
    get_table_cls = getTableOnly()
    cropped_image = get_table_cls.detect('/home/sourav/workspace/table_recognisation_model/data/idlc/ashraf_june233.png')
    print(cropped_image)

