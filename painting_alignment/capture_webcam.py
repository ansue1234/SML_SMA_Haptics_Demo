import cv2
import keyboard

def main():
    # Use the index appropriate for your external webcam (commonly 1 for the first external one)
    cap = cv2.VideoCapture() 
    cap.open(1)

    if not cap.isOpened():
        print("Error: Could not open video capture device.")
        return
    cv2.namedWindow('Webcam')

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        
        frame = cv2.resize(frame, (640, 480))
        
        if keyboard.is_pressed('q'):
            break
        if keyboard.is_pressed('s'):
            cv2.imwrite('pic2.png', frame)
        cv2.imshow('Webcam', frame)
        cv2.waitKey(1)
    
    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
