import cv2
import keyboard
import numpy as np
from grip import GripPipeline
from scipy.spatial import ConvexHull
from client import Client

drawing = False # True if mouse is pressed
ix, iy = -1, -1 # Initial x and y location
ex, ey = -1, -1 # Ending x and y location
ip = '192.168.43.176'
camera = 1
client = Client(url_1='http://' + ip + ':80/receiveData', record=True, record_file='./command_record/commands.csv')


def draw_rectangle(event, x, y, flags, param):
    global ix, iy, drawing, ex, ey

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
        ex, ey = x, y # Update ending point to start point initially

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            ex, ey = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        ex, ey = x, y


def get_top_corners(frame):

    # General Processing get line segments
    pipeline = GripPipeline()
    pipeline.process(frame)
    filtered_lines = pipeline.filter_lines_output
    # cv2.imshow('canny', pipeline.cv_canny_output)
    pts = []
    for line in filtered_lines:
        x1, y1, x2, y2 = int(line.x1), int(line.y1), int(line.x2), int(line.y2)
        pts += [[x1, y1]]
        pts += [[x2, y2]]
        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    if len(pts) > 2:
        pts = np.array(pts, np.int32)
        pts_center = np.mean(pts, axis=0)
        pts_std = np.std(pts, axis=0)

        # Process the points
        # remove outliers
        pts = pts[pts[:, 0] > pts_center[0] - 2 * pts_std[0]]
        pts = pts[pts[:, 0] < pts_center[0] + 2 * pts_std[0]]
        pts = pts[pts[:, 1] > pts_center[1] - 2 * pts_std[1]]
        pts = pts[pts[:, 1] < pts_center[1] + 2 * pts_std[1]]

        # Create Convex hull and find top left and bottom right of convex hull
        hull = ConvexHull(pts)
        bounding_hull = pts[hull.vertices]
        upper_left = sorted(bounding_hull.copy(), key=lambda x: x[0] + x[1])[0]
        bot_right = sorted(bounding_hull.copy(), key=lambda x: x[0] + x[1])[-1]

        # get diagonal of top left and bottom right
        slope = (bot_right[1] - upper_left[1]) / (bot_right[0] - upper_left[0])
        intercept = upper_left[1] - slope * upper_left[0]
        line_func = lambda x: slope * x + intercept

        # get verticies of upper right half og convex hull
        upper_right_hull = bounding_hull[bounding_hull[:, 1] < line_func(bounding_hull[:, 0])]
        def perp_dist_to_line(pt):
            x, y = pt
            return abs(-slope * x + y - intercept) / np.sqrt(slope ** 2 + 1)

        # get the upper right corner
        upper_right = sorted(upper_right_hull, key=perp_dist_to_line)[-1] if upper_right_hull.size > 0 else None
        
        return upper_left, upper_right
    return None, None

def calculate_deviance(current_pt, current_angle):
    angle_deviance = 0 - current_angle
    # virtual_rect_edge_center = np.array([(ix + ex)/2, max(iy, ey)])
    target = np.array([min(ix, ex), min(iy, ey)])
    deviance = target - current_pt
    return deviance, angle_deviance

def show_plan(plan):
    global client
    canvas = np.ones((200, 200, 3), dtype = "uint8") * 255
    if plan == 'Rotate Right':
        icon = cv2.imread('clockwise.png')
        client.send_post('k')
        stage = 'Matching Edge'
    elif plan == 'Rotate Left':
        icon = cv2.imread('counter-clockwise.png')
        client.send_post('j')
        stage = 'Matching Edge'
    elif plan == 'Move Up':
        icon = cv2.imread('up.png')
        client.send_post('w')
        stage = 'Matching Corner'
    elif plan == 'Move Down':
        icon = cv2.imread('down.png')
        client.send_post('s')
        stage = 'Matching Corner'
    elif plan == 'Move Left':
        icon = cv2.imread('left.png')
        client.send_post('a')
        stage = 'Matching Corner'
    elif plan == 'Move Right':
        icon = cv2.imread('right.png')
        client.send_post('d')
        stage = 'Matching Corner'
    elif plan == 'Matched':
        icon = cv2.imread('smiley.png')
        client.send_post('r')
        plan = 'No Action'
        stage = 'Matched'
    else:
        icon = np.ones((100, 100, 3), dtype = "uint8")*255
        plan = 'No Action'
        stage = 'No Task'

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, 'Action:', (10,20), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, plan, (10,35), font, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, 'Current Task: ', (10,165), font, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(canvas, stage, (10,180), font, 0.4, (0, 0, 255), 1, cv2.LINE_AA)
    icon = cv2.resize(icon, (100, 100))
    canvas[50:150, 50:150, :] = icon
    return canvas


