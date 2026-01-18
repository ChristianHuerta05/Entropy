import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

db = None

def initialize_firebase():
    global db
    try:
        if not firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

def log_to_db(run_id: str, message: str, type: str = "info"):
    global db
    if not db:
        print(f"[{type}] {message} (Firebase not serving)")
        return

    try:
        doc_ref = db.collection("runs").document(run_id)
        doc_ref.set({
            "logs": firestore.ArrayUnion([{
                "timestamp": datetime.datetime.now().isoformat(),
                "message": message,
                "type": type
            }])
        }, merge=True)
    except Exception as e:
        print(f"Failed to log to Firestore: {e}")
