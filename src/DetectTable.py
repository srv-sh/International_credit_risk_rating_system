from transformers import AutoModelForObjectDetection
import torch
from torchvision import transforms 
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Patch
from . import config as cfg

from .utils.resize import MaxResize

class TableDetection():
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForObjectDetection.from_pretrained(cfg.table_detection_model, revision="no_timm").to(self.device)
        self.resizer = MaxResize(800)
        self.detection_transform = transforms.Compose([
                                                    self.resizer,
                                                    transforms.ToTensor(),
                                                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                                                    ])
        self.id2label = self.model.config.id2label
        self.id2label[len(self.model.config.id2label)] = "no object"


    def convertToPixelValue(self, image):
        pixel_values = self.detection_transform(image).unsqueeze(0)
        pixel_values = pixel_values.to(self.device)
        return pixel_values

    def detect(self , image):
        pix_values  = self.convertToPixelValue(image=image)
        with torch.no_grad():
            outputs = self.model(pix_values)
            return outputs
        
    def box_cxcywh_to_xyxy(self, x):
        x_c, y_c, w, h = x.unbind(-1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
        return torch.stack(b, dim=1)
    
    def rescale_bboxes(self,out_bbox, size):
        img_w, img_h = size
        b = self.box_cxcywh_to_xyxy(out_bbox)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b
    
    def outputs_to_objects(self, outputs, img_size):
        m = outputs.logits.softmax(-1).max(-1)
        pred_labels = list(m.indices.detach().cpu().numpy())[0]
        pred_scores = list(m.values.detach().cpu().numpy())[0]
        pred_bboxes = outputs['pred_boxes'].detach().cpu()[0]
        pred_bboxes = [elem.tolist() for elem in self.rescale_bboxes(pred_bboxes, img_size)]

        objects = []
        for label, score, bbox in zip(pred_labels, pred_scores, pred_bboxes):
            class_label = self.id2label[int(label)]
            if not class_label == 'no object':
                objects.append({'label': class_label, 'score': float(score),
                                'bbox': [float(elem) for elem in bbox]})

        return objects
    
    def fig2img(self, fig):

        """Convert a Matplotlib figure to a PIL Image and return it"""
        import io
        buf = io.BytesIO()
        fig.savefig(buf)
        buf.seek(0)
        img = Image.open(buf)
        return img 
    
    def visualize_detected_tables( self, img, det_tables, out_path=None):
        # plt.imshow(img, interpolation="lanczos")
        plt.imshow(img)
        fig = plt.gcf()
        fig.set_size_inches(20, 20)
        ax = plt.gca()

        for det_table in det_tables:
            bbox = det_table['bbox']

            if det_table['label'] == 'table':
                facecolor = (1, 0, 0.45)
                edgecolor = (1, 0, 0.45)
                alpha = 0.3
                linewidth = 2
                hatch='//////'
            elif det_table['label'] == 'table rotated':
                facecolor = (0.95, 0.6, 0.1)
                edgecolor = (0.95, 0.6, 0.1)
                alpha = 0.3
                linewidth = 2
                hatch='//////'
            else:
                continue

            rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=linewidth,
                                        edgecolor='none',facecolor=facecolor, alpha=0.1)
            ax.add_patch(rect)
            rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=linewidth,
                                        edgecolor=edgecolor,facecolor='none',linestyle='-', alpha=alpha)
            ax.add_patch(rect)
            rect = patches.Rectangle(bbox[:2], bbox[2]-bbox[0], bbox[3]-bbox[1], linewidth=0,
                                        edgecolor=edgecolor,facecolor='none',linestyle='-', hatch=hatch, alpha=0.2)
            ax.add_patch(rect)

        plt.xticks([], [])
        plt.yticks([], [])

        legend_elements = [Patch(facecolor=(1, 0, 0.45), edgecolor=(1, 0, 0.45),
                                    label='Table', hatch='//////', alpha=0.3),
                            Patch(facecolor=(0.95, 0.6, 0.1), edgecolor=(0.95, 0.6, 0.1),
                                    label='Table (rotated)', hatch='//////', alpha=0.3)]
        plt.legend(handles=legend_elements, bbox_to_anchor=(0.5, -0.02), loc='upper center', borderaxespad=0,
                        fontsize=10, ncol=2)
        plt.gcf().set_size_inches(10, 10)
        plt.axis('off')

        if out_path is not None:
            plt.savefig(out_path, bbox_inches='tight', dpi=150)

        return fig
    
    def objects_to_crops(self,img, tokens, objects, class_thresholds, padding=10):
        """
        Process the bounding boxes produced by the table detection model into
        cropped table images and cropped tokens.
        """

        table_crops = []
        for obj in objects:
            if obj['score'] < class_thresholds[obj['label']]:
                continue

            cropped_table = {}

            bbox = obj['bbox']
            bbox = [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding]

            cropped_img = img.crop(bbox)

            table_tokens = [token for token in tokens if iob(token['bbox'], bbox) >= 0.5]
            for token in table_tokens:
                token['bbox'] = [token['bbox'][0]-bbox[0],
                                token['bbox'][1]-bbox[1],
                                token['bbox'][2]-bbox[0],
                                token['bbox'][3]-bbox[1]]

            # If table is predicted to be rotated, rotate cropped image and tokens/words:
            if obj['label'] == 'table rotated':
                cropped_img = cropped_img.rotate(270, expand=True)
                for token in table_tokens:
                    bbox = token['bbox']
                    bbox = [cropped_img.size[0]-bbox[3]-1,
                            bbox[0],
                            cropped_img.size[0]-bbox[1]-1,
                            bbox[2]]
                    token['bbox'] = bbox

            cropped_table['image'] = cropped_img
            cropped_table['tokens'] = table_tokens

            table_crops.append(cropped_table)

        return table_crops
        
    
    def write_img(self, image):
        image.save("/home/aiml/CredirScoring/image/temp.jpg")



if __name__=="__main__":
    table_detection = TableDetection()
    image = Image.open("/home/aiml/CredirScoring/envoyTex_sheets/balance_sheet.png").convert("RGB")
    w , h = image.size
    # print(w, h)
    outputs =  table_detection.detect(image=image)
    objects = table_detection.outputs_to_objects(outputs, image.size)
    fig = table_detection.visualize_detected_tables(image, objects, out_path="../image/table.jpg")
    visualized_image = table_detection.fig2img(fig=fig)

    tokens = []
    detection_class_thresholds = {
        "table": 0.5,
        "table rotated" : 0.5,
        "no object" : 10
    }

    crop_padding = 10

    tables_crops = table_detection.objects_to_crops(image, tokens, objects, detection_class_thresholds, padding= 12 )

    print(tables_crops)
    cropped_table = tables_crops[0]['image'].convert("RGB")

    cropped_table.save("../image/cropped_table.jpg")
    print(objects)








