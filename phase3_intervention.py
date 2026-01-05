import streamlit as st
import json, datetime
import pandas as pd
import numpy as np
from pymongo import MongoClient
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
import plotly.express as px  # ADD THIS LINE
import plotly.graph_objects as go 
# -------------------- Database Connection --------------------
@st.cache_resource
def get_phase3_db():
    """Connect to MongoDB for Phase 3 features"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["final_chatbot_talks"]
    return db

db = get_phase3_db()

# Collections for Phase 3
coping_plans_col = db["coping_plans"]
resources_col = db["resources"]
mood_board_col = db["mood_boards"]
gratitude_jar_col = db["gratitude_jar"]
worry_box_col = db["worry_box"]
sessions_col = db["sessions"]  # For assessment data

# -------------------- 🎯 PERSONALIZED COPING PLANS --------------------
def coping_plans_page(username):
    st.title("🎯 Your Personalized Coping Plan")
    st.markdown("Custom strategies based on your mental health profile")
    
    tab1, tab2, tab3 = st.tabs(["📋 My Plan", "🔄 Generate New Plan", "📚 All Plans"])
    
    with tab1:
        display_current_plan(username)
    
    with tab2:
        generate_coping_plan(username)
    
    with tab3:
        view_all_plans(username)

def generate_coping_plan(username):
    st.subheader("🔄 Generate Personalized Coping Plan")
    
    # Get user's recent assessment data
    recent_sessions = list(sessions_col.find(
        {"username": username}
    ).sort("timestamp", -1).limit(10))
    
    if not recent_sessions:
        st.info("💡 Chat with the bot first to generate a personalized plan based on your emotions!")
        return
    
    # Analyze user's patterns
    emotions = [s.get('emotion', 'neutral') for s in recent_sessions]
    most_common_emotion = max(set(emotions), key=emotions.count)
    
    st.markdown(f"### Based on your recent patterns:")
    st.info(f"**Most Common Emotion:** {most_common_emotion.title()}")
    
    # Select focus areas
    st.markdown("### Select your focus areas:")
    
    focus_areas = st.multiselect(
        "What would you like to work on?",
        ["Anxiety Management", "Stress Relief", "Mood Enhancement", 
         "Sleep Quality", "Social Connection", "Self-Esteem", 
         "Anger Management", "Grief Processing"],
        default=["Anxiety Management", "Stress Relief"]
    )
    
    intensity = st.select_slider(
        "How intense should the interventions be?",
        options=["Gentle", "Moderate", "Intensive"],
        value="Moderate"
    )
    
    if st.button("🎯 Generate My Coping Plan", use_container_width=True):
        plan = create_personalized_plan(username, most_common_emotion, focus_areas, intensity)
        
        coping_plans_col.insert_one({
            "username": username,
            "emotion_pattern": most_common_emotion,
            "focus_areas": focus_areas,
            "intensity": intensity,
            "plan": plan,
            "created_at": datetime.datetime.utcnow(),
            "active": True
        })
        
        st.success("✅ Your personalized coping plan has been generated!")
        st.rerun()

def create_personalized_plan(username, emotion, focus_areas, intensity):
    """Generate a personalized coping plan based on user data"""
    
    # Breathing exercises based on emotion
    breathing_exercises = {
        "anxiety": {
            "name": "4-7-8 Calming Breath",
            "steps": [
                "Inhale through nose for 4 seconds",
                "Hold breath for 7 seconds",
                "Exhale through mouth for 8 seconds",
                "Repeat 4 times"
            ],
            "benefit": "Activates parasympathetic nervous system, reduces anxiety"
        },
        "anger": {
            "name": "Box Breathing",
            "steps": [
                "Inhale for 4 seconds",
                "Hold for 4 seconds",
                "Exhale for 4 seconds",
                "Hold for 4 seconds",
                "Repeat 5 times"
            ],
            "benefit": "Regulates emotions and reduces anger intensity"
        },
        "sadness": {
            "name": "Energizing Breath",
            "steps": [
                "Quick inhale through nose (1 second)",
                "Quick exhale through nose (1 second)",
                "Repeat rapidly 10 times",
                "Rest and breathe normally"
            ],
            "benefit": "Increases energy and lifts mood"
        },
        "default": {
            "name": "Calm Breathing",
            "steps": [
                "Inhale slowly for 3 seconds",
                "Exhale slowly for 6 seconds",
                "Repeat 5 times"
            ],
            "benefit": "General relaxation and stress reduction"
        }
    }
    
    # Activity suggestions based on focus areas
    activities = {
        "Anxiety Management": [
            "🚶 Take a 10-minute mindful walk",
            "📝 Write down 3 things you can control right now",
            "🎧 Listen to calming music for 15 minutes",
            "🧘 Progressive muscle relaxation (5 minutes)"
        ],
        "Stress Relief": [
            "🛁 Take a warm bath or shower",
            "📚 Read for pleasure (20 minutes)",
            "🎨 Engage in creative activity",
            "☕ Practice mindful tea/coffee drinking"
        ],
        "Mood Enhancement": [
            "🌞 Get 15 minutes of sunlight",
            "🤝 Connect with a friend or family member",
            "🎵 Listen to uplifting music and dance",
            "😊 Watch a comedy show or funny videos"
        ],
        "Sleep Quality": [
            "📱 No screens 1 hour before bed",
            "📖 Read a physical book before sleep",
            "🌙 Keep bedroom cool and dark",
            "🧘 Do gentle stretching before bed"
        ],
        "Social Connection": [
            "📞 Call or text a friend you haven't spoken to recently",
            "👥 Join an online community of your interest",
            "🤝 Plan a social activity for this week",
            "💬 Share something positive with someone today"
        ],
        "Self-Esteem": [
            "🪞 Write 5 things you like about yourself",
            "🏆 Acknowledge one achievement from today",
            "💪 Do something you're good at",
            "🎯 Set and complete one small goal today"
        ],
        "Anger Management": [
            "🚶 Take a break and walk away from the situation",
            "✍️ Write an angry letter (don't send it)",
            "🥊 Physical exercise to release tension",
            "🧊 Hold ice cubes to ground yourself"
        ],
        "Grief Processing": [
            "📝 Journal about your memories",
            "🕯️ Create a small memorial or ritual",
            "🤗 Allow yourself to cry if needed",
            "💬 Talk to someone who understands your loss"
        ]
    }
    
    # Get appropriate breathing exercise
    breath_exercise = breathing_exercises.get(emotion.lower(), breathing_exercises["default"])
    
    # Select activities based on focus areas
    selected_activities = []
    for area in focus_areas:
        if area in activities:
            selected_activities.extend(activities[area][:2])  # Take top 2 from each area
    
    # Daily schedule based on intensity
    schedules = {
        "Gentle": {
            "morning": "5 minutes breathing exercise",
            "afternoon": "One coping activity from your list",
            "evening": "Gratitude reflection (3 things)"
        },
        "Moderate": {
            "morning": "10 minutes breathing + mood check-in",
            "afternoon": "Two coping activities",
            "evening": "Breathing exercise + gratitude journal"
        },
        "Intensive": {
            "morning": "15 minutes breathing + meditation",
            "midday": "Mood check-in + one activity",
            "afternoon": "Two coping activities",
            "evening": "Breathing + gratitude + worry box review"
        }
    }
    
    plan = {
        "breathing_exercise": breath_exercise,
        "activities": selected_activities,
        "daily_schedule": schedules[intensity],
        "emergency_contacts": [
            {"name": "AASRA", "number": "91-22-27546669"},
            {"name": "Vandrevala Foundation", "number": "1860-2662-345"}
        ],
        "grounding_technique": {
            "name": "5-4-3-2-1 Grounding",
            "steps": [
                "5 things you can see",
                "4 things you can touch",
                "3 things you can hear",
                "2 things you can smell",
                "1 thing you can taste"
            ]
        }
    }
    
    return plan

def display_current_plan(username):
    """Display the user's active coping plan"""
    
    plan_doc = coping_plans_col.find_one({
        "username": username,
        "active": True
    }, sort=[("created_at", -1)])
    
    if not plan_doc:
        st.info("📋 No active coping plan. Generate one in the 'Generate New Plan' tab!")
        return
    
    plan = plan_doc['plan']
    
    # Display plan header
    st.markdown(f"### Your Active Plan")
    st.caption(f"Created: {plan_doc['created_at'].strftime('%B %d, %Y')}")
    st.markdown(f"**Focus Areas:** {', '.join(plan_doc['focus_areas'])}")
    st.markdown(f"**Intensity:** {plan_doc['intensity']}")
    
    st.markdown("---")
    
    # Breathing Exercise Section
    with st.expander("🌬️ Your Breathing Exercise", expanded=True):
        breath = plan['breathing_exercise']
        st.markdown(f"### {breath['name']}")
        st.info(f"**Benefit:** {breath['benefit']}")
        
        st.markdown("**Steps:**")
        for i, step in enumerate(breath['steps'], 1):
            st.markdown(f"{i}. {step}")
        
        if st.button("✅ I completed this exercise", key="breath_complete"):
            st.success("Great job! Keep up the good work! 🌟")
    
    # Daily Schedule
    with st.expander("📅 Daily Schedule", expanded=True):
        schedule = plan['daily_schedule']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🌅 Morning")
            st.info(schedule.get('morning', 'N/A'))
        
        with col2:
            st.markdown("#### ☀️ Afternoon")
            st.info(schedule.get('afternoon', schedule.get('midday', 'N/A')))
        
        with col3:
            st.markdown("#### 🌙 Evening")
            st.info(schedule.get('evening', 'N/A'))
    
    # Activities
    with st.expander("🎯 Recommended Activities", expanded=True):
        st.markdown("Choose activities that resonate with you:")
        
        activities = plan.get('activities', [])
        for activity in activities:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"• {activity}")
            with col2:
                if st.button("✓", key=f"activity_{hash(activity)}"):
                    st.success("Done! ✨")
    
    # Grounding Technique
    with st.expander("🧘 Emergency Grounding Technique"):
        grounding = plan['grounding_technique']
        st.markdown(f"### {grounding['name']}")
        st.markdown("Use this when feeling overwhelmed:")
        
        for step in grounding['steps']:
            st.markdown(f"• {step}")
    
    # Emergency Contacts
    with st.expander("🆘 Emergency Contacts"):
        st.markdown("### Crisis Helplines")
        for contact in plan['emergency_contacts']:
            st.markdown(f"**{contact['name']}:** {contact['number']}")

