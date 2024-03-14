import cv2
from grip import GripPipeline
import numpy as np
from scipy.spatial import ConvexHull, convex_hull_plot_2d

img = cv2.imread("image.png")
# img = cv2.imread("Photo-1.jpg")
# img = cv2.imread("IMG_6083.jpg")
img = cv2.resize(img, (640, 480))
def rotate_image(image, angle):
  image_center = tuple(np.array(image.shape[1::-1]) / 2)
  rot_mat = cv2.getRotationMatrix2D(image_center, angle, 0.5)
  result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
  return result

img = rotate_image(img, 35)
pipeline = GripPipeline()
pipeline.process(img)
filtered_lines = pipeline.find_lines_output
pts = []
for line in filtered_lines:
    x1, y1, x2, y2 = int(line.x1), int(line.y1), int(line.x2), int(line.y2)
    pts += [[x1, y1]]
    pts += [[x2, y2]]
    # cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
pts = np.array(pts, np.int32)
pts_center = np.mean(pts, axis=0)
pts_std = np.std(pts, axis=0)
# remove outliers
pts = pts[pts[:, 0] > pts_center[0] - 4 * pts_std[0]]
pts = pts[pts[:, 0] < pts_center[0] + 4 * pts_std[0]]
pts = pts[pts[:, 1] > pts_center[1] - 4 * pts_std[1]]
pts = pts[pts[:, 1] < pts_center[1] + 4 * pts_std[1]]

hull = ConvexHull(pts)
bounding_hull = pts[hull.vertices]
upper_left = sorted(bounding_hull.copy(), key=lambda x: x[0] + x[1])[0]
bot_right = sorted(bounding_hull.copy(), key=lambda x: x[0] + x[1])[-1]

slope = (bot_right[1] - upper_left[1]) / (bot_right[0] - upper_left[0])
intercept = upper_left[1] - slope * upper_left[0]
line_func = lambda x: slope * x + intercept

upper_right_hull = bounding_hull[bounding_hull[:, 1] < line_func(bounding_hull[:, 0])]

def perp_dist_to_line(pt):
    x, y = pt
    return abs(-slope * x + y - intercept) / np.sqrt(slope ** 2 + 1)

upper_right = sorted(upper_right_hull, key=perp_dist_to_line)[-1]

cv2.line(img, tuple(upper_left), tuple(upper_right), (255, 0, 0), 2)

cv2.circle(img, tuple(upper_left), 10, (0, 0, 255), -1)
cv2.circle(img, tuple(upper_right), 10, (0, 0, 255), -1)
cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()