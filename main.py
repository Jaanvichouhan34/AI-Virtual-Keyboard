import cv2
from cvzone.HandTrackingModule import HandDetector
import time
import math
import pyautogui
import subprocess
import pygetwindow as gw
from playsound import playsound
import threading

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Hand detector
detector = HandDetector(detectionCon=0.8)

# Keyboard layout
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["Z", "X", "C", "V", "B", "N", "M", "<", "SPACE"]
]


button_list = []
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        x, y = 100 * j + 50, 100 * i + 50
        button_list.append({
            "pos": (x, y),
            "text": key,
            "size": (85, 85)
        })

# Sound function
def play_click_sound():
    threading.Thread(target=playsound, args=("click.mp3",), daemon=True).start()

# Draw all keys
def draw_all(img, button_list, hovered_button=None):
    for button in button_list:
        x, y = button["pos"]
        w, h = button["size"]
        color = (0, 255, 0) if button == hovered_button else (255, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)
        cv2.putText(img, button["text"], (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

# Launch Notepad
subprocess.Popen(['notepad.exe'])
time.sleep(1)

try:
    notepad = gw.getWindowsWithTitle('Untitled - Notepad')[0]
    notepad.activate()
except:
    print("❌ Could not bring Notepad to focus.")

# Main loop
final_text = ""
last_press_time = 0
delay = 0.3
click_threshold = 40

while True:
    success, img = cap.read()
    if not success:
        break

    hands, img = detector.findHands(img)
    hovered_button = None

    if hands:
        lmList = hands[0]["lmList"]
        x_tip, y_tip = lmList[8][0], lmList[8][1]
        x_middle, y_middle = lmList[12][0], lmList[12][1]

        distance = math.hypot(x_middle - x_tip, y_middle - y_tip)
        current_time = time.time()

        for button in button_list:
            x, y = button["pos"]
            w, h = button["size"]
            if x < x_tip < x + w and y < y_tip < y + h:
                hovered_button = button

                if distance < click_threshold and (current_time - last_press_time) > delay:
                    key = button["text"]
                    print("Pressed:", key)
                    play_click_sound()  # ✅ Play click sound

                    try:
                        notepad.activate()
                    except:
                        pass

                    if key == "<":
                        final_text = final_text[:-1]
                        pyautogui.press('backspace')
                    elif key == "":
                        final_text += " "
                        pyautogui.press('space')
                    else:
                        final_text += key
                        pyautogui.typewrite(key)

                    last_press_time = current_time
                break

    img = draw_all(img, button_list, hovered_button)

    # Display area
    cv2.rectangle(img, (50, 350), (1000, 450), (175, 0, 175), cv2.FILLED)
    cv2.putText(img, final_text, (60, 430),
                cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    cv2.imshow("Virtual Keyboard", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
