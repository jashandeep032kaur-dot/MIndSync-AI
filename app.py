import streamlit as st
import json, os, faiss, bcrypt, datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import cv2
import pyttsx3
import threading
import tempfile
from PIL import Image
import speech_recognition as sr
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import time
import os,datetime
  #  import speech_recognition as sr
from deepface import DeepFace
# the two phases are imported here 
import phase2_enhancements as phase2
import phase3_intervention as phase3

from _virtual_chat import virtual_chat_mode
from _virtual_chat import virtual_chat_mode, save_session_to_mongo
from enhanced_rag_system import EnhancedRAGSystem, get_enhanced_response
from chatbot_reponses import get_response, detect_emotion_from_text
# ==================== ENHANCED REMINDER SYSTEM ====================
# Add this code to your main app (after your imports and before main())

import datetime
import streamlit as st
from db import get_db

# ==================== Streamlit Page ====================
st.set_page_config(
    page_title="MindSync AI ⭐",
    page_icon="🌈",
    layout="wide"
)

# ==================== Database ====================
db = get_db()


# ==================== MENTAL HEALTH CONDITIONS ====================
MENTAL_HEALTH_CONDITIONS = {
    "anxiety": {
        "name": "Anxiety Disorders",
        "icon": "😰",
        "color": "#FF6B6B",
        "description": "Excessive worry, fear, or nervousness that interferes with daily activities.",
        "symptoms": [
            "Persistent worrying or anxiety",
            "Restlessness or feeling on edge",
            "Difficulty concentrating",
            "Muscle tension",
            "Sleep disturbances",
            "Rapid heartbeat or sweating",
            "Avoiding situations that trigger anxiety"
        ],
        "types": [
            "Generalized Anxiety Disorder (GAD)",
            "Social Anxiety Disorder",
            "Panic Disorder",
            "Specific Phobias",
            "Separation Anxiety"
        ],
        "non_medical_interventions": {
            "breathing_techniques": {
                "title": "Breathing & Relaxation",
                "exercises": [
                    {
                        "name": "4-7-8 Breathing",
                        "description": "Inhale for 4 seconds, hold for 7, exhale for 8",
                        "duration": "5-10 minutes",
                        "best_for": "Quick calm during panic"
                    },
                    {
                        "name": "Box Breathing",
                        "description": "Inhale 4s → Hold 4s → Exhale 4s → Hold 4s",
                        "duration": "5 minutes",
                        "best_for": "Pre-stressful situations"
                    }
                ]
            }
        },
        "when_to_seek_help": [
            "Anxiety interferes with work, school, or relationships",
            "You avoid many situations due to anxiety",
            "Physical symptoms are severe (chest pain, dizziness)"
        ],
        "success_stories": [
            "Sarah, 28: 'I used the exposure hierarchy to overcome my social anxiety. Started with ordering coffee, now I give presentations at work!'"
        ]
    },
    "depression": {
        "name": "Depression",
        "icon": "😔",
        "color": "#4A90E2",
        "description": "Persistent feelings of sadness, hopelessness, and loss of interest in activities.",
        "symptoms": [
            "Persistent sad, empty, or hopeless mood",
            "Loss of interest in activities once enjoyed",
            "Changes in appetite or weight",
            "Sleep problems (too much or too little)",
            "Fatigue or loss of energy"
        ],
        "types": [
            "Major Depressive Disorder",
            "Persistent Depressive Disorder (Dysthymia)",
            "Seasonal Affective Disorder (SAD)"
        ],
        "non_medical_interventions": {
            "behavioral_activation": {
                "title": "Behavioral Activation",
                "exercises": [
                    {
                        "name": "Activity Scheduling",
                        "description": "Plan pleasurable and meaningful activities daily"
                    }
                ]
            }
        },
        "when_to_seek_help": [
            "Thoughts of suicide or self-harm",
            "Unable to function in daily life"
        ],
        "success_stories": [
            "Priya, 31: 'Behavioral activation saved me. I forced myself to do one thing daily.'"
        ]
    },
    "stress": {
        "name": "Chronic Stress",
        "icon": "😫",
        "color": "#F39C12",
        "description": "Prolonged physical and emotional strain that can lead to burnout.",
        "symptoms": [
            "Feeling overwhelmed or unable to cope",
            "Irritability or mood swings",
            "Difficulty relaxing or 'switching off'"
        ],
        "types": [
            "Work-Related Stress",
            "Academic Stress",
            "Financial Stress"
        ],
        "non_medical_interventions": {
            "stress_management": {
                "title": "Immediate Stress Relief",
                "techniques": [
                    {
                        "name": "STOP Technique",
                        "steps": [
                            "S - Stop what you're doing",
                            "T - Take a breath (3 deep breaths)",
                            "O - Observe your thoughts, feelings",
                            "P - Proceed mindfully"
                        ]
                    }
                ]
            }
        },
        "when_to_seek_help": [
            "Physical health declining",
            "Burnout symptoms"
        ],
        "success_stories": [
            "David, 38: 'Implementing time blocking reduced my stress by 70%.'"
        ]
    }
}

