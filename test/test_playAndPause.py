import cv2
import numpy as np

file_path = "C:/Users/WINDOWS/Downloads/Seminar/X-maze.mp4"
cap = cv2.VideoCapture(file_path)

frame_width = 1100
frame_height = 800
is_playing = False

ret, frame = cap.read()
if not ret:
    print("Error: ไม่สามารถอ่านเฟรมแรกของวิดีโอได้")
    cap.release()
    exit()

frame = cv2.resize(frame, (frame_width, frame_height))
current_frame = frame.copy()

# ตัวแปรสำหรับจัดการ Polygon หลายอัน
polygons = [[]]  # ลิสต์ของ Polygon แต่ละอัน
is_closed = [False]  # สถานะปิดของแต่ละ Polygon
current_polygon = 0  # ดัชนี Polygon ปัจจุบัน
temp_point = None

def mouse_callback(event, x, y, flags, param):
    global polygons, is_closed, current_polygon, temp_point
    if event == cv2.EVENT_LBUTTONDOWN and not is_closed[current_polygon]:
        polygons[current_polygon].append((x, y))
    elif event == cv2.EVENT_MOUSEMOVE and len(polygons[current_polygon]) >= 1 and not is_closed[current_polygon]:
        temp_point = (x, y)
    elif event == cv2.EVENT_RBUTTONDOWN and len(polygons[current_polygon]) > 2 and not is_closed[current_polygon]:
        is_closed[current_polygon] = True
        polygons.append([])  # เริ่ม Polygon ใหม่
        is_closed.append(False)
        current_polygon += 1
        temp_point = None

def draw_polygons(img):
    # วาด Polygon ทั้งหมดและเส้นชั่วคราว
    for i, polygon in enumerate(polygons):
        if len(polygon) == 1:
            cv2.circle(img, polygon[0], 5, (0, 0, 255), -1)
        elif len(polygon) > 1:
            cv2.polylines(img, [np.array(polygon)], isClosed=is_closed[i], color=(0, 0, 255), thickness=2)
    if temp_point and len(polygons[current_polygon]) >= 1 and not is_closed[current_polygon]:
        cv2.line(img, polygons[current_polygon][-1], temp_point, (0, 0, 255), 2)

cv2.namedWindow("Video Playback")
cv2.setMouseCallback("Video Playback", mouse_callback)

while cap.isOpened():
    if is_playing:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (frame_width, frame_height))
        current_frame = frame.copy()
    
    # สร้างสำเนาเฟรมและวาด Polygon
    img = current_frame.copy()
    draw_polygons(img)
    
    # แสดงสถานะ Play/Pause
    cv2.putText(img, "Playing" if is_playing else "Paused", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Video Playback", img)
    
    key = cv2.waitKey(30 if is_playing else 0) & 0xFF
    if key == ord('p'):  
        is_playing = not is_playing
    elif key == ord('q'): 
        break

cap.release()
cv2.destroyAllWindows()