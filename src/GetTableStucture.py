from .utils.ImageJsonUtils import imageUtils
import tensorflow as tf
import numpy as np
from . import config as cfg
from sklearn.cluster import DBSCAN

class getStucture():

    def __init__(self, ocr_information):
        self.ocr_information = ocr_information
        self.image_utils = imageUtils()
        self.im = self.image_utils.json2im(ocr_information['cropped_image'])
        self.image_height = self.im.shape[0]
        self.image_width = self.im.shape[1]

    def merge_cluster(self,cluster):
        x1 = min([line[0] for line in cluster])
        y1 = min([line[1] for line in cluster])
        x2 = max([line[2] for line in cluster])
        y2 = max([line[3] for line in cluster])
        return [x1, y1, x2, y2]

    # --- LINE EXTRACTION FUNCTIONS ---
    def cluster_lines(self,lines, axis=1, eps=10):
        centers = np.array([(line[axis] + line[axis+2]) / 2 for line in lines]).reshape(-1, 1)
        clustering = DBSCAN(eps=eps, min_samples=1).fit(centers)
        clusters = {}
        for idx, label in enumerate(clustering.labels_):
            clusters.setdefault(label, []).append(lines[idx])
        return [self.merge_cluster(c) for c in clusters.values()]
    
    def apply_nms(self,boxes, probabilities, iou_threshold):
        out = tf.image.non_max_suppression(
                            boxes,
                            probabilities,
                            max_output_size = 1000,
                            iou_threshold=iou_threshold,
                            score_threshold=0.3, # float('-inf'),
                            name=None
                        )
        return out 
    def get_nms_lines(self,boxes, scores, iou_thresh, axis='horizontal'):
        lines = []
        # image_height = cropped.shape[0]
        # image_width = cropped.shape[1]
        for box in boxes:
            x_min, y_min, x_max, y_max = box
            if axis == 'horizontal':
                lines.append([0, y_min, self.image_width, y_max])
            else:
                lines.append([x_min, 0, x_max, self.image_height])
        indices = tf.image.non_max_suppression(
            boxes=lines,
            scores=scores,
            max_output_size=1000,
            iou_threshold=iou_thresh,
            score_threshold=0.3
        ).numpy()
        return [lines[i] for i in indices]
        
    def sort_lines(self, boxes):
        lines = np.sort(np.array(boxes))
        return lines
    def filter_close_lines(self,lines, min_gap=10):
        """Remove vertical lines that are too close together (likely duplicates)."""
        filtered = [lines[0]]
        for line in lines[1:]:
            if abs(line[0] - filtered[-1][0]) > min_gap:
                filtered.append(line)
        return filtered

    
    def boxes_from_image(self,method= "cluster"):

        boxes = self.ocr_information['boxes'] 
        texts = self.ocr_information['texts']
        scores =  self.ocr_information['probabilities']

        if method == "normal":
            horiz_boxes = []
            vert_boxes = []
            for box in boxes:
                x_min, y_min, x_max, y_max = box

                # Horizontal box: same y-range, full image width
                x_h, y_h = 0, y_min
                width_h = self.image_width
                height_h = y_max - y_min

                # Vertical box: same x-range, full image height
                x_v, y_v = x_min, 0
                width_v = x_max - x_min
                height_v = self.image_height

                horiz_boxes.append([x_h, y_h, x_h + width_h, y_h + height_h])
                vert_boxes.append([x_v, y_v, x_v + width_v, y_v + height_v])

            horiz_boxes_nms = self.apply_nms(boxes = horiz_boxes , probabilities = scores, iou_threshold= cfg.horiz_iou_thresh)
            sorted_horiz_lines = self.sort_lines(horiz_boxes_nms)
            vert_boxes_nms = self.apply_nms(boxes = vert_boxes , probabilities = scores, iou_threshold= cfg.vert_iou_thresh)
            sorted_vert_lines = self.sort_lines(vert_boxes_nms)
        
            return {'horiz_boxes': horiz_boxes, 'sorted_horiz_lines':sorted_horiz_lines,'vert_boxes': vert_boxes, 'sorted_vert_lines' : sorted_vert_lines, 'boxes': boxes, 'texts': texts, "scores": scores}
        
        if method == "cluster":
            # --- GET RAW LINES FROM OCR BOXES ---
            horiz_lines_raw = self.get_nms_lines(boxes, scores, iou_thresh=cfg.horiz_iou_thresh, axis='horizontal')
            vert_lines_raw = self.get_nms_lines(boxes, scores, iou_thresh=cfg.vert_iou_thresh, axis='vertical')

            # --- CLUSTER & SORT LINES ---
            horiz_lines = self.cluster_lines(horiz_lines_raw, axis=1, eps=cfg.horiz_eps)
            vert_lines = self.cluster_lines(vert_lines_raw, axis=0, eps=cfg.vert_eps)
            
            horiz_lines = sorted(horiz_lines, key=lambda l: l[1]) # filter_close_lines(sorted(horiz_lines, key=lambda l: l[1]),min_gap=9)
            vert_lines =self.filter_close_lines(sorted(vert_lines, key=lambda l: l[1]),min_gap=cfg.vert_min_gap)  #sorted(vert_lines, key=lambda l: l[0])

            return {"vert_lines": vert_lines, "horiz_lines": horiz_lines, "boxes" : boxes , "texts": texts, "scores": scores}
