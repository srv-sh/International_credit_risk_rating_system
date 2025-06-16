import os
import cv2
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from paddleocr import PaddleOCR
from ultralytics import YOLO
from sklearn.cluster import DBSCAN
import pandas as pd

# --- LOAD MODEL ---
image_path  = '/home/sourav/workspace/CreditScoring-refined-/data/idlc/Screenshot from 2025-04-06 11-06-04.png'  # Update path if needed
checkpoint_path = '/home/sourav/workspace/CreditScoring-refined-/data/best.pt'  # Update image path

model = YOLO(checkpoint_path)

# --- INPUT IMAGE ---
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# --- RUN DETECTION ---
results = model(image_path)[0]

# --- READ ORIGINAL IMAGE ---
image = cv2.imread(image_path)

def intersection(box_1, box_2):
    return [box_2[0], box_1[1], box_2[2], box_1[3]]

def iou(box_1, box_2):
    x_1 = max(box_1[0], box_2[0])
    y_1 = max(box_1[1], box_2[1])
    x_2 = min(box_1[2], box_2[2])
    y_2 = min(box_1[3], box_2[3])

    inter = max((x_2 - x_1), 0) * max((y_2 - y_1), 0)
    if inter == 0:
        return 0

    box_1_area = abs((box_1[2] - box_1[0]) * (box_1[3] - box_1[1]))
    box_2_area = abs((box_2[2] - box_2[0]) * (box_2[3] - box_2[1]))

    return inter / float(box_1_area + box_2_area - inter)

# --- PROCESS EACH DETECTED TABLE ---
for i, box in enumerate(results.boxes):
    class_id = int(box.cls[0])
    label = model.names[class_id]

    if label.lower() == 'table':
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cropped = image[y1:y2, x1:x2]
        crop_filename = f"{output_dir}/table_{i}_conf{conf:.2f}.jpg"
        cv2.imwrite(crop_filename, cropped)
        print(f"[INFO] Saved: {crop_filename}")

        # --- OCR ---
        ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
        result = ocr.predict(crop_filename)
        texts = result[0]['rec_texts']
        scores = result[0]['rec_scores']
        boxes = result[0]['rec_boxes']


# --- LINE EXTRACTION FUNCTIONS ---
def cluster_lines(lines, axis=1, eps=10):
    centers = np.array([(line[axis] + line[axis+2]) / 2 for line in lines]).reshape(-1, 1)
    clustering = DBSCAN(eps=eps, min_samples=1).fit(centers)
    clusters = {}
    for idx, label in enumerate(clustering.labels_):
        clusters.setdefault(label, []).append(lines[idx])
    return [merge_cluster(c) for c in clusters.values()]

def merge_cluster(cluster):
    x1 = min([line[0] for line in cluster])
    y1 = min([line[1] for line in cluster])
    x2 = max([line[2] for line in cluster])
    y2 = max([line[3] for line in cluster])
    return [x1, y1, x2, y2]

def get_nms_lines(boxes, scores, iou_thresh, axis='horizontal'):
    lines = []
    image_height = cropped.shape[0]
    image_width = cropped.shape[1]
    for box in boxes:
        x_min, y_min, x_max, y_max = box
        if axis == 'horizontal':
            lines.append([0, y_min, image_width, y_max])
        else:
            lines.append([x_min, 0, x_max, image_height])
    indices = tf.image.non_max_suppression(
        boxes=lines,
        scores=scores,
        max_output_size=1000,
        iou_threshold=iou_thresh,
        score_threshold=0.3
    ).numpy()
    return [lines[i] for i in indices]

def filter_close_lines(lines, min_gap=10):
    """Remove vertical lines that are too close together (likely duplicates)."""
    filtered = [lines[0]]
    for line in lines[1:]:
        if abs(line[0] - filtered[-1][0]) > min_gap:
            filtered.append(line)
    return filtered

def allinone(info):
    boxes = info['boxes']
    scores = info['scores']

    # --- GET RAW LINES FROM OCR BOXES ---
    horiz_lines_raw = get_nms_lines(boxes, scores, iou_thresh=0.5, axis='horizontal')
    vert_lines_raw = get_nms_lines(boxes, scores, iou_thresh=0.1, axis='vertical')

    # --- CLUSTER & SORT LINES ---
    horiz_lines = cluster_lines(horiz_lines_raw, axis=1, eps=5)
    vert_lines = cluster_lines(vert_lines_raw, axis=0, eps=5)
    horiz_lines = sorted(horiz_lines, key=lambda l: l[1]) # filter_close_lines(sorted(horiz_lines, key=lambda l: l[1]),min_gap=9)
    vert_lines =filter_close_lines(sorted(vert_lines, key=lambda l: l[1]),min_gap=90)  #sorted(vert_lines, key=lambda l: l[0])

    out_array = [["" for _ in range(len(vert_lines))] for _ in range(len(horiz_lines))]

    # Sort vertical lines by their x1 coordinate
    unordered_boxes = [line[0] for line in vert_lines]
    ordered_boxes = np.argsort(unordered_boxes)


    for i in range(len(horiz_lines)):
        for j in range(len(vert_lines)):
            # get the grid cell bounding box
            resultant = intersection(horiz_lines[i], vert_lines[ordered_boxes[j]])

            for b in range(len(boxes)):
                the_box = boxes[b]
                if iou(resultant, the_box) > 0.15:
                    out_array[i][j] = texts[b]

    out_array = np.array(out_array)
    out_array_df = pd.DataFrame(out_array)
    print(out_array_df)
    out_array_markdown =  out_array_df.to_markdown(index= False)
    return out_array_markdown
    # --- DRAW FINAL GRID ---
    # grid_img = cropped.copy()
    # for hline in horiz_lines:
    #     cv2.line(grid_img, (int(hline[0]), int(hline[1])), (int(hline[2]), int(hline[3])), (0, 0, 255), 1)
    # for vline in vert_lines:
    #     cv2.line(grid_img, (int(vline[0]), int(vline[1])), (int(vline[2]), int(vline[3])), (255, 0, 0), 1)

    # # --- DISPLAY RESULT ---
    # plt.figure(figsize=(10, 8))
    # plt.imshow(cv2.cvtColor(grid_img, cv2.COLOR_BGR2RGB))
    # plt.title(f"Detected Table Structure {i}")
    # plt.axis("off")
    # plt.show()

    # print("[DONE] All tables processed.")
