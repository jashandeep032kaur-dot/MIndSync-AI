# 🧠 MindSync-AI - Mental Health Support Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)](https://streamlit.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive AI-powered mental health support application that combines text/video chat, emotion detection, self-assessments, mood tracking, and personalized interventions to support mental wellness.

## ✨ Features

### 🎯 Core Features
- **💬 Text Chat Interface**: AI-powered conversations with emotion-aware responses
- **🎥 Virtual Chat**: Real-time video chat with facial emotion detection using DeepFace
- **📊 Advanced Analytics**: Comprehensive mental health metrics and visualizations
- **📝 Self-Assessments**: Clinical-grade questionnaires for anxiety, depression, stress, PTSD, and insomnia
- **🗓️ Mood Journal**: Daily mood tracking with insights and patterns
- **🎯 Goal Setting**: Personal wellness goals with progress tracking
- **📚 Guided Exercises**: Breathing techniques, meditation, and coping strategies
- **🏆 Achievements System**: Gamified wellness milestones
- **🔔 Smart Reminders**: Automated check-ins and wellness prompts
- **🎮 Interactive Tools**: Coping plans, resource library, and crisis intervention

### 🔬 Advanced Capabilities
- **Enhanced RAG System**: Retrieval-Augmented Generation for contextual, emotion-specific responses
- **Multi-Modal Emotion Detection**: Text + facial emotion analysis
- **Crisis Detection**: Automatic identification and response to crisis keywords
- **Personalized Interventions**: Tailored recommendations based on user data
- **Progress Tracking**: Long-term mental health metrics visualization
- **Interactive Wellness Tools**: Mood boards, gratitude jar, and worry box for creative emotional expression

## 🏗️ Architecture

```
MindSync-AI
├── Text Chat Module
│   ├── Emotion Detection (Transformers)
│   ├── RAG Knowledge Base (FAISS + Sentence-BERT)
│   └── Crisis Keyword Detection
├── Virtual Chat Module
│   ├── Face Emotion Detection (DeepFace)
│   ├── Speech Recognition
│   └── Text-to-Speech (pyttsx3)
├── Assessment System
│   ├── Anxiety (GAD-7)
│   ├── Depression (PHQ-9)
│   ├── Stress (PSS)
│   ├── PTSD (PCL-5)
│   └── Insomnia (ISI)
├── Phase 2 Enhancements
│   ├── Mood Journal
│   ├── Goal Tracking
│   ├── Wellness Exercises
│   ├── Achievement System
│   └── Reminder System
├── Phase 3 Interventions
│   ├── Coping Plans
│   ├── Resource Library
│   │   ├── Video Tutorials
│   │   ├── Audio Sessions
│   │   ├── CBT Worksheets
│   │   └── Educational Articles
│   └── Interactive Tools
│       ├── Mood Board Creator
│       ├── Gratitude Jar
│       └── Worry Box
└── Analytics Dashboard
    ├── Chat Analytics
    ├── Assessment Reports
    └── Combined Insights
```

## 📋 Prerequisites

- Python 3.8 or higher
- MongoDB 4.4 or higher
- Webcam (for virtual chat feature)
- Microphone (for speech input)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/mindsync-ai.git
cd mindsync-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install System Dependencies

**MongoDB**:
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Windows
# Download from https://www.mongodb.com/try/download/community
```

**Additional Libraries**:
```bash
# For speech recognition (optional)
pip install pyaudio

# For text-to-speech
pip install pyttsx3

# For face detection
pip install deepface opencv-python
```

### 5. Setup MongoDB
```bash
# Start MongoDB service
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # macOS

# Create database (automatic on first run)
```

### 6. Prepare RAG Knowledge Base
The `rag_knowledges` folder contains emotion-specific knowledge bases:

```bash
rag_knowledges/
├── happiness.json      # Responses for joy/positive emotions
├── sadness.json        # Responses for sadness/grief
├── neutral.json        # General conversational responses
├── anxiety.json        # Anxiety-specific guidance
└── depression.json     # Depression-specific support

