import pyrebase

# Firebase configuration
firebaseConfig = {
    "apiKey": "foo_bar",
    "authDomain": "devfest2025-d141d.firebaseapp.com",
    "projectId": "devfest2025-d141d",
    "storageBucket": "devfest2025-d141d.firebasestorage.app",
    "messagingSenderId": "802022613328",
    "appId": "1:802022613328:web:ec652e17e0b48f56bd4c55",
    "measurementId": "G-LHNWG2GW1H",
    "databaseURL": "https://devfest2025-d141d-default-rtdb.firebaseio.com/",
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
