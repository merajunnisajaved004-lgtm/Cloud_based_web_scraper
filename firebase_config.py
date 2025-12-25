import firebase_admin
from firebase_admin import credentials, firestore

# Load your Service Account Key
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Create Firestore client
db = firestore.client()
