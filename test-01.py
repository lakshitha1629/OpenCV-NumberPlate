import cv2
import easyocr
import datetime
import serial

def load_image(file_path):
    img = cv2.imread(file_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def recognize_plate(img):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img)
    return result

def save_results_to_file_and_send_to_arduino(results, file_path, serial_port):
    with open(file_path, 'w') as file:
        for bbox, text, prob in results:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = f"{timestamp}: {text}"
            file.write(data + "\n")
            
            try:
                serial_port.write(data_with_timestamp.encode())
            except serial.SerialException as e:
                print("Error sending data:", e)

# Load image and recognize plate
image_path = 'download.jpeg'  # Replace with your image path
img = load_image(image_path)
results = recognize_plate(img)

# Print the detected text with timestamp
for bbox, text, prob in results:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_with_timestamp = f"{timestamp}: {text} (confidence: {prob:.2f})"
    print("Detected text to send to Arduino:", data_with_timestamp)

# Try to initialize serial port for Arduino
try:
    arduino_port = 'COM3'  # Replace with your actual port
    baud_rate = 9600
    arduino_serial = serial.Serial(arduino_port, baud_rate, timeout=1)

    # Save results and send to Arduino
    output_file_path = 'detected_text.txt'
    save_results_to_file_and_send_to_arduino(results, output_file_path, arduino_serial)

    # Close the serial port
    arduino_serial.close()
except serial.SerialException as e:
    print("Could not open port:", e)
