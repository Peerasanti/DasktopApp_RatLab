import cv2
import numpy as np
from PIL import Image, ImageTk

class VideoDetection:
    def __init__(self, file_path, window, label):
        self.cap = cv2.VideoCapture(file_path)
        self.window = window
        self.label = label
        self.frame_width = 1150
        self.frame_height = 800
        self.speed = 5
        
        if not self.cap.isOpened():
            print("Error: ไม่สามารถเปิดไฟล์วิดีโอได้")
            self.window.destroy()
            return
        
        ret, frame = self.cap.read()
        if not ret:
            print("Error: ไม่สามารถอ่านเฟรมแรกของวิดีโอได้")
            self.cap.release()
            self.window.destroy()
            return
        
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        self.current_frame = frame.copy()
        
        # ตัวแปรสำหรับ Polygon
        self.polygons = [[]]
        self.is_closed = [False]
        self.current_polygon = 0
        self.temp_point = None
        self.is_playing = False
        self.is_drawing = False
        self.show_ui = True

    def mouse_callback(self, event):
        if not self.is_drawing:
            return
        
        x, y = event.x, event.y
        if event.num == 1 and not self.is_closed[self.current_polygon]: 
            self.polygons[self.current_polygon].append((x, y))
        elif event.num == 3 and len(self.polygons[self.current_polygon]) > 2 and not self.is_closed[self.current_polygon]: 
            self.is_closed[self.current_polygon] = True
            self.polygons.append([])
            self.is_closed.append(False)
            self.current_polygon += 1
            self.temp_point = None
        elif len(self.polygons[self.current_polygon]) >= 1 and not self.is_closed[self.current_polygon]:
            self.temp_point = (x, y)

    def draw_polygons(self, img):
        for i, polygon in enumerate(self.polygons):
            if len(polygon) == 1:
                cv2.circle(img, polygon[0], 5, (0, 0, 255), -1)
            elif len(polygon) > 1:
                cv2.polylines(img, [np.array(polygon)], isClosed=self.is_closed[i], color=(0, 0, 255), thickness=2)
        if self.temp_point and len(self.polygons[self.current_polygon]) >= 1 and not self.is_closed[self.current_polygon]:
            cv2.line(img, self.polygons[self.current_polygon][-1], self.temp_point, (0, 0, 255), 2)

    def update_video(self):
        if self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                self.window.destroy()
                return
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            self.current_frame = frame.copy()

        img = self.current_frame.copy()
        self.draw_polygons(img)

        if self.show_ui:
            cv2.putText(img, "Playing" if self.is_playing else "Paused", (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            cv2.putText(img, "Press 'P' to Play/Pause", (20, 80), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(img, "Press 'Q' to Quit", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(img, "Press 'H' to Hide/Show UI", (20, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # แปลงภาพเป็น PhotoImage
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)
        self.label.config(image=img_tk)
        self.label.image = img_tk  # เก็บ reference

        # อัปเดตต่อเนื่อง
        self.window.after(self.speed, self.update_video)

    def key_handler(self, event):
        if event.keysym == 'p':
            self.is_playing = not self.is_playing
        elif event.keysym == 'q':
            self.cap.release()
            self.window.destroy()
        elif event.keysym == 'h':
            self.show_ui = not self.show_ui

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()