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

# Initialize the file path for output and camera ports
output_file_path = 'detected_text.txt'
in_camera_port = 0  # Replace with your IN camera port
out_camera_port = 1  # Replace with your OUT camera port

# Main loop
last_detected_plate_in = None
last_detected_plate_out = None
last_detection_time_in = None
last_detection_time_out = None

while True:
    # Process IN camera
    img_in = capture_image_from_camera(in_camera_port)
    if img_in is not None:
        results_in = recognize_plate(img_in)

        if results_in:
            bbox_in, text_in, prob_in = results_in[0]
            cleaned_text_in = clean_number_plate(text_in)

            if cleaned_text_in != last_detected_plate_in:
                print(f"Detected IN Number Plate: {cleaned_text_in}")
                last_detected_plate_in = cleaned_text_in
                last_detection_time_in = datetime.datetime.now()

                # Format and send data for IN event and save to file
                in_data = format_and_send_data(cleaned_text_in, arduino_serial, "IN", output_file_path)

    # Process OUT camera
    img_out = capture_image_from_camera(out_camera_port)
    if img_out is not None:
        results_out = recognize_plate(img_out)

        if results_out:
            bbox_out, text_out, prob_out = results_out[0]
            cleaned_text_out = clean_number_plate(text_out)

            if cleaned_text_out != last_detected_plate_out:
                print(f"Detected OUT Number Plate: {cleaned_text_out}")
                last_detected_plate_out = cleaned_text_out
                last_detection_time_out = datetime.datetime.now()

                # Format and send data for OUT event and save to file
                out_data = format_and_send_data(cleaned_text_out, arduino_serial, "OUT", output_file_path)

    time.sleep(1) 

arduino_serial.close()
