import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
# link to the db
firebase_admin.initialize_app(cred,{'databaseURL': ''})
# refernce
ref = db.reference('students')

data = {
    "321654":
        {
            "name": "",
            "major":"",
            "starting_year":"",
            "total_attendance":"",
            "standing":"",
            "year":"",
            "last_attendance_time": ""
        },
    "852741":
        {
            "name": "",
            "major": "",
            "starting_year":"",
            "total_attendance":"",
            "standing": "",
            "year": "",
            "last_attendance_time": ""
        },
    "963852":
        {
            "name": "",
            "major": "",
            "starting_year":"",
            "total_attendance": "",
            "standing": "",
            "year": "",
            "last_attendance_time": ""
        }
}

for key, value in data.items():
    ref.child(key).set(value)