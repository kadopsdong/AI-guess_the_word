from asyncio import sleep
from cgitb import text
from typing import Final
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector  # benötigt Mediapipe
import numpy as np
from pynput.keyboard import Controller
import random
import string
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import time


webcamid = 0  # ist die Standard Kamera
FinalString = ""

cap = cv2.VideoCapture(webcamid)
cap.set(3, 1920)  # Für die größe der Tastertur
cap.set(4, 1080)  # HD Auflösung

# Postition für Skipbutton
xskip = 0
yskip = 400
wskip = 185
hskip = 85

# Position Scoreboard
xscore = 900
yscore = 15
wscore = 350
hscore = 85
Punkte = 0

# um Tastatureingaben nachzuahmen
keyboard = Controller()

# setup text
font = cv2.FONT_HERSHEY_SIMPLEX

# liest wörter aus txt-Datei, Wörter müssen mit ";" getrennt sein
with open("words.txt") as f:
    lines = f.readline()
    txtwordlist = lines.split(";")

# Wörter werden geshuffelt und mit random letters versehen
letterlist = []
for i, word in enumerate(txtwordlist):
    # es werden wörter gelöscht, die länger als 15 zeichen sind
    if len(word) >= 15:
        txtwordlist.pop(i)
        continue

    randletters = random.choices(string.ascii_lowercase, k=15 - len(word))
    letterlist.append(list(word) + randletters)
    random.shuffle(letterlist[i])

print(letterlist)

detector = HandDetector(detectionCon=0.8,
                        maxHands=1)  # Hohe genauigkeit, um zu verhindern das random keys gedrückt werden, außerdem max 1 Hand


# Klasse erstellen für eine Liste aller Buchstaben
# nur einmal erstellen, da man keine Anderen Variablen Deklarieren muss
class Button():
    def __init__(self, pos, text, size=[85, 85]):  # initialzation Method
        self.pos = pos
        self.size = size
        self.text = text


# Hiermit wird das aktuelle wort gezeichnet
def drawbuttons(img, word):
    buttonlisttodraw = createbuttonwith(word)

    for button in buttonlisttodraw:
        x, y = button.pos  # Positon
        w, h = button.size  # Größe startet bei 85,85
        cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)  # Koordinaten + Farben
        cv2.putText(img, button.text, (x + 15, y + 75), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255),
                    5)  # Anzeigen des Buchstaben im Rechteck

    return img, buttonlisttodraw


# buttons aus einem wort erstellen
def createbuttonwith(word):
    letterlist = list(word)
    buttonlist = []

    for i, buchstabe in enumerate(letterlist):
        x = 100
        y = 100
        if i < 5:
            buttonlist.append(Button([x * i, y], buchstabe))
        if 10 > i >= 5:
            buttonlist.append(Button([x * (i - 5), y * 2], buchstabe))
        if 15 > i >= 10:
            buttonlist.append(Button([x * (i - 10), y * 3], buchstabe))

    return buttonlist


# def drawdelButton():
# rectangle (imgage(x-Koordinate,Y-Koordinate vom oberen linken eck),(x-Koordinate,y-Koordinate vom unteren rechten eck), Farbe, dicke)
# cv2.rectangle(img,(5,600),(250,650),(255,0,255),cv2.FILLED)
#   cv2.putText(img,"<--",(300+25,300+25),cv2.FONT_HERSHEY_PLAIN, 5,(255,0,0),5)
#  return

#transpartente Buttons
def transparent_layout(img, word):
    imgNew = np.zeros_like(img, np.uint8)
    buttonlisttodraw = createbuttonwith(word)

    for button in buttonlisttodraw:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(imgNew, (button.pos[0], button.pos[1],
                                                   button.size[0],button.size[1]), 20 ,rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, button.text, (x + 15, y + 75), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255),
                    5)

    out = img.copy()
    alpaha = 0.5
    mask = imgNew.astype(bool)
    #print(mask.shape)
    out[mask] = cv2.addWeighted(img, alpaha, imgNew, 1-alpaha, 0)[mask]
    return out
# imgBG = cv2.imread('strand.png')# Bild für den Hintergrund
segmentor = SelfiSegmentation()
counterofwords = 0

