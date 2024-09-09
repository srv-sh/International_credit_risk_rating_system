from transformers import  TableTransformerForObjectDetection
from .  import config as cfg
from .utils.resize import MaxResize
from torchvision import transforms
import torch

class TableStuctureRecognisation():

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = TableTransformerForObjectDetection.from_pretrained(cfg.table_stucture_recognisation_model).to(self.device)
        self.resizer =  MaxResize(1000)
        self.detection_transform = transforms.Compose([
                                                    self.resizer,
                                                    transforms.ToTensor(),
                                                    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                                                    ])
        # update id2label to include "no object"
        self.structure_id2label = self.model.config.id2label
        self.structure_id2label[len(self.structure_id2label)] = "no object"
        
    def convertToPixelValue(self, cropped_table):
        pixel_values = self.detection_transform(cropped_table).unsqueeze(0)
        pixel_values = pixel_values.to(self.device)
        return pixel_values
        
    def recognise(self , croped_image):
        pix_values  = self.convertToPixelValue(cropped_table=croped_image)
        with torch.no_grad():
            outputs = self.model(pix_values)
            return outputs
    def rescale_bboxes(self,out_bbox, size):
        img_w, img_h = size
        b = self.box_cxcywh_to_xyxy(out_bbox)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b
    def box_cxcywh_to_xyxy(self, x):
        x_c, y_c, w, h = x.unbind(-1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h), (x_c + 0.5 * w), (y_c + 0.5 * h)]
        return torch.stack(b, dim=1)
    
    def non_max_suppression(self, boxes_tensor, scores_tensor, iou_threshold = 0.8):
        nms_indices = torch.ops.torchvision.nms(boxes_tensor, scores_tensor, iou_threshold=iou_threshold)
        nms_indices = nms_indices.tolist()
        return nms_indices
        
    def outputs_to_objects(self, outputs, img_size):
        m = outputs.logits.softmax(-1).max(-1)
        pred_labels = list(m.indices.detach().cpu().numpy())[0]
        pred_scores = list(m.values.detach().cpu().numpy())[0]
        pred_bboxes = outputs['pred_boxes'].detach().cpu()[0]
        pred_bboxes = [elem.tolist() for elem in self.rescale_bboxes(pred_bboxes, img_size)]

        objects = []

        ######## apply non-max-suppression technique for detect bounding box accuractly ########
        # nms_indices = self.non_max_suppression( boxes_tensor=torch.tensor( pred_bboxes,dtype=torch.float32), scores_tensor=torch.tensor( pred_scores,dtype=torch.float32))
        # pred_bboxes= [pred_bboxes[i] for i in nms_indices]
        # pred_labels = [pred_labels[i] for i in nms_indices]
        # pred_scores = [pred_scores[i] for i in nms_indices]
        ##########################################################################################


        for label, score, bbox in zip(pred_labels, pred_scores, pred_bboxes):
            class_label = self.structure_id2label[int(label)]
            if not class_label == 'no object':
                objects.append({'label': class_label, 'score': float(score),
                                'bbox': [float(elem) for elem in bbox]})
        # return objects

                
        boxes = [obj['bbox'] for obj in objects if obj['label'] == "table row"]
        scores = [obj['score'] for obj in objects if obj['label'] == "table row"]
        
        
        ######## apply non-max-suppression technique for detect bounding box accuractly ########
        nms_indices = self.non_max_suppression( boxes_tensor=torch.tensor( boxes,dtype=torch.float32), scores_tensor=torch.tensor( scores,dtype=torch.float32))
        scores  = [scores[i] for i in nms_indices]
        # objects = [objects[i] for i in nms_indices]
        n_objects =[]
        for obj in objects:
            if obj['label'] != "table row":
                n_objects.append(obj)
            elif obj['label'] == "table row" and obj['score'] in scores :
                n_objects.append(obj)
        ##########################################################################################

        return n_objects
        
    def get_cells(self, outputs, img_size):
        cells =self.outputs_to_objects(outputs=outputs, img_size=img_size)

        return cells
    




