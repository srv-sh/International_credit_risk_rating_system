tokens = []
detection_class_thresholds = {
    "table": 0.5,
    "table rotated" : 0.5,
    "no object" : 10
}
crop_padding = 12

table_detection_model = 'microsoft/table-transformer-detection'
table_stucture_recognisation_model =  "microsoft/table-structure-recognition-v1.1-all"


