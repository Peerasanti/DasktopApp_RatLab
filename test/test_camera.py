import cv2

cap = cv2.VideoCapture(0)  # ลองเปลี่ยนเป็น 1 หรือ 2 ถ้ามีกล้องหลายตัว

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
