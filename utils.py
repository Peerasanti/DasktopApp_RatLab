from datetime import datetime

thai_months = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

def get_thai_date():
    current_date = datetime.now()
    day = current_date.day
    month = thai_months[current_date.month - 1]
    year = current_date.year + 543
    return f"{day} {month} {year}"
