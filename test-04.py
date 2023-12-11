import cv2
import easyocr
import datetime
import serial
import time

def capture_image_from_camera(camera_port):
    cap = cv2.VideoCapture(camera_port)
    ret, img = cap.read()
    cap.release()
    if ret:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    else:
        return None

def recognize_plate(img):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(img)
    return result

def clean_number_plate(number_plate):
    return ''.join(char for char in number_plate if char.isalnum())

def format_and_send_data(text, serial_port, event_type, file_path):
    timestamp = datetime.datetime.now().strftime("%H|%M")
    formatted_data = f"{event_type}|{timestamp}|{text}\n"
    print(formatted_data)

    try:
        serial_port.write(formatted_data.encode())
        print("Sent to Arduino:", formatted_data)
    except serial.SerialException as e:
        print("Error sending data:", e)

    try:
        with open(file_path, 'a') as file:
            file.write(formatted_data)
        print("Saved to file:", formatted_data)
    except IOError as e:
        print("Error writing to file:", e)

    return formatted_data

# Initialize serial port for Arduino
try:
    arduino_port = 'COM3'  # Replace with your actual port
    baud_rate = 9600
    arduino_serial = serial.Serial(arduino_port, baud_rate, timeout=1)
except serial.SerialException as e:
    print("Could not open port:", e)
    exit(1)

# Initialize the file path for output and camera port
output_file_path = 'detected_text.txt'
camera_port = 0  # Replace with your camera port

# Main loop
last_detected_plate = None
last_detection_time = None

while True:
    img = capture_image_from_camera(camera_port)
    if img is not None:
        results = recognize_plate(img)

        if results:
            bbox, text, prob = results[0]
            cleaned_text = clean_number_plate(text)

            if cleaned_text != last_detected_plate:
                print(f"Detected Number Plate: {cleaned_text}")
                last_detected_plate = cleaned_text
                last_detection_time = datetime.datetime.now()

                # Format and send data for IN event and save to file
                in_data = format_and_send_data(cleaned_text, arduino_serial, "IN", output_file_path)

            elif (datetime.datetime.now() - last_detection_time).total_seconds() > 300:  # 5 minutes
                # Format and send data for OUT event and save to file
                out_data = format_and_send_data(cleaned_text, arduino_serial, "OUT", output_file_path)
                last_detected_plate = None  # Reset for new vehicle detection

    time.sleep(1) 

arduino_serial.close()
