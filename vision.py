import cv2
import numpy as np
import tflite_runtime.interpreter as tflite
from config import MODEL_PATH

LABELS = ["bird","armyworm","beetle","weevil","grasshopper"]

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

inp = interpreter.get_input_details()[0]["index"]
out = interpreter.get_output_details()[0]["index"]

def classify(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img,(224,224))
    img = img.astype(np.float32)/255.0
    img = np.expand_dims(img,0)

    interpreter.set_tensor(inp,img)
    interpreter.invoke()

    preds = interpreter.get_tensor(out)[0]
    i = int(np.argmax(preds))

    return LABELS[i], float(preds[i])