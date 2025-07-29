import cv2
import mediapipe as mp
import pygetwindow as gw
import pyautogui
import pyttsx3
import time
import os

# Initialize modules
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.75)
engine = pyttsx3.init()
engine.setProperty('rate', 150)

last_action = None
cooldown_start = time.time()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def fingers_up(hand_landmarks):
    finger_tips = [8, 12, 16, 20]
    fingers = []

    # Thumb
    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def is_pinch(hand_landmarks):
    # Check if index finger and thumb are close together (pinch)
    x1 = hand_landmarks.landmark[8].x
    y1 = hand_landmarks.landmark[8].y
    x2 = hand_landmarks.landmark[4].x
    y2 = hand_landmarks.landmark[4].y
    distance = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    return distance < 0.05

def control_window(action):
    global last_action, cooldown_start
    current_time = time.time()

    if action != last_action or (current_time - cooldown_start > 3):
        try:
            win = gw.getWindowsWithTitle(gw.getActiveWindow().title)[0]

            if action == "minimize":
                win.minimize()
                speak("Window minimized")
            elif action == "maximize":
                win.maximize()
                speak("Window maximized")
            elif action == "close":
                win.close()
                speak("Window closed")
            elif action == "switch":
                pyautogui.hotkey('alt', 'tab')
                speak("Switching window")
            elif action == "launch_menu":
                speak("Opening app launcher")
                os.system("Chrome")  # or add a custom menu GUI

            last_action = action
            cooldown_start = current_time
        except:
            print("⚠️ No found")

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            fingers = fingers_up(hand_landmarks)
            count = fingers.count(1)

            # Gesture Recognition Logic
            if count == 1 and fingers[1] == 1:
                control_window("minimize")
            elif count == 2 and fingers[1] and fingers[2]:
                control_window("maximize")
            elif count == 5:
                control_window("close")
            elif count == 3 and fingers[1] and fingers[2] and fingers[3]:
                control_window("switch")
            elif is_pinch(hand_landmarks):
                control_window("launch_menu")

    cv2.imshow("AR Window Control Pro", img)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
