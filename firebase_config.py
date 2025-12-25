import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase using Streamlit Secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["FIREBASE"]))
    firebase_admin.initialize_app(cred)

# Create Firestore client
db = firestore.client()