def view_all_plans(username):
    """View all historical coping plans"""
    
    plans = list(coping_plans_col.find(
        {"username": username}
    ).sort("created_at", -1))
    
    if not plans:
        st.info("📚 No plans yet. Generate your first one!")
        return
    
    st.subheader("📚 Your Coping Plans History")
    
    for plan_doc in plans:
        with st.expander(
            f"Plan from {plan_doc['created_at'].strftime('%B %d, %Y')} - "
            f"{plan_doc['intensity']} Intensity"
        ):
            st.markdown(f"**Focus Areas:** {', '.join(plan_doc['focus_areas'])}")
            st.markdown(f"**Based on emotion pattern:** {plan_doc['emotion_pattern'].title()}")
            
            if st.button("🔄 Activate This Plan", key=f"activate_{plan_doc['_id']}"):
                # Deactivate all plans
                coping_plans_col.update_many(
                    {"username": username},
                    {"$set": {"active": False}}
                )
                # Activate selected plan
                coping_plans_col.update_one(
                    {"_id": plan_doc["_id"]},
                    {"$set": {"active": True}}
                )
                st.success("✅ Plan activated!")
                st.rerun()

# -------------------- 📚 RESOURCE LIBRARY --------------------
def resource_library_page(username):
    st.title("📚 Resource Library")
    st.markdown("Access guided sessions, tutorials, and worksheets")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎥 Videos", "🎧 Audio", "📄 Worksheets", "📖 Articles"])
    
    with tab1:
        video_resources(username)
    
    with tab2:
        audio_resources(username)
    
    with tab3:
        worksheet_resources(username)
    
    with tab4:
        article_resources(username)

def video_resources(username):
    st.subheader("🎥 Video Tutorials")
    
    videos = [
        {
            "title": "5-Minute Breathing Exercise",
            "duration": "5:00",
            "category": "Breathing",
            "description": "Quick breathing technique to calm anxiety",
            "url": "https://www.youtube.com/watch?v=tybOi4hjZFQ"
        },
        {
            "title": "Guided Meditation for Beginners",
            "duration": "10:00",
            "category": "Meditation",
            "description": "Perfect for those new to meditation",
            "url": "https://www.youtube.com/watch?v=inpok4MKVLM"
        },
        {
            "title": "Progressive Muscle Relaxation",
            "duration": "15:00",
            "category": "Relaxation",
            "description": "Release physical tension systematically",
            "url": "https://www.youtube.com/watch?v=ihO02wUzgkc"
        },
        {
            "title": "Mindful Walking Tutorial",
            "duration": "8:00",
            "category": "Mindfulness",
            "description": "Turn your walk into a meditation",
            "url": "https://www.youtube.com/watch?v=6p_yaNFSYao"
        },
        {
            "title": "Body Scan Meditation",
            "duration": "20:00",
            "category": "Meditation",
            "description": "Deep relaxation through body awareness",
            "url": "https://www.youtube.com/watch?v=ihO02wUzgkc"
        }
    ]
    
    for video in videos:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {video['title']}")
                st.caption(f"⏱️ {video['duration']} • 🏷️ {video['category']}")
                st.markdown(video['description'])
            
            with col2:
                if st.button("▶️ Watch", key=f"video_{video['title']}"):
                    st.markdown(f"[Open Video]({video['url']})")
                    
                    # Log resource access
                    resources_col.insert_one({
                        "username": username,
                        "type": "video",
                        "title": video['title'],
                        "timestamp": datetime.datetime.utcnow()
                    })
            
            st.markdown("---")

