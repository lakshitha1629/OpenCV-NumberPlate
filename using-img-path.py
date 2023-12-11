import cv2
from matplotlib import pyplot as plt
import easyocr

def load_image(file_path):
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def recognize_plate(img):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img)
    return result

image_path = 'download.jpeg'  
img = load_image(image_path)

results = recognize_plate(img)

# plt.imshow(img)
# plt.show()

print("Detected text:")
for (bbox, text, prob) in results:
    print(f"{text} (confidence: {prob:.2f})")
