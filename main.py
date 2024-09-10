import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
from numpy.ma.core import array

from encodeGenrator import bucket
if not firebase_admin._apps:
   cred = credentials.Certificate("serviceAccountKey.json")
# link to the db
   firebase_admin.initialize_app(cred,{'databaseURL': "",
    'storageBucket': ""
})

bucket = storage.bucket()


cap=cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4,480)


# import graphics
imgBackground = cv2.imread('Resources/background.png')

# impoort modes to the list
folderModePath= 'Resources/Modes'
modePathList =os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

# load encoding file
file=open('encodes.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
# extract to two parts
encodeListKnown , studentIds = encodeListKnownWithIds

modeType=0
counter = 0
id = -1
imgStudent=[]

# display
while True:
    success, img=cap.read()
    # make image smaller to compute easier
    imgS= cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # fill in the value to the face recognition system
    # faces in the current frame list
    faceCureFrame=face_recognition.face_locations(imgS)
    # the encodings list
    encodeCurFrame=face_recognition.face_encodings(imgS,faceCureFrame)
    # overlay the webcam on background
    imgBackground[162:162+480 , 55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCureFrame:

      for encodeFace, faceLoc in zip(encodeCurFrame,faceCureFrame):
         # will compare it to every picture and decide if its true or false to each photo
          matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
        # shows how similar the photo is with the saved pic
          faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # to test print("Distance", faceDis)
        # to test print("matches", matches)
          matchIndex = np.argmin(faceDis)

          if matches[matchIndex]:
            # print("found")
            # print the ID of the match person
            # print(studentIds[matchIndex])

            # making box around the face
              y1, x2, y2, x1 = faceLoc
              y1, x2, y2, x1 =y1*4, x2*4, y2*4, x1*4
              bbox = 55+x1 , 162+y1 , x2 - x1 , y2 - y1
              imgBackground= cvzone.cornerRect(imgBackground, bbox, rt=0)
            # to give the id of the student that matched
              id = studentIds[matchIndex]
              if counter == 0 :
                  cvzone.putTextRect(imgBackground, "LOADING..",(275,400))
                  cv2.imshow("face", imgBackground)
                  cv2.waitKey(1)
                  counter = 1
                  modeType=1
      if counter != 0 :
          if counter == 1:
    #     download the data of the person
              studentInfo = db.reference(f'students/{id}').get()
              # print(studentInfo)
              blob = bucket.get_blob(f'Images/{id}.png')
              array = np.frombuffer(blob.download_as_string() , dtype=np.uint8)
              imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2RGB)

        #     update data
              datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
              secondsElapsed=(datetime.now()-datetimeObject).total_seconds()
              # print(secondsElapsed)
              if secondsElapsed >30 :
                 ref = db.reference(f'students/{id}')
                 studentInfo['total_attendance']+=1
                 ref.child('total_attendance').set(studentInfo['total_attendance'])
              # change last att time
                 ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
              else:
                  modeType = 3
                  counter = 0
                  imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

          if modeType != 3 :

            if 10<counter<20 :
                modeType=2
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if counter <=10:
                cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

          # center the name
                (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                offset = (414 - w) // 2
                cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)
                imgBackground[175:175+216 , 909:909+216] = imgStudent

            counter += 1

        # to reset
            if counter>=20 :
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else :
        modeType = 0
        counter = 0

    cv2.imshow("webcam", img)
    cv2.imshow("face", imgBackground)
    cv2.waitKey(1)