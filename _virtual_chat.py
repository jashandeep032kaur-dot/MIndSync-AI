# _virtual_chat.py
import streamlit as st
import cv2, time, os, tempfile, threading, datetime, glob, base64
import speech_recognition as sr
from deepface import DeepFace
from db import get_db

import numpy as np

DEEPFACE_AVAILABLE = True
try:
    import deepface
except:
    DEEPFACE_AVAILABLE = False

# ==================== Virtual Chat Mode ====================
def virtual_chat_mode(username=None, detect_text_emotion_func=None, retrieve_answer_func=None):
    if username is None:
        username = "Guest"
    
    if detect_text_emotion_func is None:
        def detect_text_emotion_func(text):
            return "neutral", 0.5
    
    if retrieve_answer_func is None:
        def retrieve_answer_func(query, emotion):
            return "I'm here to help. Please connect the RAG system."

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
        "last_frame": None,
        "detecting_emotion": False,  # Flag to prevent multiple detections
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # ==================== TTS ====================
    try:
        import pyttsx3
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 150)
        tts_engine.available = True
    except:
        tts_engine = type('', (), {"available": False})()

    def speak_async(text):
        if not tts_engine.available:
            return
        def speak():
            try:
                tts_engine.say(text)
                tts_engine.runAndWait()
            except:
                pass
        threading.Thread(target=speak, daemon=True).start()

    # ==================== ASYNC EMOTION DETECTION ====================
    def detect_emotion_async(frame_copy):
        """Run emotion detection in background thread"""
        if st.session_state.detecting_emotion:
            return  # Skip if already detecting
        
        st.session_state.detecting_emotion = True
        
        def detect():
            tmp_path = None
            try:
                # Save frame to temp file
                tmp_path = os.path.join(tempfile.gettempdir(), f"emotion_{int(time.time()*1000)}.jpg")
                cv2.imwrite(tmp_path, frame_copy)
                
                # Analyze emotion
                result = DeepFace.analyze(
                    img_path=tmp_path,
                    actions=["emotion"],
                    enforce_detection=False,
                    detector_backend='opencv',
                    silent=True
                )
                
                if isinstance(result, list):
                    result = result[0]
                
                emotion = result["dominant_emotion"]
                confidence = result["emotion"][emotion] / 100.0
                
                # Update session state
                st.session_state.live_emotion = emotion
                st.session_state.live_confidence = confidence
                
                # Add to timeline
                st.session_state.emotion_timeline.append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "emotion": emotion,
                    "confidence": confidence
                })
                
            except Exception as e:
                # Silent fail - keep previous emotion
                pass
            finally:
                # Cleanup
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                st.session_state.detecting_emotion = False
        
        # Run in background thread
        threading.Thread(target=detect, daemon=True).start()

    # ==================== CRISIS KEYWORDS ====================
    CRISIS_KEYWORDS = ["suicide", "kill myself", "end my life", "i want to die", "harm myself"]

    # ==================== LAYOUT ====================
    col1, col2 = st.columns([1, 1])

    # ==================== CAMERA ====================
    with col1:
        st.subheader("📹 Live Camera Feed")
        st.metric(
            "Your Current Emotion",
            f"{EMOJI_MAP.get(st.session_state.live_emotion, '😐')} {st.session_state.live_emotion.title()}",
            f"{st.session_state.live_confidence:.0%}"
        )

        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if not st.session_state.camera_active:
                if st.button("📷 Start Camera", use_container_width=True):
                    try:
                        # Release any existing camera
                        if st.session_state.cap is not None:
                            st.session_state.cap.release()
                        
                        # Open new camera
                        st.session_state.cap = cv2.VideoCapture(0)
                        st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        st.session_state.cap.set(cv2.CAP_PROP_FPS, 30)
                        st.session_state.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        
                        if st.session_state.cap.isOpened():
                            st.session_state.camera_active = True
                            st.session_state.frame_counter = 0
                            st.success("✅ Camera started!")
                        else:
                            st.error("❌ Failed to open camera")
                    except Exception as e:
                        st.error(f"Camera error: {str(e)}")
                    st.rerun()
            else:
                if st.button("⏹ Stop Camera", use_container_width=True):
                    st.session_state.camera_active = False
                    if st.session_state.cap:
                        st.session_state.cap.release()
                        st.session_state.cap = None
                    save_session_to_mongo(username)
                    st.success("Camera stopped and session saved!")
                    st.rerun()

        with btn_col2:
            if st.button("📸 Snapshot", use_container_width=True, disabled=not st.session_state.camera_active):
                if st.session_state.last_frame is not None:
                    os.makedirs("snapshots", exist_ok=True)
                    fname = f"snapshots/snap_{int(time.time())}.jpg"
                    cv2.imwrite(fname, st.session_state.last_frame)
                    st.success(f"📷 Saved!")
        
        with btn_col3:
            if st.button("🔄 Detect Now", use_container_width=True, disabled=not st.session_state.camera_active):
                if st.session_state.last_frame is not None and not st.session_state.detecting_emotion:
                    detect_emotion_async(st.session_state.last_frame.copy())
                    st.info("🔍 Detecting...")

        video_placeholder = st.empty()

        # ==================== CAMERA LOOP ====================
        if st.session_state.camera_active:
            if st.session_state.cap is None or not st.session_state.cap.isOpened():
                st.session_state.cap = cv2.VideoCapture(0)
                st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            ret, frame = st.session_state.cap.read()
            
            if ret:
                frame = cv2.flip(frame, 1)
                st.session_state.last_frame = frame.copy()
                st.session_state.frame_counter += 1

                # ==================== Emotion Detection (every 60 frames = ~2 sec) ====================
                # Run emotion detection less frequently to prevent hanging
                if st.session_state.frame_counter % 60 == 0 and not st.session_state.detecting_emotion:
                    detect_emotion_async(frame.copy())

                # Draw emotion on frame with better visibility
                emotion_text = f"{st.session_state.live_emotion.upper()}"
                confidence_text = f"{st.session_state.live_confidence:.0%}"
                
                # Background rectangle for better readability
                cv2.rectangle(frame, (5, 5), (300, 70), (0, 0, 0), -1)
                cv2.rectangle(frame, (5, 5), (300, 70), (0, 255, 0), 2)
                
                # Emotion text
                cv2.putText(
                    frame,
                    emotion_text,
                    (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )
                
                # Confidence text
                cv2.putText(
                    frame,
                    confidence_text,
                    (15, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
                
                # Display frame
                try:
                    # Try newer Streamlit API
                    video_placeholder.image(frame, channels="BGR", use_container_width=True)
                except TypeError:
                    # Fallback for older Streamlit versions
                    video_placeholder.image(frame, channels="BGR")
            else:
                video_placeholder.error("❌ Cannot read from camera")

    # ==================== CHAT ====================
    with col2:
        st.subheader("💬 Chat Interface")
        
        # Display chat history in a scrollable container
        chat_container = st.container(height=400)
        with chat_container:
            for m in st.session_state.virtual_chat_history:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])

        # Input mode selection (stays inside column)
        input_mode = st.radio("Choose Input Mode:", ["💬 Type", "🎤 Speak"], horizontal=True)
    
    # ==================== INPUT SECTION (OUTSIDE COLUMNS) ====================
    user_input = ""
    
    if input_mode == "💬 Type":
        user_input = st.chat_input("Type your message here...")
    else:
        if st.button("🎤 Press & Speak", use_container_width=True):
            recognizer = sr.Recognizer()
            with st.spinner("🎤 Listening..."):
                try:
                    with sr.Microphone() as source:
                        st.info("Speak now...")
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    user_input = recognizer.recognize_google(audio)
                    st.success(f"✅ You said: {user_input}")
                except sr.WaitTimeoutError:
                    st.error("⏱️ No speech detected")
                except sr.UnknownValueError:
                    st.error("❌ Could not understand audio")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # ==================== PROCESS USER INPUT ====================
    if user_input:
        # Get emotions
        face_emotion = st.session_state.live_emotion
        face_confidence = st.session_state.live_confidence
        text_emotion, text_confidence = detect_text_emotion_func(user_input)

        # Choose emotion based on confidence
        final_emotion = face_emotion if face_confidence > 0.5 else text_emotion

        # Check for crisis keywords
        is_crisis = any(keyword in user_input.lower() for keyword in CRISIS_KEYWORDS)

        if is_crisis:
            bot_reply = (
                "⚠️ I'm very concerned about what you're sharing. Please reach out for help immediately:\n\n"
                "🇮🇳 India Helplines:\n"
                "• AASRA: 91-22-27546669\n"
                "• Vandrevala Foundation: 1860-2662-345\n\n"
                "You are not alone. Please talk to someone who can help."
            )
        else:
            # Retrieve answer from RAG system
            bot_reply = retrieve_answer_func(user_input, final_emotion)

        # Add to chat history
        st.session_state.virtual_chat_history.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.virtual_chat_history.append({
            "role": "assistant",
            "content": bot_reply
        })

        # Speak the reply
        speak_async(bot_reply)
        
        st.rerun()

# ==================== SAVE TO MONGODB ====================
def save_session_to_mongo(username: str):
    try:
        db = get_db()
        col = db["virtual_chat_sessions"]

        # Read all snapshots
        snapshot_data = []
        if os.path.exists("snapshots"):
            for f in glob.glob("snapshots/*.jpg"):
                try:
                    with open(f, "rb") as img_file:
                        snapshot_data.append(
                            base64.b64encode(img_file.read()).decode("utf-8")
                        )
                except Exception:
                    pass

        doc = {
            "username": username,
            "timestamp": datetime.datetime.utcnow(),
            "chat_history": st.session_state.virtual_chat_history,
            "emotion_timeline": st.session_state.emotion_timeline,
            "snapshots": snapshot_data,
            "total_messages": len(st.session_state.virtual_chat_history),
            "session_duration_emotions": len(st.session_state.emotion_timeline),
        }

        col.insert_one(doc)
        st.success("✅ Virtual Chat Session saved to MongoDB")

    except Exception as e:
        st.warning("⚠️ Could not save session to database.")
