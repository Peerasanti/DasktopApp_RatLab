from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Style
from PIL import Image, ImageTk
import os
import cv2
import numpy as np


from utils import *
from validate import *
from detection import *


window_width = 980
window_height = 720
window = Tk()
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2) - 50
window.title("Rat Lab")
window.resizable(False, False)
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

output_name = ""
cap = None
is_playing = False
file_path = ""
folder_path = ""
save_path = ""

menu_bar = Menu()
window.config(menu=menu_bar)

def close_window(event):
    window.destroy()

def select_file():
    global cap, video_label, file_path
    file_path = filedialog.askopenfilename(
        title = "เลือกไฟล์วิดีโอทดลอง", 
        filetypes = (("MP4 files", "*.mp4"), ("All files", "*.*")) 
    )
    print("ไฟล์ที่เลือก:", file_path)
    if file_path and file_path.endswith(".mp4"): 
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.resize(frame_rgb, (video_width, video_height))

                img = Image.fromarray(frame_rgb)
                photo = ImageTk.PhotoImage(image=img)

                video_label.config(image=photo)
                video_label.image = photo
                path_label.config(text=f"ไฟล์วิดีโอเลือกได้ {file_path}", fg="green")
            else:
                path_label.config(text="ไม่สามารถเปิดไฟล์วิดีโอได้", fg="red")
        else:
            path_label.config(text="ไม่สามารถเปิดไฟล์วิดีโอได้", fg="red")
    else :
        path_label.config(text="โปรดเลือกไฟล์ใหม่อีกที", fg="red")

def select_folder():
    global folder_path
    folder_path = filedialog.askdirectory(title = "โฟลเดอร์สําหรับบันทึกไฟล์")
    if folder_path:
        folder_label.config(text=f"ได้เลือกโฟลเดอร์ {folder_path}", fg="green")
    else:
        folder_label.config(text="ไม่ได้เลือกโฟลเดอร์")

def clear():
    path_label.config(text="ยังไม่ได้เลือกไฟล์")
    video_label.config(image="")
    name_entry.delete(0, END)
    rat_entry.delete(0, END)
    weight_entry.delete(0, END)
    sex_entry.current(0)

def save():
    global output_name, file_path, folder_path, save_path
    output_name = name_entry.get().strip()
    rat_ID = rat_entry.get().strip()
    weight = weight_entry.get().strip()
    sex = sex_entry.get().strip()
    map = map_entry.get().strip()
    pill = pill_entry.get().strip()
    time = time_entry.get().strip()
    date = date_entry.get().strip()
    note = note_entry.get("1.0", "end-1c").strip()

    if file_path and folder_path:
        if output_name and rat_ID and sex and map and pill:
            errors = validate_data(output_name, weight, time, date)
            if errors:
                warning_label.config(text="\n".join(errors), fg="red")
                warning_label.place(x=570, y=630, width=250, height=25)
            else:
                save_path = os.path.join(folder_path, f"{output_name}.csv")
                continue_button.place(x=750, y=590, width=80, height=30)
                warning_label.place_forget()
                messagebox.showinfo("บันทึกข้อมูลเรียบร้อย", "ข้อมูลถูกบันทึกเรียบร้อยแล้ว")
        else:
            warning_label.config(text="โปรดกรอกรายละเอียดการทดลองให้ครบ", fg="red")
            warning_label.place(x=570, y=630, width=250, height=25)
    else: 
        warning_label.config(text="โปรดเลือกไฟล์และโฟลเดอร์", fg="red")
        warning_label.place(x=570, y=630, width=250, height=25)

def next_step():
    global file_path
    new_window = Toplevel(window)
    new_window.title("Rat Lab")
    new_window.state("zoomed")

    video_label = Label(new_window)
    video_label.pack(side=LEFT)

    # สร้างอินสแตนซ์ของ VideoDetection
    detector = VideoDetection(file_path, new_window, video_label)

    def drawing():
        if detector.is_drawing :
            detector.is_drawing = False
            start_button.config(text="Start Drawing")
            new_window.config(cursor="arrow")
        else:
            detector.is_drawing = True
            start_button.config(text="Stop Drawing")
            new_window.config(cursor="cross")

    start_button = Button(new_window, text="Start Drawing", command=drawing, bg="white", fg="black")
    start_button.place(x=20, y=730, width=150, height=40)

    # ผูกเหตุการณ์
    video_label.bind("<Button-1>", detector.mouse_callback)
    video_label.bind("<Button-3>", detector.mouse_callback)
    video_label.bind("<Motion>", detector.mouse_callback)
    new_window.bind("<KeyPress>", detector.key_handler)

    # จัดการการปิดหน้าต่าง
    new_window.protocol("WM_DELETE_WINDOW", detector.cleanup)

    # เริ่มอัปเดตวิดีโอ
    detector.update_video()






### ส่วนของ GUI ในหน้าแรก ###
window.bind("<Control-s>", select_folder)
window.bind("<Escape>", close_window)
menu_item = Menu()
menu_item.add_command(label="เปิด", command=select_file)
menu_item.add_command(label="บันทึกที่", command=select_folder, accelerator="Ctrl + S")
menu_item.add_separator()
menu_item.add_command(label="ออก", command=window.quit, accelerator="Esc")

