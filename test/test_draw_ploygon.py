import cv2
import numpy as np

# สร้างภาพว่าง
width, height = 800, 600
canvas = np.ones((height, width, 3), dtype=np.uint8) * 255

# ลิสต์เก็บจุดของ polygon
points = []
is_closed = False  # ตัวแปรกำหนดว่าปิดเส้นแล้วหรือยัง

# ฟังก์ชัน callback ของเมาส์
temp_point = None

def mouse_callback(event, x, y, flags, param):
    global points, is_closed, temp_point

    if event == cv2.EVENT_LBUTTONDOWN and not is_closed:
        points.append((x, y))
        temp_point = None  # รีเซ็ต temp_point หลังจากยืนยันจุด
        print(points)

    elif event == cv2.EVENT_MOUSEMOVE and len(points) >= 1 and not is_closed:
        temp_point = (x, y)  # เก็บตำแหน่งเมาส์ชั่วคราว

    elif event == cv2.EVENT_RBUTTONDOWN and len(points) > 2:
        is_closed = True
        temp_point = None

    draw_polygon()

def draw_polygon():
    img = canvas.copy()
    if len(points) == 1:
        cv2.circle(img, points[0], 5, (0, 0, 255), -1)
    if len(points) > 1:
        cv2.polylines(img, [np.array(points)], isClosed=is_closed, color=(0, 0, 255), thickness=2)
    if temp_point and len(points) >= 1:
        cv2.line(img, points[-1], temp_point, (0, 0, 255), 2)  # วาดเส้นชั่วคราว
    cv2.imshow("Polygon Drawer", img)

# ตั้งค่าการจับเมาส์
cv2.namedWindow("Polygon Drawer")
cv2.setMouseCallback("Polygon Drawer", mouse_callback)

# แสดงภาพ
cv2.imshow("Polygon Drawer", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
