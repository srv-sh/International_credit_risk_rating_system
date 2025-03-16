import io
import random
import string
from PIL import Image
import sys
sys.path.append("/workspace/CreditScoring-refined-/src")  # Add the package directory to sys.path
import config as cfg

class imageToPdf():
    def __init__(self):
        self.pdf_path = cfg.pdf_path
    
    def save_pdf(self,image):
        # Generate a random filename
        random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".pdf"

        # Save the image as a PDF
        self.output_dir = self.pdf_path+ "/" + random_name
        image.save( self.output_dir, "PDF")
        return self.output_dir



if __name__ == "__main__":
    img2pdf = imageToPdf()
    image = Image.open("/workspace/CreditScoring-refined-/data/aci/aci2_png.rf.221592b8cf4bc472c5b4fe639622b7b6.jpg").convert("RGB")
    dir_path = img2pdf.save_pdf(image=image)
    print(dir_path)