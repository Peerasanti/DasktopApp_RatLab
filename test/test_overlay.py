import numpy as np
from skimage.transform import resize
import cv2
import tkinter as tk
from PIL import Image, ImageTk

class VideoSegmentationApp:
    def __init__(self, window, model, video_path, input_size=(128, 128), frame_width=800, frame_height=600):
        self.window = window
        self.window.title("Video Segmentation with U-Net")
        
        # Initialize variables
        self.model = model
        self.input_size = input_size
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.is_playing = True
        self.show_ui = True
        self.speed = 33  # Default 33 ms (~30 FPS)
        
        # Video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Read first frame to initialize
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            self.current_frame = frame.copy()
        else:
            raise ValueError("Cannot read first frame from video")
        
        # Tkinter UI
        self.label = tk.Label(self.window)
        self.label.pack()
        
        # Bind keys
        self.window.bind('<p>', lambda e: self.toggle_play_pause())
        self.window.bind('<q>', lambda e: self.quit())
        self.window.bind('<h>', lambda e: self.toggle_ui())
        self.window.bind('<Up>', lambda e: self.speed_up())
        self.window.bind('<Down>', lambda e: self.speed_down())
        
        # Start video update
        self.update_video()

    def unet_detect(self, frame):
        """Detect objects using U-Net and return a binary mask."""
        input_frame = resize(frame, self.input_size, mode='constant', preserve_range=True)
        input_frame = np.expand_dims(input_frame, axis=0)
        result = np.squeeze(self.model.predict(input_frame, verbose=0)[0])
        
        mask = resize(result, (self.frame_height, self.frame_width)) > 0.5 
        color = np.array([0, 255, 0], dtype=np.uint8)

        overlay = frame.copy()
        overlay[mask, :] = color
        frame = cv2.addWeighted(overlay, 0.2, frame, 0.5, 0)
        
        return frame
        
        

    def draw_polygons(self, img):
        """Placeholder for drawing polygons."""
        pass  # Add your polygon logic here if needed

    def update_video(self):
        """Update video frame and UI."""
        if self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.quit()
                return
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            self.current_frame = frame.copy()

        img = self.current_frame.copy()
        img = self.unet_detect(img)

        self.draw_polygons(img)

        if self.show_ui:
            self._draw_ui(img)

        # Convert to Tkinter-compatible image
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(img_rgb))
        self.label.config(image=img_tk)
        self.label.image = img_tk  # Keep reference

        # Schedule next update
        self.window.after(self.speed, self.update_video)

    def _draw_ui(self, img):
        """Draw UI elements on the image."""
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
        cv2.putText(img, f"Speed: {self.speed} ms", (self.frame_width - 100, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def toggle_play_pause(self):
        self.is_playing = not self.is_playing

    def toggle_ui(self):
        self.show_ui = not self.show_ui

    def speed_up(self):
        self.speed = max(1, self.speed - 10)  # Minimum 1 ms

    def speed_down(self):
        self.speed = min(100, self.speed + 10)  # Maximum 100 ms

    def quit(self):
        self.is_playing = False
        if self.cap.isOpened():
            self.cap.release()
        self.window.destroy()

if __name__ == "__main__":
    import tensorflow as tf
    
    # Load model
    model_path = "../model/model_for_rat_V2.keras"  # เปลี่ยนเป็น path จริง
    model = tf.keras.models.load_model(model_path, safe_mode=False)
    
    # Start app
    root = tk.Tk()
    app = VideoSegmentationApp(root, model, "C:/Users/WINDOWS/Downloads/Seminar/Y-maze.mp4")  # เปลี่ยนเป็น path วิดีโอจริง
    root.mainloop()