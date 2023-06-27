# importing modules
import cv2
import csv
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time

cap = cv2.VideoCapture(0) #camera
cap.set(3, 1080) #width
cap.set(4, 1000) #height
detector = HandDetector(detectionCon=0.8)

qNo = 0

# making a class for each question having q, choices and answer
class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None


    def updates(self, cursor, bboxs): #detecting which block is clicked
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] <x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv2.rectangle(img, (x1, y1),(x2, y2), (0, 255, 0), cv2.FILLED)

    def reset(self, cursor, reset, current_qNo): #detecting the reset click
        x1, y1, x2, y2 = reset
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
        if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
            return 0  # Return the updated value of qNo

        return current_qNo  # If reset button not pressed, return current value of qNo

#Importing the csv file data
pathCSV = "Mcqs.csv" #path of the file
with open(pathCSV, newline='\n') as f: #opening file as f
    reader = csv.reader(f) # using csv module we read it
    dataAll = list(reader)[1:]  # coverting the data in a list format and storing in data variable

qTotal = len(dataAll)

mcqList = [] #list of mcqs
for q in dataAll:
    mcqList.append(MCQ(q)) #filling the list

print(len(mcqList))

while True: #running the camera
    success, img = cap.read() #reading cap data
    img = cv2.flip(img, 1) #flipping the video
    img= cv2.resize(img, (1080, 720)) #resizing it

    hands,img = detector.findHands(img, flipType=False)

    if qNo < qTotal:
        mcq = mcqList[qNo] #selecting the question
        img, bbox = cvzone.putTextRect(img, mcq.question, [50, 50], 2, 2, offset=20, border=2) #question here
        img, bbox1 = cvzone.putTextRect(img, mcq.choice1, [150, 200], 2, 2, offset=30, border=2) #option1
        img, bbox2 = cvzone.putTextRect(img, mcq.choice2, [400, 200], 2, 2, offset=30, border=2) #option2
        img, bbox3 = cvzone.putTextRect(img, mcq.choice3, [150, 350], 2, 2, offset=30, border=2) #option3
        img, bbox4 = cvzone.putTextRect(img, mcq.choice4, [400, 350], 2, 2, offset=30, border=2) #option4

        if hands:
            lmList = hands[0]['lmList'] #list of points on the hand
            cursor = lmList[8] #defining cursor as index tip
            length, info = detector.findDistance(lmList[8], lmList[12]) #distance between index tip and middle tip
            if length < 60:
                mcq.updates(cursor, [bbox1, bbox2, bbox3, bbox4])
                print(mcq.userAns)
                if mcq.userAns is not None:
                    time.sleep(1.0)
                    qNo += 1

    else: #questions khtm ho gye
        score = 0;
        for mcq in mcqList:
            if mcq.answer == mcq.userAns:
                score+=1
        score = round((score/qTotal)*100, 2)
        img, _ = cvzone.putTextRect(img, "Quiz completed", [150, 150], 2,2, offset=20, border=2)
        img, _ = cvzone.putTextRect(img, f'Your Score: {score}%', [150, 250], 2,2, offset=20, border=2)
        img, reset = cvzone.putTextRect(img, "Reset", [150, 350], 2, 2, offset=20, border=2)
        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8]
            length, info = detector.findDistance(lmList[8], lmList[12])
            if length < 60:
                qNo = mcq.reset(cursor, reset, qNo)
                time.sleep(1.0)

    #draw progress bar
    barValue = 150 + (750 // qTotal) * qNo
    cv2.rectangle(img, (150, 600), (barValue, 650), (0,255,0), cv2.FILLED)
    cv2.rectangle(img, (150, 600), (900, 650), (255, 0, 255), 5)
    img, _ = cvzone.putTextRect(img, f'{round((qNo/qTotal)*100)}%', [925, 635], 2, 2, offset=16)

    cv2.imshow("Img", img) #Showing the data
    cv2.waitKey(1) #after a wait of 1 sec