# These files are pre-configured with the application
```

## 🎮 Usage

### Starting the Application
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### First Time Setup
1. Navigate to the **Register** tab
2. Create an account with username and password
3. Select your gender preference
4. Login with your credentials

### Using Features

**Text Chat**:
- Select "💬 Chat" from the sidebar
- Type your message and receive AI responses
- Emotions are automatically detected and displayed

**Virtual Chat**:
- Select "🎥 Virtual Chat" from the sidebar
- Allow camera and microphone access
- Start video chat with real-time emotion detection

**Self-Assessment**:
- Navigate to "ℹ️ Resources" → "📝 Self-Assessments"
- Choose a condition (Anxiety, Depression, Stress, etc.)
- Complete the 15-question assessment
- View detailed results and recommendations

**Analytics**:
- Select "📊 Analytics" from the sidebar
- View chat patterns, emotion trends, and assessment history
- Download comprehensive reports

**Mood Journal**:
- Navigate to "🗓️ Mood Journal"
- Log daily moods with notes
- View mood patterns over time

**Coping Plans**:
- Navigate to "🎯 Coping Plans"
- Generate personalized plans based on your emotional patterns
- Get custom breathing exercises, daily schedules, and activities
- Access emergency grounding techniques

**Resource Library**:
- Browse "📚 Resource Library"
- Watch guided video tutorials on breathing, meditation, and mindfulness
- Listen to audio sessions for sleep, anxiety relief, and motivation
- Download CBT worksheets for thought records and behavioral activation
- Read comprehensive articles on mental health topics

**Interactive Tools**:
- Create visual **Mood Boards** to express emotions through colors, words, and emojis
- Build a **Gratitude Jar** by adding daily gratitude notes (organized by categories)
- Use the **Worry Box** to write down worries, categorize them, and resolve them over time
- Track patterns and gain insights from your creative expressions

## 📦 Project Structure

```
mindsync-ai/
├── app.py                          # Main Streamlit application
├── phase2_enhancements.py          # Mood journal, goals, exercises, achievements
├── phase3_intervention.py          # Coping plans, resource library, interactive tools
├── _virtual_chat.py                # Video chat module with facial emotion detection
├── enhanced_rag_system.py          # RAG implementation with emotion-aware retrieval
├── chatbot_responses.py            # Response generation logic
├── requirements.txt                # Python dependencies
├── rag_knowledges/                 # Knowledge base directory
│   ├── happiness.json              # Joy/positive emotion responses
│   ├── sadness.json                # Sadness/grief support
│   ├── neutral.json                # General conversations
│   ├── anxiety.json                # Anxiety-specific guidance
│   └── depression.json             # Depression-specific support
├── README.md                       # This file
└── LICENSE                         # MIT License
```

## 🔧 Configuration

### Database Configuration
Edit the MongoDB connection in `app.py`:
```python
@st.cache_resource
def init_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["final_chatbot_talks"]
    return db
```

### RAG Configuration
Modify RAG settings in `enhanced_rag_system.py`:
```python
class EnhancedRAGSystem:
    def __init__(self, rag_directory="rag_knowledges"):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Customize model and settings
```

### Crisis Keywords
Update crisis detection keywords in `app.py`:
```python
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", 
    "i want to die", "self harm"
]
```

## 🧪 Testing

Run tests for individual modules:
```bash
# Test RAG system
python -c "from enhanced_rag_system import EnhancedRAGSystem; rag = EnhancedRAGSystem(); print(rag.retrieve_response('anxiety help', 'fear'))"

# Test emotion detection
python -c "from chatbot_responses import detect_emotion_from_text; print(detect_emotion_from_text('I feel sad today'))"
```

## 📊 Database Schema

### Users Collection
```json
{
  "username": "string",
  "password": "hashed_string",
  "gender": "string",
  "created_at": "datetime"
}
```

### Sessions Collection
```json
{
  "username": "string",
  "user_text": "string",
  "bot_text": "string",
  "emotion": "string",
  "face_emotion": "string (optional)",
  "face_confidence": "float (optional)",
  "timestamp": "datetime"
}
```

### Goals Collection
```json
{
  "username": "string",
  "goal": "string",
  "category": "string",
  "progress": "int",
  "created_at": "datetime"
}
```

### Mood Boards Collection
```json
{
  "username": "string",
  "mood": "string",
  "color": "string",
  "words": "string",
  "emojis": ["array"],
  "timestamp": "datetime"
}
```

### Gratitude Jar Collection
```json
{
  "username": "string",
  "text": "string",
  "category": "string",
  "timestamp": "datetime"
}
```

### Worry Box Collection
```json
{
  "username": "string",
  "text": "string",
  "intensity": "string",
  "controllable": "string",
  "status": "string (active/resolved)",
  "created_at": "datetime",
  "resolved_at": "datetime (optional)"
}
```

### Coping Plans Collection
```json
{
  "username": "string",
  "emotion_pattern": "string",
  "focus_areas": ["array"],
  "intensity": "string",
  "plan": "object",
  "created_at": "datetime",
  "active": "boolean"
}
```

## 🎨 Interactive Wellness Tools

MindSync-AI includes three creative tools for emotional expression and management:

### 🎨 Mood Board Creator
Create visual representations of your emotions:
- Select colors that match your mood
- Add descriptive words and phrases
- Choose emojis to express feelings
- View your mood board gallery over time
- Track emotional patterns visually

### 🙏 Gratitude Jar
Build a collection of gratitude notes:
- Write daily gratitude entries
- Categorize by: People, Experience, Growth, Nature, etc.
- Visualize your gratitude count
- Filter and review past entries
- Cultivate positive thinking habits

### 📦 Worry Box
Manage worries systematically:
- Write down worries to externalize them
- Rate intensity (Mild → Overwhelming)
- Categorize as controllable or uncontrollable
- Store worries to revisit later with perspective
- Mark worries as resolved
- View worry patterns and insights
- Get actionable suggestions based on controllability

These tools combine psychology principles with creative expression to support mental wellness in engaging, non-clinical ways.

- **Crisis Detection**: Automatic identification of suicidal/self-harm language
- **Emergency Resources**: Immediate display of crisis helplines
- **Non-Diagnostic Approach**: Clear disclaimers that assessments are screening tools
- **Professional Referral**: Recommendations to seek professional help when needed

## 🤝 Contributing

Contributions are welcome! Please follow these steps
