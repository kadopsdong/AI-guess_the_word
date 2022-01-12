import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector  # benötigt Mediapipe
import numpy as np
from pynput.keyboard import Controller

webcamid = 0  # ist die Standard Kamera

cap = cv2.VideoCapture(webcamid)
cap.set(2, 1280)  # Für die größe der Tastertur
cap.set(4, 720)  # HD Auflösung

# setup text
font = cv2.FONT_HERSHEY_SIMPLEX



detector = HandDetector(detectionCon=0.8)  # Hohe genauigkeit, um zu verhindern das random keys gedrückt werden

#Klasse erstellen für eine Liste aller Buchstaben
#nur einmal erstellen, da man keine Anderen Variablen Deklarieren muss
class Button():
    def __init__(self,pos, text, size=[85,85]): #initialzation Method
        self.pos = pos
        self.size = size
        self.text = text

    def draw(self,img):
        x,y = self.pos #Minute 19:45 versteh ich auch nicht so ganz :D
        w,h = self.size
        cv2.rectangle(img,self.pos,(x+w,y+h),(255,0,255), cv2.FILLED) # Koordinaten + Farben
        cv2.putText(img,self.text ,(x+15,y+75), cv2.FONT_HERSHEY_PLAIN,5,(255,255,255), 5) #Anzeigen des Buchstaben im Rechteck
    
    
    
#neue Methode zum zeichnen des Rechtecks in dem die Buchstaben drinstehen
#muss nur einmal erstellt werden 
myButton = Button([100,100],"Q") # erstellen des Objektes
    

while True:
    # mit ESC kann abgebrochen werden
    success, img = cap.read() # Webcam auslesen
    hands, img = detector.findHands(img, draw=True)  # Gibt die Position der Hände zurück

    myButton.draw(img)
   
    #Button erstellen mit opencv
    #cv2.rectangle(img,(100,100),(200,200),(255,0,255), cv2.FILLED) # Koordinaten + Farben
    #cv2.putText(img,"Q" ,(115,180), cv2.FONT_HERSHEY_PLAIN,5,(255,255,255), 5) #Anzeigen des Buchstaben im Rechteck

    cv2.imshow("image", img)
    if cv2.waitKey(5) & 0xFF == 27: #hexzahl für escape
        break



    #bis Minute 22:19 geschaut