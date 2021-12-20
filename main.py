import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector  # benötigt Mediapipe

webcamid = 0  # ist die Standard Kamera

cap = cv2.VideoCapture(webcamid)
cap.set(2, 1280)  # Für die größe der Tastertur
cap.set(4, 720)  # HD Auflösung

# setup text
font = cv2.FONT_HERSHEY_SIMPLEX



detector = HandDetector(detectionCon=0.8)  # Hohe genauigkeit, um zu verhindern das random keys gedrückt werden

while True:
    # mit ESC kann abgebrochen werden
    success, img = cap.read() # Webcam auslesen
    hands, img = detector.findHands(img, draw=True)  # Gibt die Position der Hände zurück

    #Button erstelen mit opencv
    cv2.rectangle(img,(100,100),(200,200),(255,0,255), cv2.FILLED) # Koordinaten + Farben
    cv2.putText(img, ()) ##HIER WEITERMACHEN

    cv2.imshow("image", img)
    cv2.waitKey(1)