def audio_resources(username):
    st.subheader("🎧 Audio Guided Sessions")
    
    audio_sessions = [
        {
            "title": "Sleep Meditation",
            "duration": "30:00",
            "category": "Sleep",
            "description": "Gentle guidance to help you fall asleep",
            "url": "https://www.youtube.com/watch?v=aEqlQvczMJQ",
            "embed_id": "aEqlQvczMJQ"
        },
        {
            "title": "Anxiety Relief Session",
            "duration": "15:00",
            "category": "Anxiety",
            "description": "Calm your anxious thoughts",
            "url": "https://www.youtube.com/watch?v=O-6f5wQXSu8",
            "embed_id": "O-6f5wQXSu8"
        },
        {
            "title": "Morning Motivation",
            "duration": "10:00",
            "category": "Motivation",
            "description": "Start your day with positivity",
            "url": "https://www.youtube.com/watch?v=ZsTKyYOuK84",
            "embed_id": "ZsTKyYOuK84"
        },
        {
            "title": "Stress Release",
            "duration": "20:00",
            "category": "Stress",
            "description": "Let go of daily stress and tension",
            "url": "https://www.youtube.com/watch?v=inpok4MKVLM",
            "embed_id": "inpok4MKVLM"
        },
        {
            "title": "Self-Compassion Practice",
            "duration": "12:00",
            "category": "Self-Care",
            "description": "Cultivate kindness toward yourself",
            "url": "https://www.youtube.com/watch?v=11U0h0DPu7k",
            "embed_id": "11U0h0DPu7k"
        }
    ]
    
    for audio in audio_sessions:
        with st.expander(f"🎧 {audio['title']} ({audio['duration']})"):
            st.caption(f"🏷️ {audio['category']}")
            st.markdown(audio['description'])
            
            # Embed YouTube video
            st.markdown(
                f"""
                <iframe width="100%" height="200" 
                src="https://www.youtube.com/embed/{audio['embed_id']}" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True
            )
            
            # Log when user opens the expander
            if st.button("✅ Mark as Listened", key=f"audio_{audio['title']}"):
                resources_col.insert_one({
                    "username": username,
                    "type": "audio",
                    "title": audio['title'],
                    "timestamp": datetime.datetime.utcnow()
                })
                st.success("🎉 Great job! Session logged.")
            
            st.markdown("---")

def worksheet_resources(username):
    st.subheader("📄 CBT Worksheets – Guided Exercises ✨")

    worksheets = [
        {
            "title": "Thought Record",
            "category": "CBT",
            "description": "Identify negative thoughts and replace them with balanced ones.",
            "content": """
### 📝 How to use the Thought Record Worksheet
1. **Notice a Negative Thought** 💭  
   - Recall a recent thought that caused stress, worry, or discomfort.  
   - Write it down in clear words.

2. **Identify the Cognitive Distortion** 🔍  
   - Ask yourself: Is this thought all-or-nothing? Overgeneralized? Catastrophizing?  
   - Labeling the distortion helps you see it clearly.

3. **Examine the Evidence** 📊  
   - Look for facts that support this thought.  
   - Look for facts that contradict it.  
   - Balance your perspective by considering both sides.

4. **Create a Balanced Thought** 🌈  
   - Reframe the situation realistically and kindly.  
   - Example: “I struggled in the meeting, but I also shared some good ideas. I am learning and improving.”

5. **Reflect on the Outcome** 🌟  
   - How do you feel after reframing the thought?  
   - Notice changes in mood, tension, or perspective.

💡 Tip: Practice this daily for 5–10 minutes. Over time, your mind naturally starts noticing distortions and reframing automatically. ✨
"""
        },
        {
            "title": "Behavioral Activation",
            "category": "Depression",
            "description": "Plan small positive activities to improve mood.",
            "content": """
### 📝 How to use the Behavioral Activation Worksheet
1. **List Activities You Enjoy or Value** 🎨🏃‍♂️  
   - Write down small activities that bring you joy or purpose, even if it’s simple (e.g., walking, listening to music, calling a friend).

2. **Schedule Your Activities** 📅  
   - Pick 1–3 activities per day.  
   - Write down the time and place so it becomes a concrete plan.

3. **Notice Your Mood Before and After** 🌞  
   - Rate your mood from 1–10 before the activity.  
   - Rate your mood after completing it.  
   - Observe how small positive steps influence your overall mood.

4. **Start Small** 🐾  
   - Begin with achievable tasks.  
   - Small wins create momentum and motivation.

5. **Reflect and Adjust** 🔄  
   - Celebrate completed activities.  
   - Adjust your plan based on what worked and what didn’t.

💡 Tip: Even on low-energy days, doing one small activity can shift your perspective and create a positive ripple effect. 🎉
"""
        },
        {
            "title": "Anxiety Trigger Log",
            "category": "Anxiety",
            "description": "Track what triggers anxiety and how you respond.",
            "content": """
### 📝 How to use the Anxiety Trigger Log
1. **Identify Triggers** ⚠️  
   - Note situations, people, thoughts, or environments that provoke anxiety.  
   - Be specific about the context.

2. **Describe Your Response** 🧠💓  
   - Record your emotional, physical, and behavioral reactions.  
   - Examples: racing heart, shallow breathing, avoidance, rumination.

3. **Rate Anxiety Level** 📊  
   - Use a scale of 1–10 to indicate how strong the anxiety felt.  
   - Helps monitor patterns over time.

4. **Identify Coping Strategies** 🌿  
   - Note what helped calm you or what could help next time.  
   - Examples: deep breathing, mindfulness, grounding techniques, calling a friend.

5. **Reflect and Learn** 📝  
   - Review patterns weekly.  
   - Notice repeated triggers, effective coping strategies, and progress.

💡 Tip: Logging triggers does not make anxiety worse; it gives you insight and control. Knowledge is power! 💪
"""
        },
        {
            "title": "Gratitude Worksheet",
            "category": "Positive",
            "description": "Write down things you are grateful for to shift perspective.",
            "content": """
### 📝 How to use the Gratitude Worksheet
1. **List Three Things Daily** 🌸  
   - Write down at least three things you are grateful for today.  
   - Examples: sunny morning, supportive friend, completed task.

2. **Be Specific** ✨  
   - Avoid generalities like “I’m grateful for life.”  
   - Detail makes the gratitude practice more powerful.

3. **Notice the Why** 💖  
   - Reflect why you are grateful for each item.  
   - Example: “I’m grateful for my friend calling me because it made me feel supported and connected.”

4. **Include People and Moments** 👨‍👩‍👧‍👦  
   - Recognize others’ impact on your life.  
   - Small gestures often bring the most meaning.

5. **Reflect on the Impact** 🌟  
   - After a week, review your entries.  
   - Notice changes in mood, perspective, and stress levels.

💡 Tip: Gratitude rewires your brain to notice positive experiences. It’s a simple yet powerful tool for lasting happiness! 😄
"""
        },
        {
            "title": "Sleep Hygiene Checklist",
            "category": "Sleep",
            "description": "Improve your sleep routine using evidence-based habits.",
            "content": """
### 📝 How to use the Sleep Hygiene Checklist
1. **Set a Consistent Schedule** ⏰  
   - Go to bed and wake up at the same time every day.  
   - Your body thrives on routine.

2. **Create a Sleep-Friendly Environment** 🌙  
   - Keep your bedroom dark, quiet, and cool.  
   - Use blackout curtains or eye masks.  
   - Remove electronic distractions.

3. **Wind Down Before Bed** 🛀  
   - Avoid screens 60 minutes before sleep.  
   - Practice gentle stretching, deep breathing, or light reading.

4. **Limit Stimulants** ☕  
   - Avoid caffeine, nicotine, and heavy meals close to bedtime.

5. **Track Sleep Patterns** 📊  
   - Note bedtime, wake time, and sleep quality.  
   - Identify habits that help or hinder rest.

6. **Practice Relaxation Techniques** 🌿  
   - Meditation, progressive muscle relaxation, or guided audio can calm your mind.

7. **Daytime Habits Matter** 🌞  
   - Regular physical activity improves sleep.  
   - Exposure to sunlight helps regulate your circadian rhythm.

💡 Tip: Good sleep is foundational for mental, emotional, and physical health. Prioritize it, and your mind and body will thank you! 😴✨
"""
        }
    ]

    for ws in worksheets:
        with st.expander(f"📄 {ws['title']}"):
            st.caption(f"🏷️ {ws['category']}")
            st.markdown(ws['description'])
            st.markdown(ws.get('content', '📌 No detailed guide yet.'))

            if st.button("📝 Mark as Completed", key=f"ws_{ws['title']}"):
                resources_col.insert_one({
                    "username": username,
                    "type": "worksheet",
                    "title": ws['title'],
                    "timestamp": datetime.datetime.utcnow()
                })
                st.success("🎉 Worksheet completed and logged!")



def article_resources(username):
    st.subheader("📖 Helpful Articles")
    
    articles = [
        {
            "title": "Understanding Anxiety: A Complete Guide",
            "read_time": "10 min",
            "category": "Education",
            "summary": "Learn about anxiety disorders, symptoms, and evidence-based treatments.",
            "content": """Anxiety is not a weakness. It is not a flaw in your character. It is not a sign that you are broken.
Anxiety is a signal — a deeply human response from your nervous system trying to protect you.

Long ago, anxiety kept humans alive. It prepared the body to react to danger, to run, to fight, or to freeze.
But in the modern world, where threats are psychological, social, and emotional, that same system can become overactive.

When anxiety becomes constant, it stops being protection and starts becoming a burden.

You may feel it as:
A racing mind that never seems to rest.
A tightness in your chest that makes breathing feel shallow.
A constant sense that something is wrong, even when nothing is.
A fear of the future that loops endlessly in your thoughts.

This can be exhausting.
It can be isolating.
It can make you feel like you are fighting an invisible battle every single day.

But here is the truth:
You are not alone.
You are not weak.
And you are not beyond help.

Anxiety is one of the most common mental health experiences in the world.
Millions of people live with it, learn to manage it, and go on to live meaningful, peaceful lives.

Understanding anxiety is the first step toward reducing its power over you.

Anxiety is driven by your nervous system — especially a part called the amygdala.
The amygdala scans your environment for danger.
When it senses a threat, it sends a signal that releases stress hormones like adrenaline and cortisol.

Your heart beats faster.
Your breathing becomes shallow.
Your muscles tense.
Your thoughts become focused on survival.

This is known as the “fight or flight” response.

In short bursts, this system is helpful.
But when it is activated too often or for too long, it creates chronic anxiety.

Your body begins to live as if danger is always present.
Your mind becomes hyper-alert.
Your emotions become harder to regulate.

This is why anxiety is not just “in your head.”
It is in your body.
It is in your nervous system.
It is in your biology.

And because it is biological, it is treatable.

There are many forms of anxiety:
Generalized Anxiety Disorder — constant worry about many areas of life.
Social Anxiety — fear of judgment, embarrassment, or rejection.
Panic Disorder — sudden waves of intense fear and physical symptoms.
Health Anxiety — constant worry about illness or bodily sensations.
Phobias — intense fear of specific situations or objects.

Each type feels different.
But all of them share one core feature:
Your brain is trying to protect you from perceived danger.

The problem is not that your brain is broken.
The problem is that your brain is trying too hard.

Anxiety often grows when we avoid what we fear.
Avoidance gives short-term relief, but it teaches the brain that the threat was real.
So the fear grows stronger.

This is why anxiety can slowly shrink your world.
You stop doing things you once enjoyed.
You cancel plans.
You avoid people, places, or situations.

Your life becomes smaller, not because you want it to — but because anxiety is steering your choices.

The good news is that this pattern can be reversed.

Your brain is plastic — it changes with experience.
Every time you face a fear gently and safely, your brain learns:
“I survived this.”
“I can handle this.”
“This is not as dangerous as I thought.”

This is how healing happens.

There are powerful, evidence-based tools that help reduce anxiety:

Cognitive Behavioral Therapy helps you identify anxious thought patterns and replace them with more balanced ones.
Mindfulness teaches you to observe your thoughts instead of being trapped inside them.
Breathing exercises calm the nervous system and signal safety to the body.
Physical movement helps burn off excess stress hormones.
Healthy sleep restores emotional regulation.
Connection with others reminds your brain that you are safe and supported.

Sometimes medication is helpful — not as a failure, but as a support while you heal.

And perhaps the most important part of healing anxiety is changing how you relate to it.

Instead of fighting anxiety, you learn to understand it.
Instead of fearing fear, you learn to tolerate it.
Instead of judging yourself, you learn to show compassion.

You learn to say:
“This is uncomfortable, but I am safe.”
“This feeling will rise, and this feeling will fall.”
“I do not have to control everything to be okay.”

With time, patience, and practice, anxiety loses its grip.
It does not vanish overnight.
But it softens.
It quiets.
It becomes manageable.

And you become stronger — not because anxiety disappears, but because you learn you can live well even when it appears.

Your life is bigger than your fear.
Your future is not defined by your anxiety.
Your nervous system can learn peace again.

And step by step, breath by breath, moment by moment —
You are moving toward that peace.

You are not broken.
You are human.
And you are healing.
"""

        },
        {
            "title": "10 Science-Backed Ways to Reduce Stress",
            "read_time": "7 min",
            "category": "Tips",
            "summary": "Practical, research-supported strategies for stress management.",
            "content": """Stress is not a sign that you are failing.
Stress is a sign that you are human.

Your body was designed to respond to challenge with energy, focus, and alertness.
But when stress becomes constant, your nervous system never gets the message that it is safe to rest.

Your mind becomes tired.
Your body becomes tense.
Your emotions become harder to regulate.
Your joy becomes quieter.

Stress slowly drains you — not because you are weak, but because your system was never meant to run at full speed all the time.

The good news is this:
Your body also has a built-in system for calm.
You can activate it intentionally.

Here are 10 science-backed ways to reduce stress and restore balance.

1. Slow, deep breathing.
When you slow your breath, you directly signal safety to your nervous system.
Long exhalations activate the parasympathetic nervous system — the part responsible for rest and recovery.
Even five slow breaths can reduce cortisol and heart rate.

2. Move your body gently and regularly.
Exercise is one of the most effective stress regulators.
It releases endorphins, improves sleep, and burns off excess adrenaline.
This does not mean intense workouts only — walking, stretching, yoga, or dancing all count.

3. Spend time in nature.
Research shows that being in green spaces lowers stress hormones, reduces rumination, and improves mood.
Even looking at trees through a window has a calming effect on the brain.

4. Practice mindfulness.
Mindfulness trains your brain to stay in the present moment instead of looping through worries about the future.
It reduces activity in the brain’s fear center and strengthens emotional regulation.

5. Improve sleep quality.
Sleep is when your nervous system resets.
Poor sleep increases emotional reactivity and stress sensitivity.
Creating a consistent sleep routine can dramatically improve stress levels.

6. Limit caffeine and stimulants.
Caffeine activates the same system involved in anxiety and stress.
Reducing intake can significantly lower baseline tension in the body.

7. Connect with others.
Human connection is a powerful stress buffer.
Feeling seen, heard, and supported reduces cortisol and increases oxytocin — the hormone of safety and bonding.

8. Write your thoughts down.
Journaling reduces mental load by moving thoughts from your mind onto paper.
This creates clarity and reduces rumination.

9. Practice self-compassion.
Harsh self-criticism keeps the stress response activated.
Speaking to yourself with kindness tells your brain that you are safe, even when things are imperfect.

10. Accept what you cannot control.
Stress often comes from trying to control what is uncertain.
Letting go is not giving up — it is choosing peace over constant struggle.

Stress does not mean something is wrong with you.
It means your system is asking for care.

You are not meant to be calm all the time.
But you are meant to feel safe in your own body.

By practicing these tools gently and consistently, you teach your nervous system that the world is not always an emergency.
You give your mind permission to rest.
You give your body permission to soften.

And from that softness, clarity grows.
Energy returns.
Joy becomes easier to access.

Stress is not your enemy.
It is a message.

And you are learning how to listen — and how to respond with care.
"""

        },
        {
            "title": "The Power of Mindfulness",
            "read_time": "8 min",
            "category": "Mindfulness",
            "summary": "How mindfulness can transform your mental health.",
            "content": """Mindfulness is not about stopping your thoughts.
It is not about becoming calm all the time.
It is not about emptying your mind or being “perfectly present.”

Mindfulness is about learning how to be with your experience — exactly as it is — without judgment.

It is the practice of noticing what is happening inside you and around you with kindness and curiosity.

Your thoughts.
Your emotions.
Your bodily sensations.
Your breath.
Your environment.

Without pushing them away.
Without clinging to them.
Without criticizing yourself for having them.

And this simple shift changes everything.

Because most suffering does not come from pain itself.
It comes from our resistance to pain.
Our fear of it.
Our stories about it.
Our desire to escape it.

Mindfulness gently teaches you:
“You do not need to fight your experience to be okay.”

From a scientific perspective, mindfulness reshapes the brain.

Studies show that regular mindfulness practice:
Reduces activity in the amygdala (the brain’s fear center).
Strengthens the prefrontal cortex (responsible for emotional regulation).
Improves attention and focus.
Reduces rumination and worry.
Increases emotional resilience.

In simple words:
It helps your brain become calmer, clearer, and kinder.

But beyond science, mindfulness changes how life feels.

It turns automatic reactions into conscious responses.
It creates space between a feeling and an action.
It gives you the freedom to choose how you show up.

Instead of being pulled by every thought, you learn to observe them.
Instead of being overwhelmed by every emotion, you learn to hold them.
Instead of being lost in the past or anxious about the future, you return to now.

And in this moment — this breath, this body, this awareness — you find stability.

Mindfulness begins with the breath.
Not because breathing is magical, but because it is always here.

You may not always feel calm.
You may not always feel happy.
But you can always feel your breath.

And every time you notice it, you anchor yourself in the present.

Over time, this changes your relationship with your inner world.

You stop fearing your thoughts.
You stop running from your emotions.
You stop judging yourself for being human.

You learn that thoughts are just thoughts.
Emotions are just emotions.
Sensations rise and fall like waves.

You are the ocean, not the waves.

This is what gives mindfulness its power.

It does not remove pain from life.
But it removes the extra suffering we create around pain.

It does not promise happiness.
But it creates peace even when happiness is absent.

It does not change your external circumstances.
But it changes how you experience them.

And that changes everything.

Mindfulness teaches you to meet yourself with compassion.
To treat your inner experience with the same kindness you would offer a dear friend.
To stop being your own harshest critic.
To become your own safe place.

This is not weakness.
This is strength.

Because only a strong mind can be gentle.
Only a brave heart can stay present with discomfort.
Only a wise soul can choose awareness over avoidance.

Every moment of mindfulness is a moment of freedom.
Freedom from automatic reactions.
Freedom from old patterns.
Freedom from unnecessary suffering.

And with practice, that freedom grows.

You do not have to be perfect.
You do not have to meditate for hours.
You do not have to do this “right.”

You only have to begin.

One breath.
One moment.
One act of awareness at a time.

And slowly, gently, quietly —
Your relationship with yourself changes.
Your relationship with your mind changes.
Your relationship with your life changes.

That is the power of mindfulness.
"""

        },
        {
            "title": "Cognitive Distortions and How to Combat Them",
            "read_time": "12 min",
            "category": "CBT",
            "summary": "Identify and challenge unhelpful thinking patterns.",
            "content": """Our minds are powerful, but they can also play tricks on us.  
Cognitive distortions are biased ways of thinking that cause us to see reality inaccurately.  
They fuel anxiety, depression, stress, and self-doubt — often without us even noticing.

Some common distortions include:

1. **All-or-Nothing Thinking**  
   Seeing things in black or white, with no middle ground.  
   “If I fail this task, I’m a complete failure.”

2. **Overgeneralization**  
   Taking one event and assuming it defines everything.  
   “I didn’t do well today, so I’ll never succeed.”

3. **Mental Filtering**  
   Focusing solely on negative details, ignoring positives.  
   “I made a mistake in the presentation, so the whole talk was awful.”

4. **Disqualifying the Positive**  
   Dismissing your achievements or compliments.  
   “They said I did a good job, but they were just being polite.”

5. **Jumping to Conclusions**  
   Making assumptions without evidence:  
   - Mind reading: “They think I’m incompetent.”  
   - Fortune telling: “This will end badly.”

6. **Catastrophizing**  
   Exaggerating the negative outcome.  
   “If I make a small mistake, it will ruin everything.”

7. **Emotional Reasoning**  
   Believing feelings reflect facts.  
   “I feel guilty, so I must have done something wrong.”

8. **Should Statements**  
   Setting unrealistic expectations for yourself or others.  
   “I should always be productive. I must never fail.”

9. **Labeling**  
   Attaching a negative label to yourself or others.  
   “I’m useless.” “They’re a bad person.”

10. **Personalization**  
    Taking responsibility for events beyond your control.  
    “It’s my fault that the team missed the deadline.”

---

### How to Combat Cognitive Distortions

**1. Awareness is Key**  
Start noticing when your thoughts become distorted. Awareness is the first step toward change.

**2. Challenge the Thought**  
Ask yourself:  
- What is the evidence for this thought?  
- Is there another way to view this situation?  
- Would I say this to a friend?

**3. Reframe Positively**  
Replace distortions with balanced, realistic thoughts.  
- Instead of: “I always fail,” try: “Sometimes I struggle, but I also succeed.”

**4. Record and Reflect**  
Maintain a thought diary. Write down your negative thoughts, the distortion, and a rational counter-thought.

**5. Practice Self-Compassion**  
Mistakes do not define you. Treat yourself with the kindness you would show a friend.

**6. Use Mindfulness**  
Observe your thoughts without judgment. Let them pass rather than reacting automatically.

**7. Seek Evidence**  
Challenge assumptions by looking for proof. Facts often contradict distorted thoughts.

**8. Gradual Exposure**  
Face situations you fear instead of avoiding them. This weakens distorted thinking over time.

**9. Cognitive Behavioral Exercises**  
- Thought records  
- Behavioral experiments  
- Challenging core beliefs  

**10. Professional Support**  
CBT therapists can guide you in identifying distortions and building healthier thinking patterns.

---

### Why This Matters

Cognitive distortions shape your reality.  
They influence your emotions, behaviors, and decisions.  
By recognizing and challenging them, you:

- Reduce anxiety and stress  
- Improve mood and self-esteem  
- Make clearer, rational decisions  
- Build resilience and emotional intelligence  

Your mind is not your enemy.  
It is a tool. And like any tool, it works best when sharpened and guided.  

Transforming your thoughts transforms your life.
"""

        },
        {
            "title": "Building Healthy Sleep Habits",
            "read_time": "6 min",
            "category": "Sleep",
            "summary": "Create a sleep routine that works for you.",
            "content": """Sleep is not just a break from life—it’s a critical pillar of mental, emotional, and physical health.  
Yet in today’s fast-paced world, many struggle to get restorative rest.  
Building healthy sleep habits can transform your energy, mood, and overall wellbeing.

---

### Why Sleep Matters

- **Brain Function:** Sleep enhances memory, learning, and decision-making.  
- **Emotional Health:** Proper rest reduces irritability, anxiety, and depression.  
- **Physical Health:** Supports immune function, metabolism, and heart health.  
- **Energy & Focus:** Restorative sleep fuels productivity and creativity.

---

### Common Sleep Challenges

- Trouble falling asleep  
- Waking up frequently at night  
- Feeling tired despite adequate hours  
- Insomnia caused by stress or overthinking  

---

### Science-Backed Ways to Improve Sleep

1. **Set a Consistent Sleep Schedule**  
   Go to bed and wake up at the same time every day—even on weekends.  
   Your body thrives on routine.

2. **Create a Sleep-Inducing Environment**  
   - Keep your bedroom dark, cool, and quiet  
   - Use blackout curtains or eye masks  
   - Remove electronic distractions

3. **Limit Screen Time Before Bed**  
   The blue light from phones, tablets, and TVs interferes with melatonin production.  
   Aim for at least 60 minutes of screen-free time before sleep.

4. **Wind Down with a Nighttime Routine**  
   - Gentle stretching or yoga  
   - Deep breathing exercises  
   - Journaling or gratitude reflections  
   - Reading a physical book  

5. **Mind Your Diet and Beverages**  
   - Avoid caffeine and nicotine in the evening  
   - Limit heavy meals before bedtime  
   - Consider herbal teas like chamomile or lavender

6. **Stay Active During the Day**  
   Regular physical activity improves sleep quality, but avoid intense exercise right before bed.

7. **Manage Stress and Anxiety**  
   Mindfulness, meditation, and cognitive-behavioral strategies help calm racing thoughts at night.

8. **Use the Bed for Sleep Only**  
   Avoid working, scrolling, or watching TV in bed.  
   This strengthens the mental association between bed and sleep.

9. **Expose Yourself to Natural Light**  
   Morning sunlight helps regulate your circadian rhythm, signaling your body when to wake and sleep.

10. **Limit Naps**  
    Short naps (20–30 minutes) are fine, but long or late-day naps can interfere with nighttime sleep.

---

### Tips for a Powerful Sleep Routine

- Stick to a fixed “wind-down” ritual every night  
- Track sleep patterns in a journal or app  
- Listen to relaxing audio like guided meditations or nature sounds  
- Practice gratitude or visualization to calm the mind  

---

### Transform Your Life, One Night at a Time

Healthy sleep is the foundation of a thriving mind and body.  
Small changes—like dimming lights, setting a bedtime, or practicing mindfulness—create big results over time.  

By committing to consistent sleep habits, you unlock:

- Better emotional resilience  
- Clearer thinking and focus  
- Stronger immunity  
- A more balanced, joyful life  

Sleep well, live well, thrive.
"""

        }
    ]
    
    for article in articles:
        with st.expander(f"📖 {article['title']} ({article['read_time']} read)"):
            st.caption(f"🏷️ {article['category']}")
            st.markdown(article['summary'])
            
            if st.button("📚 Read Full Article", key=f"article_{article['title']}"):
                #st.info("📖 Full article would open here!")
                st.markdown(article.get('content', 'Full content not available.'))
                
                resources_col.insert_one({
                    "username": username,
                    "type": "article",
                    "title": article['title'],
                    "timestamp": datetime.datetime.utcnow()
                })

# -------------------- 🎮 INTERACTIVE TOOLS --------------------
def interactive_tools_page(username):
    st.title("🎮 Interactive Wellness Tools")
    st.markdown("Creative tools to support your mental health journey")
    
    tab1, tab2, tab3 = st.tabs(["🎨 Mood Board", "🙏 Gratitude Jar", "📦 Worry Box"])
    
    with tab1:
        mood_board_tool(username)
    
    with tab2:
        gratitude_jar_tool(username)
    
    with tab3:
        worry_box_tool(username)

def mood_board_tool(username):
    st.subheader("🎨 Mood Board Creator")
    st.markdown("Express your emotions visually through colors, words, and symbols")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Current mood
        current_mood = st.select_slider(
            "How are you feeling right now?",
            options=["😢 Very Sad", "😔 Down", "😐 Neutral", "🙂 Good", "😊 Great"],
            value="😐 Neutral"
        )
        
        # Color selection
        mood_color = st.color_picker("Pick a color that represents your mood:", "#FF6B6B")
        
        # Words/phrases
        mood_words = st.text_area(
            "Add words or phrases that describe your feelings:",
            placeholder="peaceful, hopeful, anxious, calm..."
        )
        
        # Emoji selection
        selected_emojis = st.multiselect(
            "Add emojis to your board:",
            ["😊", "😢", "😠", "😰", "🌟", "💪", "🌈", "☀️", "🌙", "💚", "🦋", "🌸"]
        )
        
        if st.button("💾 Save Mood Board", use_container_width=True):
            mood_board = {
                "username": username,
                "mood": current_mood,
                "color": mood_color,
                "words": mood_words,
                "emojis": selected_emojis,
                "timestamp": datetime.datetime.utcnow()
            }
            
            mood_board_col.insert_one(mood_board)
            st.success("✅ Mood board saved! Check your gallery below.")
            st.rerun()
    
    with col2:
        st.markdown("### 💡 Tips")
        st.info("""
        **Mood boarding helps:**
        - Express complex emotions
        - Track emotional patterns
        - Increase self-awareness
        - Process feelings creatively
        """)
    
    # Gallery of past mood boards
    st.markdown("---")
    st.markdown("### 🖼️ Your Mood Board Gallery")
    
    past_boards = list(mood_board_col.find(
        {"username": username}
    ).sort("timestamp", -1).limit(12))
    
    if past_boards:
        cols = st.columns(3)
        
        for idx, board in enumerate(past_boards):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div style='background-color: {board['color']}; 
                                padding: 20px; border-radius: 10px; 
                                text-align: center; min-height: 150px;'>
                        <div style='font-size: 2rem;'>{board['mood'].split()[0]}</div>
                        <div style='margin: 10px 0;'>{' '.join(board.get('emojis', []))}</div>
                        <div style='font-size: 0.8rem; color: #333;'>
                            {board['timestamp'].strftime('%b %d')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.expander("View details"):
                    st.markdown(f"**Mood:** {board['mood']}")
                    if board.get('words'):
                        st.markdown(f"**Words:** {board['words']}")
    else:
        st.info("🎨 Create your first mood board above!")

def gratitude_jar_tool(username):
    st.subheader("🙏 Gratitude Jar")
    st.markdown("Fill your virtual jar with things you're grateful for")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Add gratitude
        gratitude_text = st.text_area(
            "What are you grateful for today?",
            placeholder="I'm grateful for...",
            height=100
        )
        
        category = st.selectbox(
            "Category:",
            ["🤝 People", "🌟 Experience", "💪 Personal Growth", 
             "🏠 Home & Comfort", "🌍 Nature", "💼 Work", "💚 Health", "🎨 Creativity"]
        )
        
        if st.button("🙏 Add to Jar", use_container_width=True):
            if gratitude_text:
                gratitude_jar_col.insert_one({
                    "username": username,
                    "text": gratitude_text,
                    "category": category,
                    "timestamp": datetime.datetime.utcnow()
                })
                st.success("✅ Added to your gratitude jar!")
                st.balloons()
                st.rerun()
            else:
                st.warning("⚠️ Please write something you're grateful for")
    
    with col2:
        # Jar visualization
        jar_count = gratitude_jar_col.count_documents({"username": username})
        
        st.markdown("### 🏺 Your Jar")
        st.markdown(
            f"""
            <div style='text-align: center; padding: 30px; 
                        background: linear-gradient(180deg, rgba(255,215,0,0.3) 0%, rgba(255,165,0,0.5) 100%);
                        border-radius: 20px; border: 3px solid #FFD700;'>
                <div style='font-size: 4rem;'>🏺</div>
                <div style='font-size: 2rem; font-weight: bold; color: #FF8C00;'>{jar_count}</div>
                <div style='color: #666;'>gratitude notes</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # View gratitudes
    st.markdown("---")
    st.markdown("### 📖 Your Gratitude Collection")
    
    # Filter by category
    filter_category = st.selectbox(
        "Filter by category:",
        ["All"] + ["🤝 People", "🌟 Experience", "💪 Personal Growth", 
                   "🏠 Home & Comfort", "🌍 Nature", "💼 Work", "💚 Health", "🎨 Creativity"],
        key="gratitude_filter"
    )
    
    # Get gratitudes
    query = {"username": username}
    if filter_category != "All":
        query["category"] = filter_category
    
    gratitudes = list(gratitude_jar_col.find(query).sort("timestamp", -1).limit(20))
    
    if gratitudes:
        for gratitude in gratitudes:
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"**{gratitude['category']}** • {gratitude['timestamp'].strftime('%b %d, %Y')}")
                    st.markdown(f"_{gratitude['text']}_")
                
                with col2:
                    if st.button("🗑️", key=f"del_grat_{gratitude['_id']}"):
                        gratitude_jar_col.delete_one({"_id": gratitude["_id"]})
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("🙏 Start adding gratitude notes to fill your jar!")

