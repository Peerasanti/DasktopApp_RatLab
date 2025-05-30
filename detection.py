import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import cv2
import numpy as np
from PIL import Image, ImageTk
from skimage.transform import resize
import tensorflow as tf
import csv
from tkinter import messagebox


class VideoDetection:
    def __init__(self, file_path, window, label):
        self.cap = cv2.VideoCapture(file_path)
        self.fps = round(self.cap.get(cv2.CAP_PROP_FPS), 1)
        self.window = window
        self.label = label
        self.frame_width = 1150
        self.frame_height = 850
        self.speed = 20
        self.position_x = None
        self.position_y = None
        self.time_past = None
        
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
        self.detected = False

        self.model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model", "model_for_rat_V2.keras")
        try:
            self.model = tf.keras.models.load_model(self.model_path, safe_mode=False)
            print("Load model success")
        except Exception as e:
            print("Not found model file in folder '{}'".format(self.model_path))
            print(f"Error : {e}")
        self.input_size = (128, 128)

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


    def speed_up(self):
        self.speed = max(5, self.speed - 5)

    def speed_down(self):
        self.speed = min(100, self.speed + 5)
    
    def unet_detect(self, frame):
        input_frame = resize(frame, self.input_size, mode='constant', preserve_range=True)
        input_frame = np.expand_dims(input_frame, axis=0)
        
        result = np.squeeze(self.model.predict(input_frame, verbose=0)[0])
        mask = resize(result, (self.frame_height, self.frame_width), anti_aliasing=False) > 0.5

        coords = np.column_stack(np.where(mask)) 
        if len(coords) > 0: 
            centroid = np.mean(coords, axis=0).astype(int) 
            self.position_x, self.position_y = centroid[1], centroid[0] 
        else:
            self.position_x, self.position_y = None, None

        return mask
    
    def overlay_mask(self, img, mask, color=(0, 255, 200), alpha=0.5):
        overlay = img.copy()
        overlay[mask, :] = color
        return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

    def update_video(self):
        if self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                self.window.destroy()
                return
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            self.current_frame = frame.copy()
        
        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.time_past = round(current_frame / self.fps, 2)

        img = self.current_frame.copy()
        if self.detected:
            mask = self.unet_detect(img)
            img = self.overlay_mask(img, mask)
            cv2.circle(img, (self.position_x, self.position_y), 5, (0, 0, 255), -1)

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
        
            cv2.putText(img, "Press 'Up' to Speed Up", (20, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(img, "Press 'Down' to Speed Down", (20, 160), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(img, f"Speed: {self.speed} ms", (980, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(img, "Press 'T' to Detect", (20, 180),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.putText(img, f"Time: {self.time_past} second", (980, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # แปลงภาพเป็น PhotoImage
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_rgb))
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
        elif event.keysym == 'Up':
            self.speed_up()
        elif event.keysym == 'Down':
            self.speed_down()
        elif event.keysym == 't':
            self.detected = not self.detected

    def cleanup(self):
        if self.cap.isOpened():
            self.cap.release()

    def clear_area(self):
        self.polygons = [[]]
        self.is_closed = [False]
        self.current_polygon = 0

    def save_to_csv(self, data):
        filename = os.path.join(data['folder_path'], f"{data['output_name']}.csv")
        
        os.makedirs(data['folder_path'], exist_ok=True)

        with open(filename, 'w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            for key, value in data.items():
                writer.writerow([key, value])
    
        print(f"บันทึกข้อมูลลง {data['output_name']} เรียบร้อยแล้ว!")
        stop = messagebox.askyesno("บันทึกแล้วหยุดการทำงาน", f"บันทึกข้อมูลลง {data['output_name']} เรียบร้อยแล้ว!\nต้องการจะหยุดโปรแกรมหรือไม่?")
        if stop:
            self.window.destroy()