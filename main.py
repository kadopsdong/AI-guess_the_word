from cgitb import text
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector  # benötigt Mediapipe
import numpy as np
from pynput.keyboard import Controller
import random
import string

webcamid = 0  # ist die Standard Kamera

cap = cv2.VideoCapture(webcamid)
cap.set(2, 50)  # Für die größe der Tastertur
cap.set(4, 1080)  # HD Auflösung

#Text einlesen
finalText = ""

#um Tastatureingaben nachzuahmen
keyboard = Controller()

# setup text
font = cv2.FONT_HERSHEY_SIMPLEX


#liest wörter aus txt-Datei, Wörter müssen mit ";" getrennt sein
with open("words.txt") as f:
    lines = f.readline()
    txtwordlist = lines.split(";")





#Wörter werden geshuffelt und mit random letters versehen
letterlist = []
for i, word in enumerate(txtwordlist):
    # es werden wörter gelöscht, die länger als 15 zeichen sind
    if len(word) >= 15:
        txtwordlist.pop(i)
        continue

    randletters = random.choices(string.ascii_lowercase, k= 15-len(word))
    letterlist.append(list(word) + randletters)
    random.shuffle(letterlist[i])


print(letterlist)


detector = HandDetector(detectionCon=0.8, maxHands=1)  # Hohe genauigkeit, um zu verhindern das random keys gedrückt werden, außerdem max 1 Hand

#Klasse erstellen für eine Liste aller Buchstaben
#nur einmal erstellen, da man keine Anderen Variablen Deklarieren muss
class Button():
    def __init__(self,pos, text, size=[85,85]): #initialzation Method
        self.pos = pos
        self.size = size
        self.text = text

    
    
#Hiermit wird das aktuelle wort gezeichnet
def drawbuttons(img, word):
    buttonlisttodraw = createbuttonwith(word)

    for button in buttonlisttodraw:
        x,y = button.pos #Positon
        w,h = button.size #Position
        cv2.rectangle(img,button.pos,(x+w,y+h),(255,0,255), cv2.FILLED) # Koordinaten + Farben
        cv2.putText(img,button.text ,(x+15,y+75), cv2.FONT_HERSHEY_PLAIN,5,(255,255,255), 5) #Anzeigen des Buchstaben im Rechteck

    return img

#buttons aus einem wort erstellen
def createbuttonwith(word):
    letterlist = list(word)
    buttonlist = []



    for i, buchstabe in enumerate(letterlist):
        x=100
        y=100
        if i < 5:
            buttonlist.append(Button([x*i,y], buchstabe))
        if 10 > i >= 5:
            buttonlist.append(Button([x * (i - 5), y*2], buchstabe))
        if 15 > i >= 10:
            buttonlist.append(Button([x * (i - 10), y * 3], buchstabe))

    return buttonlist




while True:
    # mit ESC kann abgebrochen werden
    success, img = cap.read() # Webcam auslesen
    hands, img = detector.findHands(img, draw=True, flipType=True) # Gibt die Position der Hände zurück

    img = drawbuttons(img, letterlist[3])

    #Zeigen der Handumrandung
    
    if hands:
        for button in letterlist: 
            x, y = button.pos
            w, h = button.size

            if x < hands[8][0] < x + w and y < hands[8][1] < y + h:
                cv2.rectangle(img, (x-5,y-5),(x+w+5, y+h+5),(175,0,175),cv2.FILLED)
                cv2.putText(img,button.text,(x+20,y+65),cv2.FONT_HERSHEY_PLAIN,4,(255,255,255),4)
                l,_,_ = detector.findDistance(8,12,img,draw=False)
                print (l)
                # l ist zum anzeigen der Fingerweite, kan mann dann abändern um die genauigkeit zu erhöhen

    #clicken mit der Hand fügt buchstabe in finalText ein, die 30 ist von l, der distanz
    if l < 30:
        keybord.press(letterlist.text)
        cv2.rectangle (img,button.pos, ((x+w,y+h),(0,255,0),cv2.FILLED))
        cv2.putText(img,button.text,(x+20,y+65), cv2.FONT_HERSHEY_PLAIN, 4, (255,255,255),4)
        finalText += button.text
        sleep(0.15)
   
    #Button erstellen mit opencv
    #cv2.rectangle(img,(100,100),(200,200),(255,0,255), cv2.FILLED) # Koordinaten + Farben
    #cv2.putText(img,"Q" ,(115,180), cv2.FONT_HERSHEY_PLAIN,5,(255,255,255), 5) #Anzeigen des Buchstaben im Rechteck

    cv2.imshow("image", img)




    if cv2.waitKey(5) & 0xFF == 27: #hexzahl für escape
        break