def worry_box_tool(username):
    st.subheader("📦 Worry Box")
    st.markdown("Write down your worries and store them away - revisit them later with perspective")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Add worry
        worry_text = st.text_area(
            "What's worrying you?",
            placeholder="Write your worry here...",
            height=120
        )
        
        worry_intensity = st.select_slider(
            "How intense is this worry?",
            options=["😌 Mild", "😟 Moderate", "😰 Severe", "😱 Overwhelming"],
            value="😟 Moderate"
        )
        
        can_control = st.radio(
            "Can you control this?",
            ["✅ Yes, I can take action", "❌ No, it's out of my control"],
            horizontal=True
        )
        
        if st.button("📦 Put in Worry Box", use_container_width=True):
            if worry_text:
                worry_box_col.insert_one({
                    "username": username,
                    "text": worry_text,
                    "intensity": worry_intensity,
                    "controllable": can_control,
                    "status": "active",
                    "created_at": datetime.datetime.utcnow(),
                    "resolved_at": None
                })
                st.success("✅ Worry stored in your box. You can come back to it later.")
                st.rerun()
            else:
                st.warning("⚠️ Please write your worry first")
    
    with col2:
        st.markdown("### 💡 How it Works")
        st.info("""
        1. **Write** your worry down
        2. **Store** it in the box
        3. **Let go** for now
        4. **Revisit** later with fresh perspective
        5. **Resolve** or release it
        """)
        
        # Box visualization
        active_worries = worry_box_col.count_documents({
            "username": username,
            "status": "active"
        })
        
        st.markdown(
            f"""
            <div style='text-align: center; padding: 30px; 
                        background: linear-gradient(180deg, rgba(156,136,255,0.2) 0%, rgba(99,102,241,0.3) 100%);
                        border-radius: 15px; border: 3px solid #6366F1;'>
                <div style='font-size: 4rem;'>📦</div>
                <div style='font-size: 2rem; font-weight: bold; color: #4F46E5;'>{active_worries}</div>
                <div style='color: #666;'>active worries</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # View worries
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📦 Active Worries", "✅ Resolved", "📊 Worry Insights"])
    
    with tab1:
        display_active_worries(username)
    
    with tab2:
        display_resolved_worries(username)
    
    with tab3:
        worry_insights(username)

def display_active_worries(username):
    st.markdown("### 📦 Your Active Worries")
    
    worries = list(worry_box_col.find({
        "username": username,
        "status": "active"
    }).sort("created_at", -1))
    
    if not worries:
        st.success("🎉 Your worry box is empty! That's great!")
        return
    
    for worry in worries:
        with st.expander(
            f"{worry['intensity'].split()[0]} • "
            f"{worry['created_at'].strftime('%b %d, %Y')} • "
            f"{worry['controllable'].split()[0]}"
        ):
            st.markdown(f"**Worry:** {worry['text']}")
            st.markdown(f"**Intensity:** {worry['intensity']}")
            st.markdown(f"**Can Control:** {worry['controllable']}")
            st.caption(f"Added {worry['created_at'].strftime('%B %d, %Y at %I:%M %p')}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Mark Resolved", key=f"resolve_{worry['_id']}"):
                    worry_box_col.update_one(
                        {"_id": worry["_id"]},
                        {
                            "$set": {
                                "status": "resolved",
                                "resolved_at": datetime.datetime.utcnow()
                            }
                        }
                    )
                    st.success("Worry resolved! 🎉")
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", key=f"delete_{worry['_id']}"):
                    worry_box_col.delete_one({"_id": worry["_id"]})
                    st.rerun()
            
            with col3:
                # Suggest coping strategy
                if worry['controllable'].startswith("✅"):
                    st.info("💡 Create an action plan!")
                else:
                    st.info("💡 Practice acceptance")

def display_resolved_worries(username):
    st.markdown("### ✅ Resolved Worries")
    
    resolved = list(worry_box_col.find({
        "username": username,
        "status": "resolved"
    }).sort("resolved_at", -1).limit(20))
    
    if not resolved:
        st.info("No resolved worries yet. Keep working through your active worries!")
        return
    
    for worry in resolved:
        with st.expander(f"✅ {worry['created_at'].strftime('%b %d')} → {worry['resolved_at'].strftime('%b %d')}"):
            st.markdown(f"**Worry:** {worry['text']}")
            
            days_to_resolve = (worry['resolved_at'] - worry['created_at']).days
            st.caption(f"Resolved in {days_to_resolve} day(s)")

def worry_insights(username):
    st.markdown("### 📊 Worry Patterns & Insights")
    
    all_worries = list(worry_box_col.find({"username": username}))
    
    if not all_worries:
        st.info("Start using the worry box to see insights!")
        return
    
    df = pd.DataFrame(all_worries)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(all_worries)
        st.metric("Total Worries", total)
    
    with col2:
        active = len([w for w in all_worries if w['status'] == 'active'])
        st.metric("Active", active)
    
    with col3:
        resolved = len([w for w in all_worries if w['status'] == 'resolved'])
        st.metric("Resolved", resolved)
    
    with col4:
        if resolved > 0:
            resolution_rate = (resolved / total) * 100
            st.metric("Resolution Rate", f"{resolution_rate:.0f}%")
    
    # Intensity distribution
    st.markdown("---")
    st.markdown("#### Worry Intensity Distribution")
    
    intensity_counts = df['intensity'].value_counts()
    
    fig_intensity = px.pie(
        values=intensity_counts.values,
        names=intensity_counts.index,
        title="Distribution of Worry Intensity"
    )
    st.plotly_chart(fig_intensity, use_container_width=True)
    
    # Controllable vs Uncontrollable
    st.markdown("#### Controllable vs Uncontrollable Worries")
    
    controllable_counts = df['controllable'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        can_control = sum([1 for w in all_worries if w['controllable'].startswith('✅')])
        cannot_control = sum([1 for w in all_worries if w['controllable'].startswith('❌')])
        
        st.metric("Can Control", can_control, help="Worries you can take action on")
        st.metric("Cannot Control", cannot_control, help="Worries outside your control")
    
    with col2:
        st.info("""
        **💡 Insight:**
        
        Focus energy on controllable worries. 
        For uncontrollable ones, practice 
        acceptance and letting go.
        """)

# -------------------- MAIN PHASE 3 ROUTER --------------------
def phase3_main(username, page):
    """
    Main router for Phase 3 features
    
    Args:
        username: Current logged-in user
        page: Which page to display
    """
    
    if page == "🎯 Coping Plans":
        coping_plans_page(username)
    
    elif page == "📚 Resource Library":
        resource_library_page(username)
    
    elif page == "🎮 Interactive Tools":
        interactive_tools_page(username)

# -------------------- INTEGRATION INSTRUCTIONS --------------------
"""
HOW TO INTEGRATE PHASE 3 WITH YOUR MAIN APP:

1. Save this file as: phase3_interventions.py

2. Import in your final.py (at the top):
   
   import phase3_interventions as phase3

3. Add Phase 3 pages to sidebar navigation (in chat_page function):
   
   page = st.radio("📍 Navigate", [
       "💬 Chat", 
       " virtual_chat",
       "📊 Analytics", 
       "ℹ️ Resources",
       "🗓️ Mood Journal",
       "🎯 Goals",
       "📚 Exercises",
       "🏆 Achievements",
       "🔔 Reminders",
       "🎯 Coping Plans",      # NEW - Phase 3
       "📚 Resource Library",  # NEW - Phase 3
       "🎮 Interactive Tools"  # NEW - Phase 3
   ])

4. Update routing in chat_page function:
   
   # Phase 3 routing
   if page in ["🎯 Coping Plans", "📚 Resource Library", "🎮 Interactive Tools"]:
       phase3.phase3_main(st.session_state.username, page)
   # Phase 2 routing
   elif page in ["🗓️ Mood Journal", "🎯 Goals", "📚 Exercises", 
                 "🏆 Achievements", "🔔 Reminders"]:
       phase2.phase2_main(st.session_state.username, page)
   # Original pages
   elif page == "💬 Chat":
       chat_interface()
   elif page == "📊 Analytics":
       analytics_page()
   else:
       resources_page()

PHASE 3 FEATURES INCLUDED:
✅ Personalized Coping Plans (based on user data)
✅ Custom Breathing Exercises
✅ Daily Schedule Generator
✅ Video Tutorial Library
✅ Audio Guided Sessions
✅ CBT Worksheets
✅ Educational Articles
✅ Mood Board Creator (visual expression)
✅ Gratitude Jar (positivity building)
✅ Worry Box (worry management)
✅ Comprehensive insights and analytics

All features use your existing MongoDB database!
"""