def compute_plan(deviance, angle_deviance, corner_matched, edge_matched):
    # if (np.linalg.norm(deviance) < 10 and not corner_matched) or (np.linalg.norm(deviance) < 15 and corner_matched):
    if (np.linalg.norm(deviance) < 20):
        # adjust angle
        # if (abs(angle_deviance) < 1 and not edge_matched) or (abs(angle_deviance) < 5 and edge_matched):
        if (abs(angle_deviance) < 3):
            return 'Matched', True, True
        else:
            if angle_deviance < 0:
                return 'Rotate Left', True, False
            else:
                return 'Rotate Right', True, False
    else: 
        if abs(deviance[0]) > abs(deviance[1]):
            if deviance[0] > 0:
                return 'Move Right', False, False
            else:
                return 'Move Left', False, False
        else:
            if deviance[1] > 0:
                return 'Move Down', False, False
            else:
                return 'Move Up', False, False



def main():
    # Use the index appropriate for your external webcam (commonly 1 for the first external one)
    cap = cv2.VideoCapture() 
    cap.open(camera)

    if not cap.isOpened():
        print("Error: Could not open video capture device.")
        return
    canvas = np.ones((200, 200, 3), dtype = "uint8") * 255

    cv2.namedWindow('Webcam')
    cv2.setMouseCallback('Webcam', draw_rectangle)
    # cv2.namedWindow('Webcam')
    # cv2.setMouseCallback('Webcam', draw_rectangle)

    end = False
    detect = False
    start_calc = False
    old_left, old_right = None, None
    alpha = 0.15
    plan = None
    corner_matched, edge_matched = False, False
    while not end:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break
        outer_crop_px = 50
        h, w = 640, 480
        frame = cv2.resize(frame, (640, 480))[outer_crop_px:w - outer_crop_px, outer_crop_px:h - outer_crop_px, :]
        # h, w = frame.shape[:2]
        # frame = frame[100: h-100, 100:w - 100, :].copy()
        
        # gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # matching upper left
        if detect:
            upper_left, upper_right = get_top_corners(frame)
            # print(upper_left, upper_right)
            if upper_left is not None and upper_right is not None:
                current_angle = np.rad2deg(np.arctan2((upper_right[1] - upper_left[1]), (upper_right[0] - upper_left[0])))
                # edge_center = (upper_left + upper_right) / 2   
                if old_left is None and old_right is None:
                    old_left, old_right = upper_left, upper_right
                # edge_center = (1-alpha) * old_center + alpha * edge_center
                upper_right = (1-alpha) * old_right + alpha * upper_right
                upper_left = (1-alpha) * old_left + alpha * upper_left
                old_left, old_right = upper_left, upper_right
                # print(edge_center)
                upper_right = np.int32(upper_right)
                upper_left = np.int32(upper_left)
                cv2.line(frame, tuple(upper_left), tuple(upper_right), (255, 0, 0), 2)
                cv2.circle(frame, tuple(upper_left), 15, (0, 0, 255), -1)
                cv2.circle(frame, tuple(upper_right), 15, (0, 0, 255), -1)
                # cv2.circle(frame, (int(edge_center[0]), int(edge_center[1])), 10, (0, 0, 255), -1)
                # Start calculations
                if start_calc and (ix != -1 and iy != -1 and ex != -1 and ey != -1):
                    deviance, angle_deviance = calculate_deviance(upper_left, current_angle)
                    plan, corner_matched, edge_matched = compute_plan(deviance, angle_deviance, corner_matched, edge_matched)
                    print("deviance: ", deviance, "angle_deviance: ", angle_deviance, "plan: ", plan)
        # Visualizations
        if ix != -1 and iy != -1 and ex != -1 and ey != -1:
            cv2.rectangle(frame, (ix, iy), (ex, ey), (0, 255, 0), 2)
        # print(detect, start_calc, plan)
        cv2.imshow('canvas', show_plan(plan))
        cv2.imshow('Webcam', frame)
        cv2.waitKey(1)
        # print("happening")

        # Break the loop when 'q' is pressed
        if keyboard.is_pressed('q'):
            end = True
        if keyboard.is_pressed('s'):
            start_calc = True        
        if keyboard.is_pressed('d'):
            detect = True
        if keyboard.is_pressed('r'):
            detect = False
            start_calc = False

    # Release the capture and close any OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
