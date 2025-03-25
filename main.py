from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Style
from datetime import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import socket
import os
import cv2
import numpy as np
import locale


from utils import *
from validate import *
from detection import *

locale.setlocale(locale.LC_TIME, 'th_TH.UTF-8')

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

### global variable ###
output_name = ""
cap = None
is_playing = False
file_path = ""
folder_path = ""
save_path = ""
output_name = ""
rat_ID = ""
weight = 0
time = ""
date = ""
note = ""
data = {}
camera_id = ""

### window menu bar ###
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
    path_label.config(text="ยังไม่ได้เลือกไฟล์", fg="black")
    folder_label.config(text="ยังไม่ได้เลือกโฟลเดอร์", fg="black")
    video_label.config(image="")
    name_entry.delete(0, END)
    rat_entry.delete(0, END)
    sex_entry.current(0)
    map_entry.current(0)
    pill_entry.delete(0, END)
    date_entry.delete(0, END)
    note_entry.delete("1.0", "end")

def save():
    global output_name, file_path, folder_path, save_path, data
    output_name = name_entry.get().strip()
    rat_ID = rat_entry.get().strip()
    sex = sex_entry.get().strip() 
    map = map_entry.get().strip() 
    pill = pill_entry.get().strip() or '-'
    date = date_entry.get().strip() or '-'
    note = note_entry.get("1.0", "end-1c").strip() or '-'
    print(f"วันที่: {date}")

    if file_path and folder_path:
        if output_name and rat_ID and sex and map and pill:
            errors = validate_data(output_name, date)
            if errors:
                warning_label.config(text="\n".join(errors), fg="red")
                warning_label.place(x=570, y=630, width=350, height=25)
            else:
                save_path = os.path.join(folder_path, f"{output_name}.csv")
                continue_button.place(x=750, y=590, width=100, height=30)
                warning_label.place_forget()
                data = {
                    "output_name": output_name,
                    "file_path": file_path,
                    "folder_path": folder_path,
                    "rat_ID": rat_ID,
                    "sex": sex,
                    "map": map,
                    "pill": pill,   
                    "date": date,
                    "note": note
                }
                messagebox.showinfo("บันทึกข้อมูลเรียบร้อย", "ข้อมูลถูกบันทึกเรียบร้อยแล้ว")
        else:
            warning_label.config(text="โปรดกรอกรายละเอียดการทดลองให้ครบ", fg="red")
            warning_label.place(x=570, y=630, width=250, height=25)
    else: 
        warning_label.config(text="โปรดเลือกไฟล์และโฟลเดอร์สำหรับบันทึกผลลัพธ์", fg="red")
        warning_label.place(x=570, y=630, width=250, height=25)


def next_step():
    global file_path, data
    new_window = Toplevel(window)
    new_window.title("Rat Lab")
    new_window.state("zoomed")
    new_window.resizable(False, False)

    custom_font = ("Helvetica", 10)

    video_label = Label(new_window)
    video_label.pack(side=LEFT)

    canvas = Canvas(new_window, width=2, bg="black", height=1000)
    canvas.place(x=1150, y=0)

    # สร้างอินสแตนซ์ของ VideoDetection
    detector = VideoDetection(file_path, new_window, video_label)

    def drawing():
        if detector.is_drawing :
            detector.is_drawing = False
            start_button.config(text="Start Drawing", bg="#58d05a")
            new_window.config(cursor="arrow")
        else:
            detector.is_drawing = True
            start_button.config(text="Stop Drawing", bg="#FF7F7F")
            new_window.config(cursor="cross")

    start_button = Button(new_window, text="Start Drawing", command=drawing,
                          bg="#58d05a",
                          fg="white",
                          font=custom_font, 
                          activebackground="#FFFFE0")
    
    start_button.place(x=20, y=730, width=150, height=40)

    clear_area = Button(new_window, text="Clear All Area", command=detector.clear_area, 
                        bg="#58d05a", 
                        fg="white",
                        font=custom_font,
                        activebackground="#FFFFE0")
    
    clear_area.place(x=180, y=730, width=150, height=40)

    back_button = Button(new_window, text="Back", command=new_window.destroy,
                         bg="white", 
                         fg="black",
                         font=custom_font,
                         activebackground="#FFFFE0")
    
    back_button.place(x=1180, y=730, width=150, height=40)

    finish_button = Button(new_window, text="Finish" ,
                           bg="white", 
                           fg="black",
                           font=custom_font,
                           activebackground="#FFFFE0")
    
    finish_button.place(x=1340, y=730, width=150, height=40)

    title_label = Label(new_window, text="ข้อมูลการทดลอง", font=("Helvetica", 15))
    title_label.place(x=1180, y=20)

    data_label = Label(new_window, text=f"ชื่อการทดลอง : {data['output_name']}\n"
                                        f"ชื่อหนูทดลอง : {data['rat_ID']}\n"
                                        f"เพศหนูทดลอง : {data['sex']}\n"
                                        f"แผนที่ทดลอง : {data['map']}\n"
                                        f"ยาทดลอง : {data['pill']}\n"
                                        f"วันที่ทดลอง : {data['date']}\n"
                                        f"หมายเหตุ : {data['note']}", 
                        font=("Helvetica", 12), anchor=W, justify=LEFT)
    data_label.place(x=1180, y=50)

    video_label.bind("<Button-1>", detector.mouse_callback)
    video_label.bind("<Button-3>", detector.mouse_callback)
    video_label.bind("<Motion>", detector.mouse_callback)
    new_window.bind("<KeyPress>", detector.key_handler)

    new_window.protocol("WM_DELETE_WINDOW", detector.cleanup)

    detector.update_video()

