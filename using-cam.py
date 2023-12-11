import cv2
import easyocr

def recognize_plate(img, reader):
    result = reader.readtext(img)
    return result

def main():
    reader = easyocr.Reader(['en'])

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = recognize_plate(rgb_frame, reader)

        for (bbox, text, prob) in results:
            top_left = tuple(bbox[0][0])
            bottom_right = tuple(bbox[1][0])
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
