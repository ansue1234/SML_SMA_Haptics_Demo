import time
import torch
import cv2
import keyboard
from cvzone.HandTrackingModule import HandDetector
from record import AudioProcessor
import numpy as np
import pyttsx3

from ..code.client import Client

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
engine = pyttsx3.init()
client = Client(url_1='http://192.168.43.176:80/receiveData', record_file='./command_record/command_out.csv', record=True)

def get_object_stats(frame, df_result, class_name, object_center=None):
    # object_center = None
    for index, row in df_result.iterrows():
        x1, y1, x2, y2 = row['xmin'], row['ymin'], row['xmax'], row['ymax']
        object_name = row['name']
        if object_name == class_name:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            cv2.putText(frame, object_name, (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
            object_center = np.array([int((x1+x2)/2), int((y1+y2)/2)])
        else:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, object_name, (int(x1), int(y1-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
    return frame, object_center

def compute_plan(object_center, hand_center):
    if object_center is not None and hand_center is not None:
        if np.linalg.norm(object_center - hand_center) <= 20:
            return 'Matched'
        elif np.abs(object_center[0] - hand_center[0]) < 20:
            if object_center[1] > hand_center[1]:
                return 'Move Down'
            else:
                return 'Move Up'
        else:
            if object_center[0] > hand_center[0]:
                return 'Move Right'
            else:
                return 'Move Left'
    return None

def display_init():
    canvas = np.ones((200, 200, 3), dtype = "uint8") * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, 'Action:', (10,20), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, 'Listening to input ...', (10,35), font, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    icon = cv2.imread('../painting_alignment/listening.png')
    icon = cv2.resize(icon, (100, 100))
    canvas[50:150, 50:150, :] = icon
    return canvas

def display_plan(plan, object_name, hand_center, object_center):
    canvas = np.ones((200, 200, 3), dtype = "uint8") * 255
    stage = object_name
    if plan == 'Move Up':
        icon = cv2.imread('../painting_alignment/up.png')
        client.send_post('w')
    elif plan == 'Move Down':
        icon = cv2.imread('../painting_alignment/down.png')
        client.send_post('s')
    elif plan == 'Move Left':
        icon = cv2.imread('../painting_alignment/left.png')
        client.send_post('a')
    elif plan == 'Move Right':
        icon = cv2.imread('../painting_alignment/right.png')
        client.send_post('d')
    elif plan == 'Matched':
        icon = cv2.imread('../painting_alignment/smiley.png')
        client.send_post('r')
        plan = 'No Action'
    else:
        icon = np.ones((100, 100, 3), dtype = "uint8")*255
        plan = 'No Action'
        if object_center is None:
            stage = 'Finding' + ' ' + object_name + '...'
        elif hand_center is None:
            stage = 'Finding' + ' hand...'
        else:
            stage = 'N/A'

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, 'Action:', (10,20), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, plan, (10,35), font, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, 'Object Wanted: ', (10,165), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, stage, (10,180), font, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
    icon = cv2.resize(icon, (100, 100))
    canvas[50:150, 50:150, :] = icon
    return canvas

def draw_thinking():
    canvas = np.ones((480, 640, 3), dtype = "uint8") * 255
    icon = cv2.imread('thinking.png')
    # icon = cv2.resize(icon, (100, 100))
    icon_w, icon_h = icon.shape[:2]
    print(icon.shape[:2])
    buffer_w = (640 - icon_w)//2
    buffer_h = (480 - icon_h)//2
    canvas[buffer_h: buffer_h + icon_h, buffer_w:buffer_w + icon_w, :] = icon
    return canvas

def main():
    # Use the index appropriate for your external webcam (commonly 1 for the first external one)
    # cv2.namedWindow('Webcam')
    # cv2.setMouseCallback('Webcam', draw_rectangle)
    object_name = 'N/A'
    avaliable_objects = ['backpack', 'umbrella', 'handbag', 'frisbee', 'sports ball',
                         'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
                         'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 
                         'laptop', 'mouse', 'keyboard', 'cell phone', 'book', 'scissors', 
                         'teddy bear']
    
    cap = cv2.VideoCapture() 
    cap.open(1)
    if not cap.isOpened():
        print("Error: Could not open video capture device.")
        return
    # cv2.namedWindow('Webcam')
    cv2.startWindowThread() 
    canvas = display_init()
    object_center, hand_center = None, None
    found = False
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        frame = cv2.resize(frame, (640, 480))
        cv2.imshow('Canvas', canvas)
        cv2.moveWindow("Canvas", 110, 50)
        cv2.waitKey(1)
        # speech recognition to start the program
        while object_name == 'N/A':
            cv2.imshow('Webcam', draw_thinking())
            cv2.moveWindow("Webcam", 310, 50)
            cv2.waitKey(1)
            engine.say("What object do you want to find?")
            engine.runAndWait()
            print("Recording Audio...")
            audio_processor = AudioProcessor()
            audio_processor.record_voice_input()
            # engine.say("Thanks, let me try to understand what you said.")
            # engine.runAndWait()
            object_name = audio_processor.transcribe_audio()
            print(object_name)
            object_found = False
            for obj in avaliable_objects:
                if obj in object_name:
                    object_name = obj
                    object_found = True
                    break
            if not object_found:
                object_name = 'N/A'
                engine.say("Sorry, I didn't get that. Can you try again?")
                engine.runAndWait()
            else:
                engine.say("Sure, I will find " + object_name + " for you.")
                engine.runAndWait()
                print("Object Wanted: ", object_name)

        if object_name == 'N/A':    
            print("Waiting for audio command...")

        if object_name != 'N/A':
            pred_frame = frame[..., ::-1]
            hands, frame = detector.findHands(frame, draw=True, flipType=True)
            if hands:
                hand = hands[0]
                hand_center = np.array([hand['center'][0], hand['center'][1]])

            results = model(pred_frame)
            df_result = results.pandas().xyxy[0]
            frame, detected_object_center = get_object_stats(frame, df_result, object_name, object_center)
            if detected_object_center is not None:
                object_center = detected_object_center
            plan = compute_plan(object_center, hand_center)
            canvas = display_plan(plan, object_name, hand_center, object_center)

            if plan == 'Matched':
                # cv2.waitKey(100)
                found = True
            
            if object_center is not None:
                cv2.circle(frame, (int(object_center[0]), int(object_center[1])), 5, (255, 0, 0), -1)
            if hand_center is not None:
                cv2.circle(frame, (int(hand_center[0]), int(hand_center[1])), 5, (255, 0, 0), -1)
                # cv2.imshow('Canvas', canvas)
                # cv2.imshow('Webcam', frame)
                # cv2.waitKey(1)
        cv2.imshow('Canvas', canvas)
        cv2.imshow('Webcam', frame)
        cv2.waitKey(1)
        # object_name = 'N/A'
        if found:
            engine.say("I found " + object_name + " for you.")
            engine.runAndWait()
            found = False
            plan = None
            object_name = 'N/A'
            object_center, hand_center = None, None
            time.sleep(5)
            continue
        if keyboard.is_pressed('q'):
            break
    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
