import os
### turn off onednn (Tensorflow extension)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import tensorflow as tf
from skimage.transform import resize
from collections import deque
import numpy as np
import time
import csv
import cv2

### settings tensorflow , model and video path
model_path = "C:/Users/WINDOWS/Downloads/Seminar/OpenCV/project/model/model_for_rat_V2.keras"
video_path = "C:/Users/WINDOWS/Downloads/Seminar/Y-maze.mp4"

### Try to load model 
try :
    model = tf.keras.models.load_model(model_path , safe_mode=False)
    print("Load model success")
except Exception as e:
    print("Load model fail")
    print(f"Error : {e}")

""" 
This function is for testing model 
Description : 
    This function will show result about video compare batween
    original video and result video 
Parameters : model , video_path
"""
def test_model(model, video_path):
    cap = cv2.VideoCapture(video_path)
    frame_size = [500, 512]

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        ### resize frame to prediction
        img = resize(frame, (128, 128), mode='constant', preserve_range=True)
        img = np.expand_dims(img, axis=0)
        result = model.predict(img)[0]
        result = (result * 255).astype(np.uint8)
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        result = resize(result, (frame_size[0], frame_size[1]))
        frame = resize(frame, (frame_size[0], frame_size[1]))

        cv2.imshow('model_result', result)
        cv2.imshow("result", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
### ----------------------------------------------------------------------------------------------------------------------------------------------------- ###
    
"""
This function is for testing overlay object from model to original video
Description : 
    This function will create mask video and overlay it on 
    original video
Parameters : model , video_path
"""
def overlay_object_test(model, video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        ### resize frame to prediction
        img = resize(frame, (128, 128), mode='constant', preserve_range=True)
        img = np.expand_dims(img, axis=0)
        result = np.squeeze(model.predict(img)[0])

        ### resize result for mask object in orinal frame
        mask = resize(result, (frame.shape[0], frame.shape[1])) > 0.5

        ### choose color for segmentation mask
        color = np.array([0, 255, 0], dtype=np.uint8)

        ### create overlay mask
        overlay = frame.copy()
        overlay[mask, :] = color
        frame = cv2.addWeighted(overlay, 0.2, frame, 0.5, 0)

        ### display video
        cv2.imshow("Custom Model Segmentation", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release() 
    cv2.destroyAllWindows()
### ----------------------------------------------------------------------------------------------------------------------------------------------------- ###

"""
This function is for saving overlay object video
Description : 
    This function will save video from ovaerlay object video
Parameters : model , video_path
"""
def save_video_detection(model, video_path):
    cap = cv2.VideoCapture(video_path)
    ### define height & width for saving video
    frame_width = int(cap.get(3)) 
    frame_height = int(cap.get(4)) 
    size = (frame_width, frame_height) 

    # Below VideoWriter object will create 
    # a frame of above defined The output  
    # is stored in 'filename.avi' file. 
    save_video = cv2.VideoWriter('filename.avi',  cv2.VideoWriter_fourcc(*'MJPG'), 10, size)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
            
        ### resize frame to prediction
        img = resize(frame, (128, 128), mode='constant', preserve_range=True)
        img = np.expand_dims(img, axis=0)
        result = np.squeeze(model.predict(img)[0])

        ### resize result for mask object in orinal frame
        mask = resize(result, (frame.shape[0], frame.shape[1])) > 0.5

        ### choose color for segmentation mask
        color = np.array([0, 255, 0], dtype=np.uint8)

        ### create overlay mask
        overlay = frame.copy()
        overlay[mask, :] = color
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

        save_video.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        save_video.release()
        cv2.destroyAllWindows()
### ----------------------------------------------------------------------------------------------------------------------------------------------------- ###


"""
This function is find center of rat and overloay it on original video
Description : 
    This function will find center of rat and overlay it on original video
    for check rat position and save data to csv file
Parameters : model , video_path
"""
def find_center_by_overlay(model, video_path):
    cap = cv2.VideoCapture(video_path)
    ### Check video frame rate
    fps = round(cap.get(cv2.CAP_PROP_FPS), 1)

    ### Create csv file and choose path to save it
    with open('C:/Users/WINDOWS/Downloads/Seminar/OpenCV/project/smartLab.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        ### Add header column
        field = ["Execute Time", "Timestamp", "Frame No.", "Rat position X", "Rat position Y", "Current Zone"]
        writer.writerow(field)
        start_time = time.time()


        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            ### resize frame to prediction
            img = resize(frame, (128, 128), mode='constant', preserve_range=True)
            img = np.expand_dims(img, axis=0)
            result = np.squeeze(model.predict(img)[0])

            ### resize result for mask object in orinal frame
            mask = resize(result, (frame.shape[0], frame.shape[1])) > 0.5

            ### choose color for segmentation mask
            color = np.array([0, 255, 0], dtype=np.uint8)

            ### create overlay mask
            overlay = frame.copy()

            ### draw shape
            zones = {
                "Zone A" : np.array([[449, 244], [429, 276], [138, 54], [185, 40]], np.int32),
                "Zone B" : np.array([[449, 244], [461, 276], [767, 57], [724, 40]], np.int32),
                "Zone C" : np.array([[429, 276], [461, 276], [461, 774], [429, 774]], np.int32),
            }
            zones = {name: poly.reshape((-1, 1, 2)) for name, poly in zones.items()}
            current_zone = ""

            overlay[mask, :] = color
            
            ### find centroid of object and draw it for assign it as a rat center
            coords = np.column_stack(np.where(mask)) 
            if len(coords) > 0: 
                centroid = np.mean(coords, axis=0).astype(int) 
                cx, cy = centroid[1], centroid[0] 

                for zone, poly in zones.items():
                    if cv2.pointPolygonTest(poly, (float(cx), float(cy)), False) >= 0: 
                        color = (0, 255, 0) 
                        current_zone = zone
                    else:
                        color = (0, 0, 255) 

                    cv2.fillPoly(overlay, [poly], color)

                ### Draw centroid point
                cv2.circle(frame, (cx, cy), radius=3, color=(255, 0, 0), thickness=-1)
                cv2.putText(frame, "Rat position X: {}, Y: {}".format(cx, cy), (15, 700), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)
                cv2.putText(frame, "Video {} fps".format(fps), (15, 760), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)

            current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
            time_past = round((current_frame / fps), 3)
            timestamp = round((time.time() - start_time), 3)
            cv2.putText(frame, "Time {} second".format(round(time_past, 2)), (15, 730), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 2)

            frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

            ### display video
            cv2.imshow("Custom Model Segmentation", frame)

            ### write data to csv file
            writer.writerow([timestamp, '{} second'.format(time_past), current_frame, cx, cy, current_zone])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release() 
        cv2.destroyAllWindows()
### ----------------------------------------------------------------------------------------------------------------------------------------------------- ###

line = deque(maxlen=150)
def rat_path(model, video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        ### resize frame to prediction
        img = resize(frame, (128, 128), mode='constant', preserve_range=True)
        img = np.expand_dims(img, axis=0)
        result = np.squeeze(model.predict(img)[0])

        ### resize result for mask object in orinal frame
        mask = resize(result, (frame.shape[0], frame.shape[1])) > 0.5

        ### find centroid of object and draw it for assign it as a rat center
        coords = np.column_stack(np.where(mask)) 
        if len(coords) > 0: 
            centroid = np.mean(coords, axis=0).astype(int) 
            cx, cy = centroid[1], centroid[0] 

            ### Draw centroid point
            cv2.circle(frame, (cx, cy), radius=3, color=(255, 0, 0), thickness=-1)

            if len(line) > 1:
                for i in range(1, len(line)):
                    cv2.line(frame, line[i - 1], line[i], (0, 255, 0), 2)
            line.appendleft((cx, cy))
        
        cv2.imshow("Custom Model Segmentation", frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release() 
    cv2.destroyAllWindows()
### ----------------------------------------------------------------------------------------------------------------------------------------------------- ###

from collections import deque
import cv2
import numpy as np
from skimage.transform import resize

def path_heatmap(model, video_path, scale_factor=2, circle_radius=20):
    cap = cv2.VideoCapture(video_path)

    heatmap = None
    frame_count = 0 

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        if frame_count == 0: 
            heatmap_height = frame.shape[0] * scale_factor
            heatmap_width = frame.shape[1] * scale_factor
            heatmap = np.zeros((heatmap_height, heatmap_width), dtype=np.float32)
        frame_count += 1

        ### resize frame to prediction
        img = resize(frame, (128, 128), mode='constant', preserve_range=True)
        img = np.expand_dims(img, axis=0)
        result = np.squeeze(model.predict(img)[0])

        ### resize result for mask object in original frame
        mask = resize(result, (frame.shape[0], frame.shape[1])) > 0.5

        ### find centroid of object and draw it for assign it as a rat center
        coords = np.column_stack(np.where(mask)) 
        if len(coords) > 0: 
            centroid = np.mean(coords, axis=0).astype(int) 
            cx, cy = centroid[1], centroid[0] 

            ### ปรับตำแหน่งให้สเกลตาม heatmap
            cx_scaled = int(cx * scale_factor)
            cy_scaled = int(cy * scale_factor)

            ### อัปเดต heatmap โดยสะสมน้ำหนักในรูปวงกลม
            cv2.circle(heatmap, (cx_scaled, cy_scaled), radius=circle_radius * scale_factor, color=1, thickness=-1)
        
        ### ปรับขนาด kernel ให้เป็นเลขคี่
        base_kernel_size = 25
        kernel_size = base_kernel_size * scale_factor
        if kernel_size % 2 == 0:  # ถ้าเป็นเลขคู่ ให้เพิ่ม 1
            kernel_size += 1
        kernel = (kernel_size, kernel_size)

        ### สร้าง heatmap ที่เรียบเนียนด้วย Gaussian blur
        heatmap_blur = cv2.GaussianBlur(heatmap, kernel, 0)
        heatmap_normalized = np.uint8(255 * heatmap_blur / (heatmap_blur.max() + 1e-10))  # Normalize ตามค่าสูงสุด
        heatmap_color = cv2.applyColorMap(heatmap_normalized, cv2.COLORMAP_JET)

        ### ปรับขนาด heatmap เพื่อ overlay กับวิดีโอ
        heatmap_resized = cv2.resize(heatmap_color, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_LINEAR)
        overlay = cv2.addWeighted(frame, 0.7, heatmap_resized, 0.3, 0)

        ### แสดงผล
        cv2.imshow("Custom Model Segmentation", overlay)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # บันทึก heatmap สุดท้าย (ถ้าต้องการ)
    cv2.imwrite("final_heatmap.png", heatmap_color)
    cap.release()
    cv2.destroyAllWindows()
### ----------------------------------------------------------------------------------------------------------------------------------------------------- ###



### Call function ###
"""
Use to call function and add argument for function
if you don't need to use function just comment it
but if want to use just uncomment it 
"""
#####################
### function name ###
#####################
if __name__ == "__main__":
    print('Test model')

    # test_model(model, video_path)
    # overlay_object_test(model, video_path)
    find_center_by_overlay(model, video_path) # use only y-maze
    # rat_path(model, video_path)
    # path_heatmap(model, video_path)