def update_video():
    if cap and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (video_width, video_height))
            img = Image.fromarray(frame_rgb)
            photo = ImageTk.PhotoImage(image=img)
            video_label.config(image=photo)
            video_label.image = photo
        window.after(10, update_video) 

def is_valid_ip(ip):
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if ip_pattern.match(ip):
        return all(0 <= int(x) <= 255 for x in ip.split("."))
    return False

def connect_camera(ip_address):
    global cap
    camera_url = f"http://{ip_address}/video"

    if not is_valid_ip(ip_address):
        try:
            socket.gethostbyname(ip_address)
        except socket.gaierror:
            path_label.config(text=f"ไม่สามารถเชื่อมต่อไปที่ '{ip_address}' ได้", fg="red")
            return

    try:
        cv2.setUseOptimized(True)
        cap = cv2.VideoCapture(camera_url)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 1000)
        
        if not cap.isOpened():
            path_label.config(text="ไม่สามารถเชื่อมต่อกล้องได้", fg="red")
            print("ไม่สามารถเชื่อมต่อกล้องได้")
            camera_window() 
            return
        
        path_label.config(text=f"เชื่อมต่อไปที่ {camera_url}", fg="green")
        update_video()

    except Exception as e:
        path_label.config(text=f"เกิดข้อผิดพลาด: {str(e)}", fg="red")
        print(f"Error: {str(e)}")
        camera_window()

def camera_window():
    ip_window = Toplevel(window)
    ip_window.title("กรอก IP Camera")
    ip_window.geometry("300x150")

    label = Label(ip_window, text="กรุณากรอก IP Address ของกล้อง: ")
    label.pack(pady=10)

    ip_entry = Entry(ip_window, width=30)
    ip_entry.pack(pady=10)

    def submit_ip():
        ip = ip_entry.get() 
        if ip:
            ip_window.destroy() 
            connect_camera(ip)  
    
    button_frame = Frame(ip_window)
    button_frame.pack(pady=10)

    submit_button = Button(button_frame, text="ยืนยัน", command=submit_ip)
    submit_button.pack(side='left', padx=10)

    cancel_button = Button(button_frame, text="ยกเลิก", command=ip_window.destroy)
    cancel_button.pack(side='left', padx=10)

### for testing only ###
def skip_form(event):
    name_entry.insert(0, "Rat Lab 001")
    rat_entry.insert(0, "Rat 001")
    sex_entry.insert(0, "เพศผู้")
    map_entry.insert(0, "X-maze")
    pill_entry.insert(0, "Pill 001")
    note_entry.insert("1.0", "Note")

### ส่วนของ GUI ในหน้าแรก ###
window.bind("<Control-s>", select_folder)
window.bind("<Escape>", close_window)
window.bind("<S>", skip_form)
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

cam_button = Button(window, text="เชื่อมต่อกล้องด้วย IP Camera", command=camera_window)
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

sex_label = Label(window, text="เพศหนูทดลอง : ", bg="#FFFFCC")
sex_label.place(x=570, y=110)

sex = ["", "เพศผู้", "เพศเมีย"]
sex_entry = Combobox(window, value=sex)
sex_entry.place(x=690, y=110, width=250, height=25)
sex_entry.current(0)

map_label = Label(window, text="แผนที่ที่ใช้ทดลอง : ", bg="#FFFFCC")
map_label.place(x=570, y=140)

map = ["", "X-maze", "Y-maze", "Water maze"]
map_entry = Combobox(window, value=map, state="normal")
map_entry.place(x=690, y=140, width=250, height=25)

pill_label = Label(window, text="ยาที่ใช้ในการทดลอง : ")
pill_label.place(x=570, y=170)

pill_entry = Entry(window)
pill_entry.place(x=690, y=170, width=250, height=25)

date_label = Label(window, text="วันที่ทดลอง : ")
date_label.place(x=570, y=200)

date_entry = DateEntry(window, locale='th_TH', date_pattern='dd-mm-yyyy')
date_entry.place(x=690, y=200, width=250, height=25)
current_date = datetime.now()
thai_year = current_date.year + 543  
thai_date = current_date.replace(year=thai_year)  
date_entry.set_date(thai_date)

note_label = Label(window, text="หมายเหตุเพิ่มเติม : ")
note_label.place(x=570, y=230)

note_entry = Text(window, wrap="word")
note_entry.place(x=690, y=230, width=250, height=200)


### ปุ่มบันทึก ล้างทั้งหมด ดําเนินการต่อ เพื่อใช้กับส่วนกรอกข้อมูลข้างบน ###
save_button = Button(window, text="บันทึก", command=save)
save_button.place(x=570, y=590, width=80, height=30)

clear_button = Button(window, text="ล้างทั้งหมด", command=clear)
clear_button.place(x=660, y=590, width=80, height=30)

select_folder_button = Button(window, text="เลือกโฟลเดอร์บันทึกผลลัพธ์", command=select_folder)
select_folder_button.place(x=570, y=520, width=130, height=30)

continue_button = Button(window, text="ดําเนินการต่อ  -->", command=next_step)
# continue_button.place(x=750, y=590, width=100, height=30)

window.mainloop()