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

def clean_number_plate(number_plate):
    return ''.join(char for char in number_plate if char.isalnum())

def format_and_send_data(text, serial_port, event_type, file_path):
    timestamp = datetime.datetime.now().strftime("%H|%M")
    formatted_data = f"{event_type}|{timestamp}|{text}\n"
    print(formatted_data)

    try:
        # Write to serial port
        serial_port.write(formatted_data.encode())
        print("Sent to Arduino:", formatted_data)
    except serial.SerialException as e:
        print("Error sending data:", e)

    try:
        # Write to file
        with open(file_path, 'a') as file:
            file.write(formatted_data)
        print("Saved to file:", formatted_data)
    except IOError as e:
        print("Error writing to file:", e)

    return formatted_data

# Load image and recognize plate
image_path = 'download.jpeg'  # Replace with your image path
img = load_image(image_path)
results = recognize_plate(img)

# Initialize the file path for output
output_file_path = 'detected_text.txt'

# Assuming the first result is the number plate
if results:
    bbox, text, prob = results[0]
    cleaned_text = clean_number_plate(text)
    print(f"Detected Number Plate: {cleaned_text}")

    # Initialize serial port for Arduino
    try:
        arduino_port = 'COM3'  # Replace with your actual port
        baud_rate = 9600
        arduino_serial = serial.Serial(arduino_port, baud_rate, timeout=1)

        # Format and send data for IN event and save to file
        in_data = format_and_send_data(cleaned_text, arduino_serial, "IN", output_file_path)

        # Your logic to wait for OUT event...
        # After OUT event, format and send data for OUT event and save to file
        out_data = format_and_send_data(cleaned_text, arduino_serial, "OUT", output_file_path)

        # Close the serial port
        arduino_serial.close()

    except serial.SerialException as e:
        print("Could not open port:", e)
else:
    print("No number plate detected.")
