import re

thai_months = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def is_valid_filename(filename):
    invalid_chars = r'[<>:"/\\|?*]'
    return bool(filename and not re.search(invalid_chars, filename))

def is_valid_weight(weight):
    try:
        w = float(weight)
        return w > 0
    except ValueError:
        return False

def is_valid_time(time_str):
    pattern = r"^\d{2}:\d{2}$"
    if re.match(pattern, time_str):
        hours, minutes = map(int, time_str.split(":"))
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    return False

def is_valid_date(date_str):
    try:
        day, month, year = date_str.split()
        day = int(day)
        year = int(year)
        return (1 <= day <= 31) and (month in thai_months) and (2500 <= year <= 3000)
    except (ValueError, IndexError):
        return False

def validate_data(output_name, weight, time, date):
    errors = []
    if not is_valid_filename(output_name):
        errors.append("ชื่อไฟล์ไม่ถูกต้อง (ห้ามใช้ <>:\"/\\|?*)")
    if not is_valid_weight(weight):
        errors.append("น้ำหนักต้องเป็นตัวเลขบวก")
    if not is_valid_time(time):
        errors.append("เวลาต้องอยู่ในรูปแบบ HH:MM (เช่น 14:30)")
    if not is_valid_date(date):
        errors.append("วันที่ต้องอยู่ในรูปแบบ DD เดือน YYYY (เช่น 22 มีนาคม 2568)")
    return errors