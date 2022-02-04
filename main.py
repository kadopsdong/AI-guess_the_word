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

"""
Dieses Programm dient ist für Schüler kreiert, um Wörter erraten zu können

"""

"""
SETUP:
    -Wörter, welche abgefragt werden müssen in words.txt abgelegt werden
        - Buchstaben werden 1:1 übernommen (Großbuchstabe bleiben groß, Kleinbuchstaben bleiben klein)
            -Vorteil: -Der Anfangsbuchstabe kann so leichter gefunden werden
                      -Abkürzungen werden nicht verfälscht
        - Wörter können maximal 15 Zeichen lang sein, dies erleichtert die Suche
        - Wörter werden mit Zufälligen Buchstaben aufgefüllt (Sodass jedes Wort 15 Buchstaben enthält)

TODO:


"""

"""
Camera settings (1920x1080)
"""
WEBCAMID = 0  # ist die Standardkamera (Webcam)
LENGTHVIDEO = 1920
WIDEVIDEO = 1080

cap = cv2.VideoCapture(WEBCAMID)
cap.set(3, LENGTHVIDEO)
cap.set(4, WIDEVIDEO)

"""
GUI
"""


# for each letter take this button
class Button():
    def __init__(self, pos, text, size=[85, 85]):  # initialzation Method
        self.pos = pos
        self.size = size
        self.text = text


# setup text
font = cv2.FONT_HERSHEY_SIMPLEX

# position for skipbutton
XSKIP = 0
YSKIP = 400
WSKIP = 185
HSKIP = 85

# position for scoreboard
XSCORE = 900
YSCORE = 15
WSCORE = 350
HSCORE = 85

"""
Guessword Spiel variablen 
"""
counterOfWords = 0
FinalString = ""
points = 0

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


# Hiermit wird das aktuelle wort gezeichnet
def drawbuttons(img, word):
    buttonlisttodraw = createbuttonwith(word)

    for button in buttonlisttodraw:
        x, y = button.pos  # Positon
        w, h = button.size  # Größe startet bei 85,85
        cv2.rectangle(img, button.pos, (x + w, y + h), (175, 0, 175))  # Koordinaten + Farben
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


def createStaticOuputGUI():
    # Timer button
    cv2.rectangle(img, (10, 10), (10 + 330, 10 + 50), (255, 255, 0), cv2.FILLED)  # ASTRID bitte position hinzufuegen
    cv2.putText(img, "Zeit:" + str(used_time), (25, 55), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # Skip word button
    cv2.rectangle(img, (XSKIP, YSKIP), (XSKIP + WSKIP, YSKIP + HSKIP), (175, 175, 0), cv2.FILLED)
    cv2.putText(img, "Skip", (25, 470), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    # Score button
    cv2.rectangle(img, (XSCORE, YSCORE), (XSCORE + WSCORE, YSCORE + HSCORE), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, "Score:" + str(points), (910, 73), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

    return cv2





# imgBG = cv2.imread('strand.png')# Bild für den Hintergrund
segmentor = SelfiSegmentation()

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
    if FinalString == txtwordlist[counterOfWords]:
        counterOfWords += 1
        FinalString = ""
        start_time = time.time()
        points += 10

    if counterOfWords == len(txtwordlist):
        counterOfWords = 0
        start_time = time.time()

    # distanz der Finger wird gemessen

    img, buttons = drawbuttons(img, letterlist[counterOfWords])

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
                    points += 1
                    #deletes button if its correct
                    if FinalString == txtwordlist[counterOfWords][:len(FinalString)]:
                        img, buttons = drawbuttons(img, letterlist[counterOfWords].pop(i))


                # Es wird das wort geskippt
                if XSKIP < Xfinger < XSKIP + WSKIP and YSKIP < Yfinger < YSKIP + HSKIP and flanke == True:
                    counterOfWords += 1
                    FinalString = ""
                    points = points - 15
                    start_time = time.time()
                    print(points)

                    if counterOfWords == len(txtwordlist):
                        counterOfWords = 0
                    else:
                        break



    print(FinalString)
    durchgang = 0

    # drawdelButton() #button zum löschen wir hier mitgezeichnet
    # eingabe ist identisch mit lösung
    if FinalString == txtwordlist[counterOfWords][:len(FinalString)]:
        # rectangle bleibt grün
        # wenn buchstabe richtig

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
        points = points - 1

        # lezter Buchstabe wird verworfen
        FinalString = FinalString[:-1]

    # Button erstellen mit opencv
    # cv2.rectangle(img,(100,100),(200,200),(255,0,255), cv2.FILLED) # Koordinaten + Farben
    # cv2.putText(img,"Q" ,(115,180), cv2.FONT_HERSHEY_PLAIN,5,(255,255,255), 5) #Anzeigen des Buchstaben im Rechteck

    # Timer button
    used = time.time()
    used_time = used - start_time
    used_time = format(used_time, ".1f")


    createStaticOuputGUI()

    cv2.imshow("image", img)

    if cv2.waitKey(5) & 0xFF == 27:  # hexzahl für escape
        break