menu_bar.add_cascade(label="ไฟล์", menu=menu_item)
menu_bar.add_cascade(label="แก้ไข")
menu_bar.add_cascade(label="ช่วยเหลือ")

frame_width = 500
frame_height = 500
frame = LabelFrame(window, text="วิดีโอ", borderwidth=3, relief="groove")
frame.place(x=50,  y=50, width=frame_width, height=frame_height)

video_width = 440
video_height = 452
video_label = Label(frame)
video_label.place(x=20, y=14, width=video_width, height=video_height)

select_file_button = Button(window, text="เลือกไฟล์วิดิโอ", command=select_file)
select_file_button.place(x=50, y=590, width=80, height=30)

or_label = Label(window, text="หรือ")
or_label.place(x=150, y=595)

cam_button = Button(window, text="เชื่อมต่อกล้องด้วย IP Camera")
cam_button.place(x=200, y=590, width=150, height=30)

path_label = Label(window, text="ยังไม่ได้เลือกไฟล์")
path_label.place(x=50, y=560)

folder_label = Label(window, text="ยังไม่ได้เลือกโฟลเดอร์", anchor="w")
folder_label.place(x=570, y=560, width=250, height=25)

warning_label = Label(window, text="โปรดกรอกรายละเอียดการทดลองให้ครบ", fg="red", anchor="w")
explain_label = Label(window, text="* ต้องใช้ชื่อไฟล์ที่มีอักษรและตัวเลขเท่านั้น\n"
                                   "* ต้องกรอกข้อมูลลงในช่องที่มีสีพื้นหลังให้ครบ\n"
                                   "* ต้องกรอกข้อมูลให้ตรงตามรูปแบบที่กำหนด\n"
                                   "* หากไม่มีข้อมูลให้เว้นว่างหรือใส่ \"-\"", 
                      fg="red", anchor="w", justify="left")
explain_label.place(x=50, y=630, width=300, height=70)


### ส่วนของการกรอกรายละเอียดการทดลอง ###
name_label = Label(window, text="ชื่อการทดลอง/ชื่อไฟล์ : ", bg="#FFFFCC")
name_label.place(x=570, y=50)

name_entry = Entry(window)
name_entry.place(x=690, y=50, width=250, height=25)

rat_label = Label(window, text="ชื่อหนูทดลอง/ID : ", bg="#FFFFCC")
rat_label.place(x=570, y=80)

rat_entry = Entry(window)
rat_entry.place(x=690, y=80, width=250, height=25)

weight_label = Label(window, text="น้ําหนักหนูทดลอง : ")
weight_label.place(x=570, y=110)

weight_entry = Entry(window)
weight_entry.place(x=690, y=110, width=250, height=25)

sex_label = Label(window, text="เพศหนูทดลอง : ", bg="#FFFFCC")
sex_label.place(x=570, y=140)

sex = ["เลือกเพศของหนูทดลอง", "เพศผู้", "เพศเมีย"]
sex_entry = Combobox(window, value=sex)
sex_entry.place(x=690, y=140, width=250, height=25)
sex_entry.current(0)

map_label = Label(window, text="แผนที่ที่ใช้ทดลอง : ", bg="#FFFFCC")
map_label.place(x=570, y=170)

map = ["X-maze", "Y-maze", "Water maze"]
map_entry = Combobox(window, value=map, state="normal")
map_entry.place(x=690, y=170, width=250, height=25)

pill_label = Label(window, text="ยาที่ใช้ในการทดลอง : ")
pill_label.place(x=570, y=200)

pill_entry = Entry(window)
pill_entry.place(x=690, y=200, width=250, height=25)

time_label = Label(window, text="เวลาที่ใช้ในการทดลอง : ")
time_label.place(x=570, y=230)

time_entry = Entry(window)
time_entry.place(x=690, y=230, width=250, height=25)

date_label = Label(window, text="วันที่ทดลอง : ")
date_label.place(x=570, y=260)

date_entry = Entry(window)
date_entry.insert(0, get_thai_date())
date_entry.place(x=690, y=260, width=250, height=25)

note_label = Label(window, text="หมายเหตุ : ")
note_label.place(x=570, y=290)

note_entry = Text(window, wrap="word")
note_entry.place(x=690, y=290, width=250, height=200)


### ปุ่มบันทึก ล้างทั้งหมด ดําเนินการต่อ เพื่อใช้กับส่วนกรอกข้อมูลข้างบน ###
save_button = Button(window, text="บันทึก", command=save)
save_button.place(x=570, y=590, width=80, height=30)

clear_button = Button(window, text="ล้างทั้งหมด", command=clear)
clear_button.place(x=660, y=590, width=80, height=30)

select_folder_button = Button(window, text="เลือกโฟลเดอร์บันทึกผลลัพธ์", command=select_folder)
select_folder_button.place(x=570, y=520, width=130, height=30)

continue_button = Button(window, text="ดําเนินการต่อ", command=next_step)
continue_button.place(x=750, y=590, width=80, height=30)

window.mainloop()