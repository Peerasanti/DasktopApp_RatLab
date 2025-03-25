import re
from datetime import datetime

def is_valid_filename(filename):
    invalid_chars = r'[<>:"/\\|?*-]'
    return bool(filename and not re.search(invalid_chars, filename))

def is_valid_date(date_str):
    if not date_str or date_str == '-': 
        return True
    try:
        day, month, year = map(int, date_str.split('-'))
        datetime(year, month, day) 
        return 2500 <= year <= 3000  
    except (ValueError, IndexError):
        return False

def validate_data(output_name, date):
    errors = []
    if not is_valid_filename(output_name):
        errors.append("ชื่อไฟล์ไม่ถูกต้อง (ห้ามใช้ <>:\"/\\|?*)")
    if not is_valid_date(date):
        errors.append("วันที่ต้องอยู่ในรูปแบบ DD/MM/YYYY (เช่น 25-03-2568)")
    return errors