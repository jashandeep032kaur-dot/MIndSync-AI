# _virtual_chat.py
import streamlit as st
import cv2, time, os, tempfile, threading, datetime, glob, base64
import speech_recognition as sr
from deepface import DeepFace
from pymongo import MongoClient

DEEPFACE_AVAILABLE = True
try:
    import deepface
except:
    DEEPFACE_AVAILABLE = False

# ==================== Virtual Chat Mode ====================
#def virtual_chat_mode(username: str):
def virtual_chat_mode(username=None,detect_text_emotion_func=None):
    if username is None:
        username = "Guest"  # default if no username is provided

    st.title("🎥 Virtual Chat - Live Face Emotion Detection")

    if not DEEPFACE_AVAILABLE:
        st.error("⚠️ DeepFace library not installed. Please install it: `pip install deepface`")
        return

    st.info("📸 Camera stays open! Chat freely with text or voice - bot speaks back!")

    EMOJI_MAP = {
        "happy": "😄", "sad": "😢", "angry": "😠", "fear": "😨",
        "neutral": "😐", "surprise": "😲", "disgust": "🤢"
    }

    # ==================== SESSION STATE ====================
    for key, val in {
        "live_emotion": "neutral",
        "live_confidence": 0.0,
        "camera_active": False,
        "frame_counter": 0,
        "cap": None,
        "virtual_chat_history": [],
        "emotion_timeline": [],
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ==================== TTS ====================
    try:
        import pyttsx3
        tts_engine = pyttsx3.init()
        tts_engine.available = True
    except:
        tts_engine = type('', (), {"available": False})()

    def speak_async(text):
        if not tts_engine.available:
            return
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except:
            pass

    # ==================== CRISIS KEYWORDS ====================
    CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "i want to die"]

    # ==================== LAYOUT ====================
    col1, col2 = st.columns([1,1])

    # ==================== CAMERA ====================
    with col1:
        st.subheader("📹 Live Camera Feed")
        st.metric(
            "Your Current Emotion",
            f"{EMOJI_MAP.get(st.session_state.live_emotion, '😐')} {st.session_state.live_emotion.title()}",
            f"{st.session_state.live_confidence:.0%}"
        )

        if not st.session_state.camera_active:
            if st.button("📷 Start Camera", use_container_width=True):
                st.session_state.camera_active = True
                st.rerun()
        else:
            if st.button("⏹ Stop Camera", use_container_width=True):
                st.session_state.camera_active = False
                if st.session_state.cap:
                    st.session_state.cap.release()
                    st.session_state.cap = None
                save_session_to_mongo(username)
                st.rerun()

        video_placeholder = st.empty()

        if st.button("📸 Take Snapshot", use_container_width=True):
            if st.session_state.cap and st.session_state.cap.isOpened():
                ret, snap = st.session_state.cap.read()
                if ret:
                    os.makedirs("snapshots", exist_ok=True)
                    fname = f"snapshots/snap_{int(time.time())}.jpg"
                    cv2.imwrite(fname, snap)
                    st.success(f"Saved: {fname}")
                    st.image(snap, channels="BGR")

        if st.session_state.camera_active:
            if st.session_state.cap is None or not st.session_state.cap.isOpened():
                st.session_state.cap = cv2.VideoCapture(0)

            ret, frame = st.session_state.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                st.session_state.frame_counter += 1

                # ==================== Emotion Detection ====================
                if st.session_state.frame_counter % 15 == 0:
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                    cv2.imwrite(tmp.name, frame)
                    try:
                        res = DeepFace.analyze(tmp.name, actions=["emotion"], enforce_detection=False)
                        if isinstance(res, list):
                            res = res[0]
                        emo = res["dominant_emotion"]
                        conf = res["emotion"][emo] / 100
                        st.session_state.live_emotion = emo
                        st.session_state.live_confidence = conf

                        # Add to emotion timeline
                        st.session_state.emotion_timeline.append({
                            "timestamp": datetime.datetime.now().isoformat(),
                            "emotion": emo,
                            "confidence": conf
                        })
                    except:
                        pass
                    os.unlink(tmp.name)

                cv2.putText(frame, st.session_state.live_emotion, (10,40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                video_placeholder.image(frame, channels="BGR", use_container_width=True)

    # ==================== CHAT ====================
    with col2:
        st.subheader("💬 Chat Interface")
        for m in st.session_state.virtual_chat_history:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

        input_mode = st.radio("Choose Input Mode:", ["💬 Type", "🎤 Speak"], horizontal=True)
        user_input = ""

        if input_mode == "💬 Type":
            user_input = st.chat_input("Type your message here...")
        else:
            if st.button("🎤 Press & Speak", use_container_width=True):
                recognizer = sr.Recognizer()
                try:
                    with sr.Microphone() as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    user_input = recognizer.recognize_google(audio)
                    st.success(f"You said: {user_input}")
                except:
                    st.error("Voice not understood")

        if user_input:
            face_em = st.session_state.live_emotion
            face_conf = st.session_state.live_confidence
           # text_em, text_conf = detect_text_emotion(user_input)
            if detect_text_emotion_func is not None:
                text_em, text_conf = detect_text_emotion_func(user_input)
            else:
                text_em, text_conf = "neutral", 0.0  # Define in main.py

            final_em = face_em if face_conf > 0.5 else text_em
            is_crisis = any(k in user_input.lower() for k in CRISIS_KEYWORDS)

            if is_crisis:
                bot_reply = "⚠️ Please reach out for help immediately. You are not alone."
            else:
                bot_reply = retrieve_answer(user_input, final_em)  # Define in main.py

            st.session_state.virtual_chat_history.append({"role":"user","content":user_input})
            st.session_state.virtual_chat_history.append({"role":"assistant","content":bot_reply})
            threading.Thread(target=speak_async, args=(bot_reply,), daemon=True).start()
            st.rerun()

# ==================== SAVE TO MONGODB ====================
def save_session_to_mongo(username: str):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["final_chatbot_talks"]
    col = db["virtual_chat_sessions"]

    # Read all snapshots
    snapshot_data = []
    for f in glob.glob("snapshots/*.jpg"):
        with open(f, "rb") as img_file:
            snapshot_data.append(base64.b64encode(img_file.read()).decode("utf-8"))

    doc = {
        "username": username,
        "timestamp": datetime.datetime.now(),
        "chat_history": st.session_state.virtual_chat_history,
        "emotion_timeline": st.session_state.emotion_timeline,
        "snapshots": snapshot_data
    }
    col.insert_one(doc)
    st.success("✅ Virtual Chat Session saved to MongoDB")