# ==================== ASSESSMENT QUESTIONS (15 each) ====================
ASSESSMENT_QUESTIONS = {
    "anxiety": [
        {"question": "Over the last 2 weeks, how often have you felt nervous, anxious, or on edge?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you been unable to stop or control worrying?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you been worrying too much about different things?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had trouble relaxing?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you been so restless that it's hard to sit still?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you become easily annoyed or irritable?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt afraid as if something awful might happen?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you experienced heart racing or pounding?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had trouble concentrating on things?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you experienced muscle tension or soreness?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you avoided situations because they make you anxious?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had difficulty sleeping due to worry?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt like you're losing control?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you experienced sweating or trembling?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had intrusive worrying thoughts?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]}
    ],
    "depression": [
        {"question": "Over the last 2 weeks, how often have you had little interest or pleasure in doing things?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt down, depressed, or hopeless?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had trouble falling or staying asleep?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt tired or had little energy?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had poor appetite or been overeating?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt bad about yourself or that you're a failure?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had trouble concentrating on things?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you moved or spoken so slowly that others noticed?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you thought you would be better off dead?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt isolated or withdrawn from others?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you experienced unexplained crying spells?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt worthless or excessively guilty?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you lost interest in activities you used to enjoy?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you had difficulty making decisions?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]},
        {"question": "How often have you felt like life isn't worth living?", "options": ["Not at all", "Several days", "More than half the days", "Nearly every day"], "scores": [0, 1, 2, 3]}
    ],
    "stress": [
        {"question": "In the last month, how often have you felt unable to control important things in your life?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt difficulties were piling up so high you could not overcome them?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you been upset because of something unexpected?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt nervous and stressed?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt confident about handling personal problems?", "options": ["Very often", "Fairly often", "Sometimes", "Almost never", "Never"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt things were going your way?", "options": ["Very often", "Fairly often", "Sometimes", "Almost never", "Never"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you found yourself unable to cope with all the things you had to do?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you been able to control irritations in your life?", "options": ["Very often", "Fairly often", "Sometimes", "Almost never", "Never"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt on top of things?", "options": ["Very often", "Fairly often", "Sometimes", "Almost never", "Never"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you been angered by things outside your control?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt overwhelmed by your responsibilities?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had trouble relaxing?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you experienced physical symptoms of stress (headaches, stomach issues)?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt like you're constantly racing against time?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had difficulty sleeping due to stress?", "options": ["Never", "Almost never", "Sometimes", "Fairly often", "Very often"], "scores": [0, 1, 2, 3, 4]}
    ],
    "ptsd": [
        {"question": "How often have you had unwanted upsetting memories of the traumatic event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had nightmares about the traumatic event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt as if the traumatic event was happening again?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt very upset when reminded of the traumatic event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had strong physical reactions when reminded of the event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you avoided memories, thoughts, or feelings about the event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you avoided external reminders of the traumatic event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had trouble remembering important parts of the event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had strong negative beliefs about yourself or the world?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you blamed yourself for the traumatic event?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you had strong negative feelings (fear, horror, anger, guilt, shame)?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you lost interest in activities you used to enjoy?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you felt distant or cut off from other people?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you been irritable or aggressive?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often have you been overly alert or on guard?", "options": ["Not at all", "A little bit", "Moderately", "Quite a bit", "Extremely"], "scores": [0, 1, 2, 3, 4]}
    ],
    "insomnia": [
        {"question": "How often do you have difficulty falling asleep?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you wake up during the night?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you wake up too early and can't go back to sleep?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How satisfied are you with your current sleep pattern?", "options": ["Very satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very dissatisfied"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How noticeable is your sleep problem to others?", "options": ["Not noticeable", "Barely noticeable", "Somewhat noticeable", "Very noticeable", "Extremely noticeable"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How worried are you about your sleep problem?", "options": ["Not worried", "A little worried", "Somewhat worried", "Very worried", "Extremely worried"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How much does your sleep problem interfere with daily functioning?", "options": ["Not at all", "A little", "Somewhat", "Much", "Very much"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you feel tired during the day?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you use sleep medication or aids?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you have difficulty concentrating due to lack of sleep?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you feel irritable due to poor sleep?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often does lack of sleep affect your mood?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you worry about not being able to sleep?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often do you feel unrefreshed after sleep?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]},
        {"question": "How often does poor sleep affect your work or social life?", "options": ["Never", "Rarely", "Sometimes", "Often", "Always"], "scores": [0, 1, 2, 3, 4]}
    ]
}

# ==================== DeepFace Check ====================
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

# ==================== Database / RAG ====================
    
@st.cache_resource
def load_emotion_model():
    return pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

@st.cache_resource
def init_enhanced_rag():
    return EnhancedRAGSystem(rag_directory="rag_knowledges")

#embedder, index, rag_inputs, rag_outputs = load_rag()
emotion_classifier = load_emotion_model()
enhanced_rag= init_enhanced_rag()
#users_col, sessions_col, assessments_col = db["users"], db["sessions"], db["assessments"]
users_col, sessions_col, assessments_col = db["users"], db["sessions"], db["assessments"]
reminders_col = db["reminders"] 
CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "i want to die", "self harm","i don't want to live","i can't go on"]


# Initialize RAG
enhanced_rag = init_enhanced_rag()
# ==================== TTS Engine ====================
class TTSEngine:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            self.available = True
        except:
            self.available = False
    
    def speak(self, text):
        if not self.available: 
            return
        threading.Thread(target=lambda: self.engine.say(text) or self.engine.runAndWait(), daemon=True).start()

tts_engine = TTSEngine()

# ==================== Helpers ====================
def create_user(u, p,gender=None):
    if users_col.find_one({"username": u}): 
        return False
    hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt())
    users_col.insert_one({"username": u, "password": hashed,"gender": gender, "created_at": datetime.datetime.utcnow()})
    return True

def verify_user(u, p):
    user = users_col.find_one({"username": u})
    return bcrypt.checkpw(p.encode(), user["password"]) if user else False


def detect_text_emotion(text):
    """
    Enhanced emotion detection - tries custom detection first, 
    then falls back to transformer model
    """
    # Try custom keyword-based detection first (faster)
    emotion, confidence = detect_emotion_from_text(text)
    
    if confidence > 0.8:
        return emotion, confidence
    
    # Fallback to transformer model for uncertain cases
    try:
        res = emotion_classifier(text)[0]
        best_emotion = max(res, key=lambda x: x["score"])
        return best_emotion["label"], best_emotion["score"]
    except:
        return emotion, confidence


# def retrieve_answer(query, emotion=None):
#     """Enhanced RAG retrieval with emotion-aware responses and motivational content"""
    
#     # First try RAG knowledge base
#     if rag_inputs and index is not None:
#         try:
#             q_emb = embedder.encode([query], convert_to_numpy=True)
#             distances, indices = index.search(q_emb, 3)  # Get top 3 matches
            
#             # Get the best match
#             best_match_idx = indices[0][0]
#             best_distance = distances[0][0]
            
#             # If distance is reasonable (similar enough), use RAG response
#             if best_distance < 1.5:  # Threshold for similarity
#                 base_response = rag_outputs[best_match_idx]
                
#                 # Enhance with emotion-specific motivation
#                 enhanced_response = enhance_response_with_motivation(base_response, emotion, query)
#                 return enhanced_response
#         except:
#             pass
    
#     # Fallback: Generate contextual response based on emotion and keywords
#     return generate_contextual_response(query, emotion)



def retrieve_answer(user_input, emotion):
    """
    Enhanced retrieval that combines RAG + contextual responses
    Priority: RAG knowledge base → Contextual responses
    """
    # Try RAG knowledge base first
    rag_result = enhanced_rag.retrieve_response(user_input, emotion, top_k=3)
    
    if rag_result and rag_result['confidence'] > 0.65:
        # Good match from RAG - use it
        return rag_result['combined']
    
    # Fallback to contextual responses
    return get_response(user_input, emotion)

def get_severity_level(condition, score, max_score):
    """Determine severity level based on score"""
    percentage = (score / max_score) * 100
    
    if percentage <= 33:
        return "Minimal"
    elif percentage <= 66:
        return "Moderate"
    else:
        return "Severe"

EMOJI_MAP = {"joy":"😊","sadness":"😢","anger":"😠","fear":"😰","surprise":"😲","neutral":"😐"}

# ==================== Session State ====================
if 'authenticated' not in st.session_state: 
    st.session_state.authenticated = False
#if 'username' not in st.session_state: 
    #st.session_state.username = None
if "username" not in st.session_state:
    st.session_state.username = "guest"
if 'chat_history' not in st.session_state: 
    st.session_state.chat_history = []
if 'virtual_chat_history' not in st.session_state: 
    st.session_state.virtual_chat_history = []
if "gender" not in st.session_state:
    st.session_state.gender = None  # Will be set after login

# ==================== Authentication Page ====================
def auth_page():
    st.title("🧠 Welcome to MindSync AI")
    st.subheader("Login / Register")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        u = st.text_input("Username", key="auth_user")
        p = st.text_input("Password", type="password", key="auth_pass")
        if st.button("Login"):
            if verify_user(u, p): 
                st.session_state.authenticated = True
                st.session_state.username = u
                user_data = users_col.find_one({"username": u})
                st.session_state.gender = user_data.get("gender", "👤")  # Default if not stored

                st.success(f"Welcome back! {st.session_state.gender} {st.session_state.username}")
                if st.session_state.gender is None:
                    st.session_state.gender = st.radio("Select your gender:", ["👨 Male", "👩 Female"])
                st.rerun()
            else: 
                st.error("Invalid credentials")
    
    with tab2:
        ru = st.text_input("New Username", key="reg_user")
        rp = st.text_input("New Password", type="password", key="reg_pass")
        rpp = st.text_input("Confirm Password", type="password", key="reg_pass2")
        gender = st.radio("Select your gender:", ["👨 Male", "👩 Female"])
        if st.button("Register"):
            if rp != rpp: 
                st.error("Passwords don't match")
            elif create_user(ru, rp): 
                st.success("Registered! Please login now.")
            else: 
                st.error("Username already exists")
# ==================== Reminder System ====================
# Initialize reminder tracking in session state
if 'last_reminder_check' not in st.session_state:
    st.session_state.last_reminder_check = datetime.datetime.now() - datetime.timedelta(minutes=10)
if 'shown_reminders' not in st.session_state:
    st.session_state.shown_reminders = set()
if 'reminder_dismiss' not in st.session_state:
    st.session_state.reminder_dismiss = {}

def show_pending_reminders(username):
    """Show pending reminders as sidebar notifications"""
    now = datetime.datetime.now()
    
    # Only check every 5 minutes
    time_since_check = (now - st.session_state.last_reminder_check).seconds
    if time_since_check < 300:
        return
    
    st.session_state.last_reminder_check = now
    
    try:
        active_reminders = list(reminders_col.find({"username": username, "enabled": True}))
    except:
        return
    
    if not active_reminders:
        return
    
    current_hour = now.hour
    current_minute = now.minute
    current_time_str = f"{current_hour}:{current_minute:02d}"
    reminders_shown = []
    
    for reminder in active_reminders:
        reminder_type = reminder.get('type')
        reminder_id = f"{reminder_type}_{current_time_str}"
        
        if reminder_id in st.session_state.shown_reminders:
            continue
        
        dismiss_until = st.session_state.reminder_dismiss.get(reminder_id)
        if dismiss_until and now < dismiss_until:
            continue
        
        if reminder_type == "checkin":
            reminder_time = reminder.get('time', '20:00')
            r_hour, r_minute = map(int, reminder_time.split(':'))
            
            if r_hour == current_hour and abs(r_minute - current_minute) <= 5:
                reminders_shown.append({
                    'id': reminder_id,
                    'title': '🔔 Mood Check-in Reminder',
                    'message': 'Time to log your mood! Head to Mood Journal.',
                    'color': 'warning'
                })
        
        elif reminder_type == "breathing":
            frequency = reminder.get('frequency', 'Every 4 hours')
            should_show = False
            
            if frequency == "Every 2 hours":
                should_show = current_hour % 2 == 0 and current_minute < 5
            elif frequency == "Every 4 hours":
                should_show = current_hour % 4 == 0 and current_minute < 5
            elif frequency == "Twice daily":
                should_show = current_hour in [9, 18] and current_minute < 5
            
            if should_show:
                reminders_shown.append({
                    'id': reminder_id,
                    'title': '🌬️ Breathing Exercise Reminder',
                    'message': 'Take 2 minutes for a breathing break!',
                    'color': 'info'
                })
        
        elif reminder_type == "goal":
            frequency = reminder.get('frequency', 'Daily')
            should_show = False
            
            if frequency == "Daily":
                should_show = current_hour == 9 and current_minute < 5
            elif frequency == "Every 3 days":
                day_of_year = now.timetuple().tm_yday
                should_show = day_of_year % 3 == 0 and current_hour == 9 and current_minute < 5
            elif frequency == "Weekly":
                should_show = now.weekday() == 0 and current_hour == 9 and current_minute < 5
            
            if should_show:
                reminders_shown.append({
                    'id': reminder_id,
                    'title': '🎯 Goal Progress Check',
                    'message': 'Review your wellness goals today!',
                    'color': 'success'
                })
    
    if reminders_shown:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔔 Reminders")
        
        for reminder in reminders_shown:
            st.session_state.shown_reminders.add(reminder['id'])
            
            if reminder['color'] == 'warning':
                st.sidebar.warning(f"**{reminder['title']}**")
            elif reminder['color'] == 'info':
                st.sidebar.info(f"**{reminder['title']}**")
            elif reminder['color'] == 'success':
                st.sidebar.success(f"**{reminder['title']}**")
            
            st.sidebar.caption(reminder['message'])
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.sidebar.button("✓ Got it", key=f"dismiss_{reminder['id']}", use_container_width=True):
                    st.rerun()
            with col2:
                if st.sidebar.button("⏰ Snooze", key=f"snooze_{reminder['id']}", use_container_width=True):
                    st.session_state.reminder_dismiss[reminder['id']] = now + datetime.timedelta(minutes=30)
                    st.rerun()
            
            st.sidebar.markdown("---")

def clear_old_reminders():
    """Clear reminder tracking daily"""
    now = datetime.datetime.now()
    
    if 'last_reminder_reset' not in st.session_state:
        st.session_state.last_reminder_reset = now.date()
    
    if st.session_state.last_reminder_reset < now.date():
        st.session_state.shown_reminders = set()
        st.session_state.reminder_dismiss = {}
        st.session_state.last_reminder_reset = now.date()


def detect_text_emotion(text: str):
    """Detect emotion from text based on keywords in generate_contextual_response"""
    text = text.lower()
    
    # Match keywords to emotion
    if any(word in text for word in ["happy", "joy", "excited", "happiness", "amazing", "awesome"]):
        return "joy", 0.9
    elif any(word in text for word in ["sad", "sadness", "down", "cry", "tired"]):
        return "sadness", 0.9
    elif any(word in text for word in ["angry", "frustrated", "mad", "furious"]):
        return "anger", 0.9
    elif any(word in text for word in ["fear", "afraid", "scared", "panic"]):
        return "fear", 0.9
    elif any(word in text for word in ["surprise", "amazed", "wow", "shocked"]):
        return "surprise", 0.9
    else:
        return "neutral", 0.5

# ==================== NOW UPDATE YOUR chat_page() FUNCTION ====================

def chat_page():
    if st.session_state.authenticated:
        clear_old_reminders()
        show_pending_reminders(st.session_state.username)

    # Sidebar
    with st.sidebar:
        #st.title(f"👤 {st.session_state.username}")
        user_emoji = st.session_state.get("gender", "👤")
        st.title(f"{st.session_state.gender} {st.session_state.username}")

        st.markdown("---")
        
        # Radio selection
        selected_page = st.radio("📍 Navigate", [
            "💬 Chat",
            "🎥 Virtual Chat",
            "📊 Analytics", 
            "ℹ️ Resources",
            # Phase 2
            "🗓️ Mood Journal",
            "🎯 Goals",
            "📚 Exercises",
            "🏆 Achievements",
            "🔔 Reminders",
            # Phase 3
            "🎯 Coping Plans",
            "📚 Resource Library",
            "🎮 Interactive Tools"
        ])

        # Update session_state when selection changes
        st.session_state.page = selected_page

        if st.button("Logout"): 
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.chat_history = []
            st.session_state.gender = None
            st.session_state.virtual_chat_history = []
            st.rerun()

    # ------------------ Page Routing ------------------
    page = st.session_state.page  # always get latest selection

    # Phase 3
    if page in ["🎯 Coping Plans", "📚 Resource Library", "🎮 Interactive Tools"]:
        phase3.phase3_main(st.session_state.username, page)

    # Phase 2
    elif page in ["🗓️ Mood Journal", "🎯 Goals", "📚 Exercises", 
                  "🏆 Achievements", "🔔 Reminders"]:
        phase2.phase2_main(st.session_state.username, page)

    # Other pages
    elif page == "💬 Chat":
        chat_interface()
    elif page == "🎥 Virtual Chat":
        #virtual_chat_mode(st.session_state.username,detect_text_emotion_func=detect_text_emotion)
        virtual_chat_mode(
            username=st.session_state.username,
            detect_text_emotion_func=detect_text_emotion,
            retrieve_answer_func=retrieve_answer  # Added this line
        )

    elif page == "📊 Analytics":
        analytics_page()
    elif page == "ℹ️ Resources":
        resources_page()

# ==================== Text Chat ====================
def chat_interface():
    st.title("💬 Text Chat")
    
    for m in st.session_state.chat_history:
        with st.chat_message(m['role']):
            st.markdown(m['content'])
            if 'emotion' in m and m['role'] == 'assistant':
                st.caption(f"Detected emotion: {EMOJI_MAP.get(m['emotion'], '😐')} {m['emotion']}")
    
    user_input = st.chat_input("Type your message here...")
    if user_input:
        text_emotion, _ = detect_text_emotion(user_input)
        is_crisis = any(k in user_input.lower() for k in CRISIS_KEYWORDS)
        
        if is_crisis:
            bot_reply = """⚠️ I'm deeply concerned about what you're sharing. Your life matters.

🆘 **Please reach out immediately**:
- AASRA: 91-22-27546669 (24/7)
- Vandrevala Foundation: 1860-2662-345 (24/7)
- iCall: 022-25521111

You don't have to face this alone. These helplines have trained counselors ready to listen and support you right now.

Please also tell someone you trust - a family member, friend, or colleague. You matter more than you know. 💙"""
        else:
            # Use enhanced retrieval with emotion awareness
            bot_reply = retrieve_answer(user_input, text_emotion)
        
        sessions_col.insert_one({
            "username": st.session_state.username,
            "user_text": user_input,
            "bot_text": bot_reply,
            "emotion": text_emotion,
            "timestamp": datetime.datetime.utcnow()
        })
        
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        st.session_state.chat_history.append({'role': 'assistant', 'content': bot_reply, 'emotion': text_emotion})
        st.rerun()

# ==================== Virtual Chat with Face Emotion ====================

# ==================== Analytics Page ====================
def analytics_page():
    st.title("📊 Analytics Dashboard")
    username = st.session_state.username
    
    # Tabs for different analytics
    tab1, tab2, tab3 = st.tabs(["💬 Chat Analytics", "📝 Assessment Reports", "📈 Combined Insights"])
    
    # ==================== TAB 1: CHAT ANALYTICS ====================
    with tab1:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        sessions = list(sessions_col.find({"username": username, "timestamp": {"$gte": cutoff}}))
        
        if not sessions:
            st.info("💡 Start chatting to see your analytics!")
            return
        
        df = pd.DataFrame(sessions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        df['hour'] = df['timestamp'].dt.hour
        df['emotion'] = df.apply(lambda x: x.get('final_emotion') or x.get('emotion', 'neutral'), axis=1)
        
        # Key Metrics
        st.subheader("📈 Chat Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Messages", len(sessions))
        with col2:
            st.metric("Most Common Emotion", df['emotion'].mode()[0].title() if len(df['emotion'].mode()) > 0 else "N/A")
        with col3:
            st.metric("Days Active", df['date'].nunique())
        with col4:
            avg_conf = df['face_confidence'].mean() if 'face_confidence' in df.columns else 0
            st.metric("Avg Face Confidence", f"{avg_conf:.1%}")
        
        # Emotion trends over time
        st.subheader("📈 Emotion Trends Over Time")
        emotion_over_time = df.groupby(['date', 'emotion']).size().reset_index(name='count')
        fig = px.line(
            emotion_over_time,
            x='date', 
            y='count', 
            color='emotion',
            title="Daily Emotion Patterns",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Emotion distribution pie chart
        st.subheader("🥧 Emotion Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = go.Figure(data=[go.Pie(
                labels=df['emotion'].value_counts().index,
                values=df['emotion'].value_counts().values,
                hole=0.3,
                marker=dict(colors=px.colors.qualitative.Set3)
            )])
            fig2.update_layout(title="Overall Emotion Distribution")
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Hourly activity heatmap
            hourly_data = df.groupby('hour').size().reset_index(name='count')
            fig3 = px.bar(
                hourly_data,
                x='hour',
                y='count',
                title="Activity by Hour of Day",
                labels={'hour': 'Hour', 'count': 'Number of Messages'}
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # Scatter Plot - Face Confidence vs Text Emotion
        st.subheader("📊 Face Confidence vs Emotion Analysis")
        
        if 'face_confidence' in df.columns and 'face_emotion' in df.columns:
            # Create scatter plot
            fig4 = px.scatter(
                df,
                x='timestamp',
                y='face_confidence',
                color='face_emotion',
                size=[10]*len(df),
                hover_data=['user_text', 'emotion'],
                title="Face Emotion Confidence Over Time",
                labels={'face_confidence': 'Confidence Level', 'timestamp': 'Time'}
            )
            fig4.update_traces(marker=dict(size=12, line=dict(width=1, color='DarkSlateGrey')))
            fig4.update_layout(height=400)
            st.plotly_chart(fig4, use_container_width=True)
            
            # Additional scatter: Emotion correlation
            st.subheader("🔄 Text vs Face Emotion Match")
            df['emotion_match'] = df.apply(
                lambda x: 'Match' if x.get('face_emotion') == x.get('emotion') else 'Mismatch', 
                axis=1
            )
            
            fig5 = px.scatter(
                df,
                x='face_confidence',
                y=df.index,
                color='emotion_match',
                hover_data=['face_emotion', 'emotion', 'user_text'],
                title="Face vs Text Emotion Correlation",
                labels={'face_confidence': 'Face Confidence', 'y': 'Session Index'},
                color_discrete_map={'Match': '#00CC96', 'Mismatch': '#EF553B'}
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Stats
            match_rate = (df['emotion_match'] == 'Match').sum() / len(df) * 100
            st.info(f"📊 Face-Text Emotion Match Rate: **{match_rate:.1f}%**")
        else:
            st.info("💡 Use Virtual Chat with face detection to see face confidence analytics!")
        
        # Weekly emotion summary
        st.subheader("📅 Weekly Emotion Summary")
        df['week'] = df['timestamp'].dt.to_period('W').astype(str)
        weekly_emotions = df.groupby(['week', 'emotion']).size().reset_index(name='count')
        fig6 = px.bar(
            weekly_emotions,
            x='week',
            y='count',
            color='emotion',
            title="Weekly Emotion Breakdown",
            barmode='stack'
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    # ==================== TAB 2: ASSESSMENT REPORTS ====================
    with tab2:
        st.subheader("📝 Mental Health Assessment History")
        
        # Fetch all assessments for user
        assessments = list(assessments_col.find({"username": username}).sort("timestamp", -1))
        
        if not assessments:
            st.info("💡 Take assessments in the Resources section to see reports here!")
            return
        
        # Convert to DataFrame
        df_assess = pd.DataFrame(assessments)
        df_assess['timestamp'] = pd.to_datetime(df_assess['timestamp'])
        df_assess['date'] = df_assess['timestamp'].dt.date
        
        # Summary metrics
        st.subheader("📊 Assessment Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Assessments", len(assessments))
        with col2:
            conditions_tested = df_assess['condition'].nunique()
            st.metric("Conditions Tested", conditions_tested)
        with col3:
            most_recent = df_assess.iloc[0]['timestamp'].strftime("%Y-%m-%d")
            st.metric("Last Assessment", most_recent)
        
        # Assessment scores over time
        st.subheader("📈 Assessment Scores Over Time")
        fig_scores = px.line(
            df_assess,
            x='date',
            y='percentage',
            color='condition',
            markers=True,
            title="Assessment Score Trends (Percentage)",
            labels={'percentage': 'Score (%)', 'date': 'Date', 'condition': 'Condition'}
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        
        # Condition-wise breakdown
        st.subheader("🧩 Condition-wise Assessment Scores")
        
        for condition in df_assess['condition'].unique():
            with st.expander(f"📊 {MENTAL_HEALTH_CONDITIONS[condition]['icon']} {MENTAL_HEALTH_CONDITIONS[condition]['name']}"):
                condition_data = df_assess[df_assess['condition'] == condition].sort_values('timestamp')
                
                if len(condition_data) > 0:
                    # Line chart for this condition
                    fig_cond = go.Figure()
                    fig_cond.add_trace(go.Scatter(
                        x=condition_data['date'],
                        y=condition_data['score'],
                        mode='lines+markers',
                        name='Score',
                        line=dict(color=MENTAL_HEALTH_CONDITIONS[condition]['color'], width=3),
                        marker=dict(size=10)
                    ))
                    fig_cond.update_layout(
                        title=f"{MENTAL_HEALTH_CONDITIONS[condition]['name']} Progress",
                        xaxis_title="Date",
                        yaxis_title="Score",
                        height=300
                    )
                    st.plotly_chart(fig_cond, use_container_width=True)
                    
                    # Latest assessment details
                    latest = condition_data.iloc[-1]
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Latest Score", f"{latest['score']}/{latest['max_score']}")
                    with col2:
                        st.metric("Percentage", f"{latest['percentage']:.1f}%")
                    with col3:
                        severity = get_severity_level(condition, latest['score'], latest['max_score'])
                        st.metric("Severity", severity)
                    with col4:
                        # Progress indicator
                        if len(condition_data) > 1:
                            prev_score = condition_data.iloc[-2]['percentage']
                            current_score = latest['percentage']
                            delta = current_score - prev_score
                            st.metric("Change", f"{delta:+.1f}%", delta=f"{delta:+.1f}%")
                        else:
                            st.metric("Assessments", "1")
                    
                    # Historical table
                    st.markdown("##### Assessment History")
                    history_table = condition_data[['date', 'score', 'max_score', 'percentage']].copy()
                    history_table['percentage'] = history_table['percentage'].round(1).astype(str) + '%'
                    history_table.columns = ['Date', 'Score', 'Max Score', 'Percentage']
                    st.dataframe(history_table, use_container_width=True, hide_index=True)
        
        # Overall severity heatmap
        st.subheader("🌡️ Severity Heatmap")
        severity_data = df_assess.pivot_table(
            values='percentage',
            index='condition',
            columns='date',
            aggfunc='mean'
        )
        
        fig_heatmap = px.imshow(
            severity_data,
            labels=dict(x="Date", y="Condition", color="Severity %"),
            color_continuous_scale="RdYlGn_r",
            title="Assessment Severity Over Time"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # ==================== TAB 3: COMBINED INSIGHTS ====================
    with tab3:
        st.subheader("📈 Combined Mental Health Insights")
        
        # Check if we have both chat and assessment data
        if not sessions:
            st.info("💡 No chat data available yet!")
            return
        if not assessments:
            st.info("💡 No assessment data available yet!")
            return
        
        st.markdown("""
        This section combines your chat emotions with assessment scores to provide comprehensive insights.
        """)
        
        # Emotion vs Assessment correlation
        st.subheader("🔗 Emotion Patterns vs Assessment Scores")
        
        # Get dominant emotions per day
        df_emotions_daily = df.groupby(['date', 'emotion']).size().reset_index(name='count')
        dominant_emotion_per_day = df_emotions_daily.loc[df_emotions_daily.groupby('date')['count'].idxmax()]
        
        # Merge with assessments
        df_merged = pd.merge(
            df_assess[['date', 'condition', 'percentage']],
            dominant_emotion_per_day[['date', 'emotion']],
            on='date',
            how='left'
        )
     # **FIX: Remove rows with NaN values in percentage or emotion**
        df_merged = df_merged.dropna(subset=['percentage', 'emotion']) 

        if not df_merged.empty:
            fig_combined = px.scatter(
                df_merged,
                x='date',
                y='percentage',
                color='emotion',
                size=[10]*len(df_merged),
                hover_data=['condition'],
                title="Assessment Scores vs Daily Dominant Emotion",
                labels={'percentage': 'Assessment Score (%)', 'date': 'Date'}
            )
            st.plotly_chart(fig_combined, use_container_width=True)
        else:
            st.info("💡 No overlapping data between chat emotions and assessments on the same days yet!")
        # Wellness Score
        st.subheader("💯 Overall Wellness Score")
        
        # Calculate wellness score (inverted assessment scores + positive emotion ratio)
        avg_assessment_score = df_assess['percentage'].mean()
        positive_emotions = ['joy', 'surprise']
        positive_ratio = (df['emotion'].isin(positive_emotions).sum() / len(df)) * 100
        
        wellness_score = ((100 - avg_assessment_score) + positive_ratio) / 2
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Wellness Score", f"{wellness_score:.1f}/100")
        with col2:
            st.metric("Positive Emotion %", f"{positive_ratio:.1f}%")
        with col3:
            st.metric("Avg Assessment Score", f"{avg_assessment_score:.1f}%")
        
        # Gauge chart for wellness score
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=wellness_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Wellness Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 33], 'color': "lightcoral"},
                    {'range': [33, 66], 'color': "lightyellow"},
                    {'range': [66, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Recommendations
        st.subheader("💡 Personalized Recommendations")
        
        if wellness_score >= 70:
            st.success("""
            🌟 **Great job!** Your mental health metrics are positive!
            - Keep up your healthy routines
            - Continue social connections
            - Maintain work-life balance
            """)
        elif wellness_score >= 40:
            st.warning("""
            ⚠️ **Room for improvement**
            - Increase physical activity (30 min daily)
            - Practice daily mindfulness or meditation
            - Strengthen social connections
            - Consider self-help resources in the app
            """)
        else:
            st.error("""
            🆘 **Attention needed**
            - Your metrics suggest you may be struggling
            - Strongly consider professional mental health support
            - Use crisis helplines if in distress
            - Implement daily self-care routines
            - Reach out to trusted friends/family
            """)
        
        # Download report button
        if st.button("📥 Download Full Report (CSV)"):
            # Combine data for download
            report_data = {
                'Chat Sessions': len(sessions),
                'Assessments Taken': len(assessments),
                'Wellness Score': wellness_score,
                'Positive Emotion %': positive_ratio,
                'Average Assessment Score': avg_assessment_score
            }
            
            st.download_button(
                label="Download Report",
                data=str(report_data),
                file_name=f"mental_health_report_{username}_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

# ==================== Resources Page with Quizzes ====================
def resources_page():
    st.title("ℹ️ Mental Health Resources")
    
    tab1, tab2, tab3 = st.tabs(["🆘 Crisis Helplines", "📝 Self-Assessments", "💡 Self-Help"])
    
    with tab1:
        st.subheader("🆘 Crisis Helplines (India)")
        helplines = {
            "AASRA": "91-22-27546669",
            "Vandrevala Foundation": "1860-2662-345",
            "iCall": "022-25521111",
            "Snehi": "91-22-27546669"
        }
        for org, contact in helplines.items():
            st.info(f"**{org}**: {contact}")
    
    with tab2:
        st.subheader("📝 Mental Health Self-Assessments")
        
        condition = st.selectbox(
            "Select a condition to assess:",
            list(MENTAL_HEALTH_CONDITIONS.keys()),
            format_func=lambda x: MENTAL_HEALTH_CONDITIONS[x]["name"]
        )
        
        data = MENTAL_HEALTH_CONDITIONS[condition]
        
        st.markdown(f"## {data['icon']} {data['name']}")
        st.markdown(data["description"])
        
        with st.expander("📋 View Symptoms & Types"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Symptoms")
                for s in data["symptoms"]:
                    st.write(f"• {s}")
            with col2:
                st.markdown("### Types")
                for t in data["types"]:
                    st.write(f"• {t}")
        
        # Assessment Quiz
        if condition in ASSESSMENT_QUESTIONS:
            st.markdown("---")
            st.subheader(f"📝 {data['name']} Assessment Quiz (15 Questions)")
            st.info("💡 This comprehensive assessment helps identify symptoms. Answer honestly for accurate results.")
            
            questions = ASSESSMENT_QUESTIONS[condition]
            total_score = 0
            max_score = sum([max(q["scores"]) for q in questions])
            
            # Use form for better UX
            with st.form(key=f"quiz_form_{condition}"):
                for idx, q in enumerate(questions):
                    st.markdown(f"**Question {idx + 1}/15:**")
                    choice = st.radio(
                        q["question"],
                        q["options"],
                        key=f"{condition}_q{idx}"
                    )
                    score_index = q["options"].index(choice)
                    total_score += q["scores"][score_index]
                
                submitted = st.form_submit_button("📊 Submit & View Results")
            
            if submitted:
                # Calculate percentage
                percentage = (total_score / max_score) * 100
                
                # Save to database
                assessment_record = {
                    "username": st.session_state.username,
                    "condition": condition,
                    "score": total_score,
                    "max_score": max_score,
                    "percentage": percentage,
                    "timestamp": datetime.datetime.utcnow()
                }
                assessments_col.insert_one(assessment_record)
                
                st.markdown("---")
                st.markdown(f"### 📊 Your Assessment Results")
                
                # Score display
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Score", f"{total_score}/{max_score}")
                with col2:
                    st.metric("Percentage", f"{percentage:.1f}%")
                with col3:
                    severity = get_severity_level(condition, total_score, max_score)
                    st.metric("Severity", severity)
                
                # Progress bar
                st.progress(total_score / max_score)
                
                # Interpretation based on condition
                st.markdown("### 🔍 Interpretation")
                
                if condition == "anxiety":
                    if total_score <= 15:
                        st.success("🟢 **Minimal Anxiety** - You're experiencing low levels of anxiety.")
                        recommendation = "Continue healthy habits like exercise, good sleep, and stress management."
                    elif total_score <= 30:
                        st.warning("🟡 **Mild to Moderate Anxiety** - You're experiencing noticeable anxiety symptoms.")
                        recommendation = "Consider self-help strategies, breathing exercises, and lifestyle changes. Monitor your symptoms."
                    else:
                        st.error("🔴 **Moderate to Severe Anxiety** - You're experiencing significant anxiety that may be interfering with daily life.")
                        recommendation = "Strongly consider consulting a mental health professional. Self-help strategies can supplement professional treatment."
                
                elif condition == "depression":
                    if total_score <= 15:
                        st.success("🟢 **Minimal Depression** - You're experiencing few depressive symptoms.")
                        recommendation = "Maintain healthy routines, social connections, and activities you enjoy."
                    elif total_score <= 30:
                        st.warning("🟡 **Mild to Moderate Depression** - You're experiencing noticeable depressive symptoms.")
                        recommendation = "Try behavioral activation, regular exercise, and social engagement. Consider therapy if symptoms persist."
                    else:
                        st.error("🔴 **Moderate to Severe Depression** - You're experiencing significant depression.")
                        recommendation = "Professional help is strongly recommended. Depression is treatable - please reach out to a mental health provider."
                
                elif condition == "stress":
                    if total_score <= 20:
                        st.success("🟢 **Low Stress** - You're managing stress well.")
                        recommendation = "Continue your current coping strategies and maintain work-life balance."
                    elif total_score <= 40:
                        st.warning("🟡 **Moderate Stress** - You're experiencing considerable stress.")
                        recommendation = "Implement stress management techniques: time management, relaxation practices, and setting boundaries."
                    else:
                        st.error("🔴 **High Stress** - You're experiencing very high stress levels.")
                        recommendation = "Urgent lifestyle changes needed. Consider reducing commitments, seeking support, and possibly professional counseling."
                
                elif condition == "ptsd":
                    if total_score <= 20:
                        st.success("🟢 **Minimal PTSD Symptoms** - You're experiencing few trauma-related symptoms.")
                        recommendation = "Continue self-care and processing strategies. Reach out for support if symptoms increase."
                    elif total_score <= 40:
                        st.warning("🟡 **Mild to Moderate PTSD** - You're experiencing noticeable trauma symptoms.")
                        recommendation = "Grounding techniques and support groups may help. Consider trauma-focused therapy like EMDR or CPT."
                    else:
                        st.error("🔴 **Moderate to Severe PTSD** - You're experiencing significant trauma symptoms.")
                        recommendation = "Professional trauma therapy is strongly recommended. PTSD is highly treatable with specialized approaches."
                
                elif condition == "insomnia":
                    if total_score <= 20:
                        st.success("🟢 **Minimal Sleep Issues** - Your sleep is relatively good.")
                        recommendation = "Maintain good sleep hygiene and consistent sleep schedule."
                    elif total_score <= 40:
                        st.warning("🟡 **Moderate Insomnia** - You're experiencing noticeable sleep difficulties.")
                        recommendation = "Try CBT-I techniques: sleep restriction, stimulus control, and sleep hygiene improvements."
                    else:
                        st.error("🔴 **Severe Insomnia** - You're experiencing significant sleep problems.")
                        recommendation = "Consider consulting a sleep specialist. CBT-I (cognitive behavioral therapy for insomnia) is highly effective."
                
                st.info(f"💡 **Recommendation**: {recommendation}")
                
                st.warning("⚠️ **Important**: This is a screening tool, NOT a medical diagnosis. Please consult a qualified mental health professional for accurate assessment and treatment.")
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📈 View My Assessment History"):
                        st.session_state.view_assessment_history = True
                with col2:
                    if st.button("📞 Find Professional Help"):
                        st.info("Check the Crisis Helplines tab for professional resources.")
        
        # Interventions
        st.markdown("---")
        st.subheader("🛠️ Non-Medical Interventions")
        for section_key, section in data["non_medical_interventions"].items():
            with st.expander(section["title"]):
                for key, value in section.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                st.markdown(f"**{item.get('name', '')}**")
                                st.write(item.get('description', ''))
                            else:
                                st.write(f"• {item}")
        
        # Success Stories
        with st.expander("🌟 Success Stories"):
            for story in data["success_stories"]:
                st.success(story)
        
        # When to Seek Help
        with st.expander("🆘 When to Seek Professional Help"):
            for item in data["when_to_seek_help"]:
                st.warning(item)
    
    with tab3:
        st.subheader("💡 Quick Self-Help Tips")
        st.markdown("""
        ### Breathing Exercises
        - **4-7-8 Breathing**: Inhale 4s, hold 7s, exhale 8s
        - **Box Breathing**: Inhale 4s, hold 4s, exhale 4s, hold 4s
        
        ### Daily Wellness
        - 🌅 Morning sunlight (15-30 min)
        - 🏃 Exercise (30 min daily)
        - 😴 Sleep consistency (7-9 hours)
        - 📝 Journaling
        - 🧘 Meditation (5-10 min)
        """)

# ==================== Main Entry Point ====================
def main():
    if not st.session_state.authenticated:
        auth_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()
