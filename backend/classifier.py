import numpy as np
import cv2

# Placeholder: replace with real TFLite model
def detect_pest(frame):
    # Currently randomly returns None or a pest type
    import random
    pests = ["bird", "army worm", "beetle", "weevil", "grasshopper"]
    return random.choice(pests + [None, None])