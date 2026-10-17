import numpy as np

def iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1_, y1_, x2_, y2_ = box2

    # Compute intersection
    inter_x1 = max(x1, x1_)
    inter_y1 = max(y1, y1_)
    inter_x2 = min(x2, x2_)
    inter_y2 = min(y2, y2_)

    if inter_x2 < inter_x1 or inter_y2 < inter_y1:
        return 0.0

    inter_area = (inter_x2 - inter_x1 + 1) * (inter_y2 - inter_y1 + 1)

    # Compute union
    box1_area = (x2 - x1 + 1) * (y2 - y1 + 1)
    box2_area = (x2_ - x1_ + 1) * (y2_ - y1_ + 1)
    union_area = box1_area + box2_area - inter_area

    # Compute IoU
    iou = inter_area / union_area
    return iou

def non_max_suppression(boxes, scores, iou_threshold=1):
    indices = np.argsort(scores)[::-1]
    keep = []

    while len(indices) > 0:
        current = indices[0]
        keep.append(current)
        if len(indices) == 1:
            break

        remaining_indices = indices[1:]
        remaining_boxes = [boxes[i] for i in remaining_indices]  # Corrected line
        current_box = boxes[current]

        ious = np.array([iou(current_box, box) for box in remaining_boxes])

        # Debugging: print IoU values
        # print(f"Current Box: {current_box}, Remaining Boxes: {remaining_boxes}")
        # print(f"IoUs: {ious}")

        # Select boxes with IoU less than the threshold
        remaining_indices = remaining_indices[ious < iou_threshold]
        indices = remaining_indices  # Update indices with those that survived NMS

    return keep
