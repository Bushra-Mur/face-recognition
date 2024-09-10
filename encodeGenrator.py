import cv2
import face_recognition
import pickle
import os
import numpy as np
from face_recognition import face_encodings
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from firebase_admin.storage import bucket

cred = credentials.Certificate("serviceAccountKey.json")
# link to the db
firebase_admin.initialize_app(cred,{'databaseURL': ''
                                    ,'storageBucket': ''
                                    })


# from main import imgModeList

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
# print(pathList)
imgList = []
studentIds = []
# import imgs
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # split the ids from png
    studentIds.append(os.path.splitext(path)[0])
#     upload to db
    fileNames = f'{folderPath}/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(fileNames)
    blob.upload_from_filename(fileNames)


# print(studentIds)

# encode imgs
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        # convert to rgb color
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList
encodeListKnown = findEncodings(imgList)
# save each ID to their encoding
encodeListKnownWithIds=[encodeListKnown, studentIds]

file = open("encodes.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()