start_time = time.time()
closed = False
while True:
    flanke = False
    # mit ESC kann abgebrochen werden
    success, img = cap.read()  # Webcam auslesen
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True, flipType=False)  # Gibt die Position der Hände zurück
    #    img = segmentor.removeBG(img, (100,255,0), threshold=0.3) #Beschränkt handerkennung zu sehr

    # Wenn wort erkannt wurde
    if FinalString == txtwordlist[counterofwords]:
        counterofwords += 1
        FinalString = ""
        start_time = time.time()
        Punkte += 10

    if counterofwords == len(txtwordlist):
        counterofwords = 0
        start_time = time.time()

    # distanz der Finger wird gemessen

    if hands:
        lmlist = hands[0]['lmList']
        length, _, img = detector.findDistance(lmlist[8], lmlist[12], img)
        Xfinger, Yfinger = lmlist[8]

        if length > 40 and closed == True:
            flanke = False
            closed = False
        # print("!FLANKE")

        if length < 40 and closed == False:
            flanke = True
            print(flanke)
            closed = True

        for i, button in enumerate(buttons):
            x, y = button.pos
            w, h = button.size

            if length < 60:
                # position von der Hand mit der Position des Buttons abgleichen
                # muss in der range x,y und w,h
                if x < Xfinger < x + w and y < Yfinger < y + h and flanke == True:
                    # click= False
                    cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (255, 0, 255), cv2.FILLED)
                    # if click == True:
                    FinalString += button.text
                    sleep(10)

                    # buttons.pop(i) #Button wird geloescht
                    #   click = False

                print(len(txtwordlist))

                # Es wird das wort geskippt
                if xskip < Xfinger < xskip + wskip and yskip < Yfinger < yskip + hskip and flanke == True:
                    counterofwords += 1
                    FinalString = ""
                    start_time = time.time()
                    Punkte = Punkte - 15

                    if counterofwords == len(txtwordlist):
                        counterofwords = 0

    sleep(1)

    print(FinalString)
    
    #img, buttons = drawbuttons(img, letterlist[counterofwords])
    img,buttons = transparent_layout(img, letterlist[counterofwords])
    # drawdelButton() #button zum löschen wir hier mitgezeichnet
    # eingabe ist identisch mit lösung
    if FinalString == txtwordlist[counterofwords][:len(FinalString)]:
        # rectangle bleibt grün
        # wenn buchstabe richtig
        if flanke == True:
            Punkte += 1

        cv2.rectangle(img, (75, 650), (800, 550), (0, 255, 0), cv2.FILLED)  # ASTRID
        # dann wird hier das rectangle beschrieben
        cv2.putText(img, FinalString, (87, 645), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255),
                    4)  # ASTRID Finalstring muss ausgegeben werden

    else:  # eingabe ist Fehlerhaft
        # rectangle wird rot
        cv2.rectangle(img, (100, 650), (800, 550), (0, 0, 255), cv2.FILLED)  # ASTRID
        # dann wird hier das rectangle beschrieben
        cv2.putText(img, FinalString, (87, 645), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255),
                    4)  # ASTRID Finalstring muss ausgegeben werden
        Punkte = Punkte - 1

        # lezter Buchstabe wird verworfen
        FinalString = FinalString[:-1]

    # Button erstellen mit opencv
    # cv2.rectangle(img,(100,100),(200,200),(255,0,255), cv2.FILLED) # Koordinaten + Farben
    # cv2.putText(img,"Q" ,(115,180), cv2.FONT_HERSHEY_PLAIN,5,(255,255,255), 5) #Anzeigen des Buchstaben im Rechteck

    # Timer button
    used = time.time()
    used_time = used - start_time
    used_time = format(used_time, ".1f")
    # print(used_time)

    cv2.rectangle(img, (10, 10), (10 + 330, 10 + 50), (255, 255, 0), cv2.FILLED)  # ASTRID bitte position hinzufuegen
    # dann wird hier das rectangle beschrieben
    cv2.putText(img, "Zeit:" + str(used_time), (25, 55), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # Skip word button
    cv2.rectangle(img, (xskip, yskip), (xskip + wskip, yskip + hskip), (175, 175, 0),
                  cv2.FILLED)  # ASTRID bitte position hinzufuegen
    # dann wird hier das rectangle beschrieben
    cv2.putText(img, "Skip", (25, 470), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # Score button
    cv2.rectangle(img, (xscore, yscore), (xscore + wscore, yscore + hscore), (0, 0, 0),
                  cv2.FILLED)  # ASTRID bitte position hinzufuegen
    # dann wird hier das rectangle beschrieben
    cv2.putText(img, "Score:" + str(Punkte), (910, 73), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    cv2.imshow("image", img)

    if cv2.waitKey(5) & 0xFF == 27:  # hexzahl für escape
        cv2.destroyAllWindows()
        break