import streamlit as st
import json, datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar

from db import get_db

db = get_db()


# Collections for Phase 2
mood_journal_col = db["mood_journal"]
goals_col = db["goals"]
exercises_col = db["exercises"]
achievements_col = db["achievements"]
reminders_col = db["reminders"]

# -------------------- 🗓️ MOOD JOURNAL --------------------
def mood_journal_page(username):
    st.title("🗓️ Daily Mood Journal")
    st.markdown("Track your emotions and identify patterns over time")
    
    tab1, tab2, tab3 = st.tabs(["📝 New Entry", "📊 Mood History", "🔥 Heatmap"])
    
    with tab1:
        new_mood_entry(username)
    
    with tab2:
        mood_history(username)
    
    with tab3:
        mood_heatmap(username)

def new_mood_entry(username):
    st.subheader("How are you feeling today?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Mood selector with emojis
        mood_options = {
            "😊 Great": 5,
            "🙂 Good": 4,
            "😐 Okay": 3,
            "😔 Down": 2,
            "😢 Struggling": 1
        }
        
        selected_mood = st.radio(
            "Select your mood:",
            options=list(mood_options.keys()),
            horizontal=True
        )
        
        # Detailed emotions
        emotions = st.multiselect(
            "What emotions are you experiencing?",
            ["Joy", "Calm", "Energetic", "Anxious", "Sad", "Angry", 
             "Stressed", "Hopeful", "Lonely", "Content", "Frustrated", "Grateful"]
        )
        
        # Notes and triggers
        notes = st.text_area(
            "What's on your mind? (Optional)",
            placeholder="Write about your day, thoughts, or anything you'd like to remember..."
        )
        
        triggers = st.text_input(
            "Any triggers or important events?",
            placeholder="E.g., work deadline, social event, exercise..."
        )
        
    with col2:
        st.markdown("### 💡 Quick Tips")
        st.info("""
        **Benefits of Journaling:**
        - Identify mood patterns
        - Recognize triggers
        - Track progress
        - Process emotions
        """)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Save Entry", use_container_width=True):
            entry = {
                "username": username,
                "mood": selected_mood,
                "mood_score": mood_options[selected_mood],
                "emotions": emotions,
                "notes": notes,
                "triggers": triggers,
                "timestamp": datetime.datetime.utcnow(),
                "date": datetime.datetime.utcnow().date().isoformat()
            }
            
            # Check if entry exists for today
            existing = mood_journal_col.find_one({
                "username": username,
                "date": entry["date"]
            })
            
            if existing:
                mood_journal_col.update_one(
                    {"_id": existing["_id"]},
                    {"$set": entry}
                )
                st.success("✅ Today's entry updated!")
            else:
                mood_journal_col.insert_one(entry)
                st.success("✅ Entry saved successfully!")
                
                # Check for streak achievement
                check_journal_streak(username)
            
            st.rerun()

def mood_history(username):
    entries = list(mood_journal_col.find(
        {"username": username}
    ).sort("timestamp", -1).limit(30))
    
    if not entries:
        st.info("📝 No entries yet. Start journaling to see your history!")
        return
    
    df = pd.DataFrame(entries)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Mood trend chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['mood_score'],
        mode='lines+markers',
        name='Mood Score',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title='Your Mood Journey (Last 30 Days)',
        xaxis_title='Date',
        yaxis_title='Mood Score',
        yaxis=dict(range=[0, 6], ticktext=['', 'Struggling', 'Down', 'Okay', 'Good', 'Great'], 
                   tickvals=[0, 1, 2, 3, 4, 5]),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_mood = df['mood_score'].mean()
        st.metric("Average Mood", f"{avg_mood:.1f}/5")
    
    with col2:
        trend = "📈" if df['mood_score'].iloc[0] > df['mood_score'].iloc[-1] else "📉"
        st.metric("Recent Trend", trend)
    
    with col3:
        best_day = df.loc[df['mood_score'].idxmax(), 'timestamp'].strftime('%b %d')
        st.metric("Best Day", best_day)
    
    with col4:
        entries_count = len(entries)
        st.metric("Total Entries", entries_count)
    
    # Recent entries
    st.markdown("---")
    st.subheader("📖 Recent Entries")
    
    for entry in entries[:10]:
        with st.expander(f"{entry['mood']} - {entry['timestamp'].strftime('%b %d, %Y')}"):
            if entry.get('emotions'):
                st.markdown(f"**Emotions:** {', '.join(entry['emotions'])}")
            if entry.get('notes'):
                st.markdown(f"**Notes:** {entry['notes']}")
            if entry.get('triggers'):
                st.markdown(f"**Triggers:** {entry['triggers']}")

def mood_heatmap(username):
    st.subheader("🔥 Mood Calendar Heatmap")
    
    # Get last 90 days
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=90)
    
    entries = list(mood_journal_col.find({
        "username": username,
        "timestamp": {"$gte": start_date}
    }))
    
    if not entries:
        st.info("📅 Start journaling to see your mood heatmap!")
        return
    
    # Create heatmap data
    df = pd.DataFrame(entries)
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    # Generate calendar grid
    today = datetime.date.today()
    dates = pd.date_range(start=today - datetime.timedelta(days=90), end=today, freq='D')
    
    heatmap_data = []
    for date in dates:
        date_str = date.date()
        entry = df[df['date'] == date_str]
        score = entry['mood_score'].values[0] if len(entry) > 0 else 0
        
        heatmap_data.append({
            'date': date_str,
            'weekday': date.dayofweek,
            'week': date.isocalendar()[1],
            'score': score
        })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    # Create pivot table
    pivot = heatmap_df.pivot(index='weekday', columns='week', values='score')
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        colorscale=[
            [0, '#f0f0f0'],
            [0.2, '#ffcccb'],
            [0.4, '#ffb6c1'],
            [0.6, '#90ee90'],
            [0.8, '#98fb98'],
            [1.0, '#00ff00']
        ],
        colorbar=dict(title="Mood")
    ))
    
    fig.update_layout(
        title='90-Day Mood Heatmap',
        xaxis_title='Week Number',
        yaxis_title='Day of Week',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.markdown("### 📊 Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        best_day = heatmap_df.groupby('weekday')['score'].mean().idxmax()
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        st.info(f"🌟 Your best day is typically **{days[best_day]}**")
    
    with col2:
        consistency = (heatmap_df['score'] > 0).sum() / len(heatmap_df) * 100
        st.info(f"📝 You've journaled **{consistency:.0f}%** of days")

# -------------------- 🎯 GOAL TRACKING --------------------
def goal_tracking_page(username):
    st.title("🎯 Wellness Goals")
    st.markdown("Set and track your personal wellness objectives")
    
    tab1, tab2 = st.tabs(["🎯 My Goals", "➕ New Goal"])
    
    with tab1:
        display_goals(username)
    
    with tab2:
        create_goal(username)

def create_goal(username):
    st.subheader("Create a New Goal")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        goal_types = {
            "🏃 Exercise": "exercise",
            "🧘 Meditation": "meditation",
            "👥 Social": "social",
            "😴 Sleep": "sleep",
            "💧 Hydration": "hydration",
            "📚 Learning": "learning",
            "🎨 Creative": "creative"
        }
        
        goal_type = st.selectbox("Goal Type", list(goal_types.keys()))
        goal_name = st.text_input("Goal Name", placeholder="E.g., Exercise 3 times a week")
        
        col_a, col_b = st.columns(2)
        with col_a:
            target_value = st.number_input("Target Value", min_value=1, value=3)
        with col_b:
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
        
        notes = st.text_area("Notes (Optional)", placeholder="Why is this goal important to you?")
        
        if st.button("🎯 Create Goal", use_container_width=True):
            goal = {
                "username": username,
                "type": goal_types[goal_type],
                "name": goal_name,
                "target": target_value,
                "frequency": frequency,
                "current": 0,
                "notes": notes,
                "created_at": datetime.datetime.utcnow(),
                "status": "active"
            }
            
            goals_col.insert_one(goal)
            st.success("✅ Goal created successfully!")
            st.rerun()
    
    with col2:
        st.markdown("### 💡 Goal Tips")
        st.info("""
        **SMART Goals:**
        - Specific
        - Measurable
        - Achievable
        - Relevant
        - Time-bound
        """)

def display_goals(username):
    goals = list(goals_col.find({
        "username": username,
        "status": "active"
    }))
    
    if not goals:
        st.info("🎯 No active goals. Create your first goal to get started!")
        return
    
    for goal in goals:
        progress = min((goal['current'] / goal['target']) * 100, 100)
        
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {goal['name']}")
                st.progress(progress / 100)
                st.caption(f"{goal['current']}/{goal['target']} • {goal['frequency']}")
            
            with col2:
                if st.button("➕", key=f"inc_{goal['_id']}", help="Increment"):
                    goals_col.update_one(
                        {"_id": goal["_id"]},
                        {"$inc": {"current": 1}}
                    )
                    
                    # Check if goal completed
                    if goal['current'] + 1 >= goal['target']:
                        unlock_achievement(username, "goal_completed")
                    
                    st.rerun()
            
            with col3:
                if st.button("✅", key=f"complete_{goal['_id']}", help="Mark Complete"):
                    goals_col.update_one(
                        {"_id": goal["_id"]},
                        {"$set": {"status": "completed", "completed_at": datetime.datetime.utcnow()}}
                    )
                    unlock_achievement(username, "goal_master")
                    st.rerun()
            
            st.markdown("---")

# -------------------- 📚 GUIDED EXERCISES --------------------
def guided_exercises_page(username):
    st.title("📚 Guided Wellness Exercises")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌬️ Breathing", "💭 Thought Record", "🙏 Gratitude", "📝 CBT Worksheet"
    ])
    
    with tab1:
        breathing_exercise(username)
    
    with tab2:
        thought_record(username)
    
    with tab3:
        gratitude_journal(username)
    
    with tab4:
        cbt_worksheet(username)

def breathing_exercise(username):
    st.subheader("🌬️ Breathing Exercises")
    
    exercise_type = st.selectbox(
        "Choose an exercise:",
        ["4-7-8 Breathing", "Box Breathing", "Calm Breathing"]
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if exercise_type == "4-7-8 Breathing":
            st.markdown("""
            ### 4-7-8 Breathing Technique
            
            This technique helps reduce anxiety and promote relaxation.
            
            **Steps:**
            1. **Inhale** through your nose for **4 seconds**
            2. **Hold** your breath for **7 seconds**
            3. **Exhale** through your mouth for **8 seconds**
            4. Repeat 4 times
            """)
            
        elif exercise_type == "Box Breathing":
            st.markdown("""
            ### Box Breathing
            
            Used by Navy SEALs to stay calm under pressure.
            
            **Steps:**
            1. **Inhale** for **4 seconds**
            2. **Hold** for **4 seconds**
            3. **Exhale** for **4 seconds**
            4. **Hold** for **4 seconds**
            5. Repeat 4 times
            """)
            
        else:
            st.markdown("""
            ### Calm Breathing
            
            Simple relaxation breathing.
            
            **Steps:**
            1. **Inhale** slowly through nose for **3 seconds**
            2. **Exhale** slowly through mouth for **6 seconds**
            3. Repeat 5 times
            """)
        
        if st.button("▶️ Start Exercise", use_container_width=True):
            # Log exercise completion
            exercises_col.insert_one({
                "username": username,
                "type": "breathing",
                "exercise": exercise_type,
                "timestamp": datetime.datetime.utcnow()
            })
            
            st.success("✅ Exercise completed! Great job taking care of yourself.")
            unlock_achievement(username, "breath_master")
    
    with col2:
        st.markdown("### 💡 Benefits")
        st.info("""
        - Reduces stress
        - Lowers heart rate
        - Improves focus
        - Reduces anxiety
        - Better sleep
        """)

def thought_record(username):
    st.subheader("💭 Thought Record Worksheet")
    st.markdown("Identify and challenge negative thoughts using CBT techniques")
    
    situation = st.text_area(
        "1. What was the situation?",
        placeholder="Describe what happened..."
    )
    
    emotions = st.text_input(
        "2. What emotions did you feel?",
        placeholder="E.g., Anxious, sad, angry..."
    )
    
    automatic_thought = st.text_area(
        "3. What automatic thoughts came up?",
        placeholder="What went through your mind?"
    )
    
    evidence_for = st.text_area(
        "4. Evidence supporting the thought:",
        placeholder="What makes you think this thought is true?"
    )
    
    evidence_against = st.text_area(
        "5. Evidence against the thought:",
        placeholder="What suggests this thought might not be completely true?"
    )
    
    balanced_thought = st.text_area(
        "6. A more balanced thought:",
        placeholder="What's a more realistic way to think about this?"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save Record", use_container_width=True):
            record = {
                "username": username,
                "type": "thought_record",
                "situation": situation,
                "emotions": emotions,
                "automatic_thought": automatic_thought,
                "evidence_for": evidence_for,
                "evidence_against": evidence_against,
                "balanced_thought": balanced_thought,
                "timestamp": datetime.datetime.utcnow()
            }
            
            exercises_col.insert_one(record)
            st.success("✅ Thought record saved!")
            unlock_achievement(username, "thought_challenger")

def gratitude_journal(username):
    st.subheader("🙏 Daily Gratitude Journal")
    st.markdown("Research shows gratitude improves mental well-being")
    
    st.markdown("### What are you grateful for today?")
    
    gratitude1 = st.text_input("1.", placeholder="Something you're thankful for...")
    gratitude2 = st.text_input("2.", placeholder="Another thing you appreciate...")
    gratitude3 = st.text_input("3.", placeholder="One more thing...")
    
    reflection = st.text_area(
        "Optional: Reflect on why these matter to you",
        placeholder="Take a moment to reflect..."
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save Entry", use_container_width=True):
            entry = {
                "username": username,
                "type": "gratitude",
                "items": [gratitude1, gratitude2, gratitude3],
                "reflection": reflection,
                "timestamp": datetime.datetime.utcnow()
            }
            
            exercises_col.insert_one(entry)
            st.success("✅ Gratitude entry saved!")
            unlock_achievement(username, "gratitude_warrior")
    
    # Show recent entries
    st.markdown("---")
    st.markdown("### 📖 Recent Entries")
    
    recent = list(exercises_col.find({
        "username": username,
        "type": "gratitude"
    }).sort("timestamp", -1).limit(5))
    
    for entry in recent:
        with st.expander(entry['timestamp'].strftime('%b %d, %Y')):
            for i, item in enumerate(entry['items'], 1):
                if item:
                    st.markdown(f"{i}. {item}")

def cbt_worksheet(username):
    st.subheader("📝 CBT Worksheet")
    st.markdown("Work through cognitive distortions with this structured approach")
    
    distortion_types = [
        "All-or-Nothing Thinking",
        "Overgeneralization",
        "Mental Filter",
        "Discounting Positives",
        "Jumping to Conclusions",
        "Magnification/Minimization",
        "Emotional Reasoning",
        "Should Statements",
        "Labeling",
        "Personalization"
    ]
    
    distortion = st.selectbox("Type of cognitive distortion:", distortion_types)
    
    trigger = st.text_area("What triggered this thought?")
    thought = st.text_area("The distorted thought:")
    challenge = st.text_area("Challenge: What's the evidence against this?")
    reframe = st.text_area("Reframed thought:")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Save Worksheet", use_container_width=True):
            worksheet = {
                "username": username,
                "type": "cbt_worksheet",
                "distortion": distortion,
                "trigger": trigger,
                "thought": thought,
                "challenge": challenge,
                "reframe": reframe,
                "timestamp": datetime.datetime.utcnow()
            }
            
            exercises_col.insert_one(worksheet)
            st.success("✅ CBT worksheet saved!")

# -------------------- 🏆 GAMIFICATION --------------------
def gamification_page(username):
    st.title("🏆 Achievements & Progress")
    st.markdown("Track your wellness journey milestones")
    
    tab1, tab2 = st.tabs(["🏅 Achievements", "📊 Statistics"])
    
    with tab1:
        display_achievements(username)
    
    with tab2:
        display_statistics(username)

def display_achievements(username):
    # Define all achievements
    all_achievements = {
        "first_chat": {
            "name": "First Steps",
            "description": "Started your first conversation",
            "icon": "👋",
            "points": 10
        },
        "journal_streak_7": {
            "name": "Week Warrior",
            "description": "Journaled for 7 days straight",
            "icon": "🔥",
            "points": 50
        },
        "goal_completed": {
            "name": "Goal Getter",
            "description": "Completed your first goal",
            "icon": "🎯",
            "points": 30
        },
        "breath_master": {
            "name": "Breath Master",
            "description": "Completed 10 breathing exercises",
            "icon": "🌬️",
            "points": 40
        },
        "thought_challenger": {
            "name": "Thought Challenger",
            "description": "Completed 5 thought records",
            "icon": "💭",
            "points": 50
        },
        "gratitude_warrior": {
            "name": "Gratitude Warrior",
            "description": "Logged gratitude 10 times",
            "icon": "🙏",
            "points": 40
        },
        "goal_master": {
            "name": "Goal Master",
            "description": "Completed 5 wellness goals",
            "icon": "🏆",
            "points": 100
        }
    }
    
    # Get user's achievements
    user_achievements = list(achievements_col.find({"username": username}))
    unlocked_ids = [a['achievement_id'] for a in user_achievements]
    
    # Calculate total points
    total_points = sum([all_achievements[a['achievement_id']]['points'] 
                       for a in user_achievements if a['achievement_id'] in all_achievements])
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏅 Achievements", f"{len(user_achievements)}/{len(all_achievements)}")
    
    with col2:
        st.metric("⭐ Total Points", total_points)
    
    with col3:
        level = total_points // 100 + 1
        st.metric("📊 Level", level)
    
    st.markdown("---")
    
    # Display achievements grid
    cols = st.columns(3)
    
    for idx, (achievement_id, achievement) in enumerate(all_achievements.items()):
        with cols[idx % 3]:
            is_unlocked = achievement_id in unlocked_ids
            
            if is_unlocked:
                st.markdown(f"""
                <div style='padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            border-radius: 10px; text-align: center; color: white;'>
                    <div style='font-size: 3rem;'>{achievement['icon']}</div>
                    <div style='font-weight: bold; margin: 10px 0;'>{achievement['name']}</div>
                    <div style='font-size: 0.9rem; opacity: 0.9;'>{achievement['description']}</div>
                    <div style='margin-top: 10px; font-weight: bold;'>+{achievement['points']} pts</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='padding: 20px; background: #f0f0f0; border-radius: 10px; 
                            text-align: center; opacity: 0.5;'>
                    <div style='font-size: 3rem;'>🔒</div>
                    <div style='font-weight: bold; margin: 10px 0;'>{achievement['name']}</div>
                    <div style='font-size: 0.9rem;'>{achievement['description']}</div>
                    <div style='margin-top: 10px;'>+{achievement['points']} pts</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

def display_statistics(username):
    # Gather all user data
    total_chats = db["sessions"].count_documents({"username": username})
    total_journal = mood_journal_col.count_documents({"username": username})
    total_goals = goals_col.count_documents({"username": username})
    completed_goals = goals_col.count_documents({"username": username, "status": "completed"})
    total_exercises = exercises_col.count_documents({"username": username})
    
    # Display comprehensive stats
    st.subheader("📊 Your Wellness Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Total Chats", total_chats)
        st.metric("📝 Journal Entries", total_journal)
    
    with col2:
        st.metric("🎯 Goals Created", total_goals)
        st.metric("✅ Goals Completed", completed_goals)
    
    with col3:
        st.metric("📚 Exercises Done", total_exercises)
    
    with col4:
        # Calculate streak
        streak = calculate_login_streak(username)
        st.metric("🔥 Login Streak", f"{streak} days")
    
    # Activity timeline
    st.markdown("---")
    st.subheader("📈 Activity Timeline")
    
    # Combine all activities
    activities = []
    
    # Chats
    for chat in db["sessions"].find({"username": username}).limit(100):
        activities.append({
            "date": chat["timestamp"],
            "type": "Chat",
            "description": "Had a conversation"
        })
    
    # Journal
    for entry in mood_journal_col.find({"username": username}).limit(100):
        activities.append({
            "date": entry["timestamp"],
            "type": "Journal",
            "description": f"Mood: {entry['mood']}"
        })
    
    # Goals
    for goal in goals_col.find({"username": username}).limit(100):
        activities.append({
            "date": goal["created_at"],
            "type": "Goal",
            "description": f"Created goal: {goal['name']}"
        })
    
    # Exercises
    for exercise in exercises_col.find({"username": username}).limit(100):
        activities.append({
            "date": exercise["timestamp"],
            "type": "Exercise",
            "description": f"Completed {exercise['type']}"
        })
    
    # Sort by date
    activities.sort(key=lambda x: x["date"], reverse=True)
    
    # Display timeline
    for activity in activities[:20]:
        st.markdown(f"**{activity['date'].strftime('%b %d, %I:%M %p')}** - {activity['type']}: {activity['description']}")

def unlock_achievement(username, achievement_id):
    """Unlock an achievement for a user"""
    existing = achievements_col.find_one({
        "username": username,
        "achievement_id": achievement_id
    })
    
    if not existing:
        achievements_col.insert_one({
            "username": username,
            "achievement_id": achievement_id,
            "unlocked_at": datetime.datetime.utcnow()
        })

def check_journal_streak(username):
    """Check and award streak achievements"""
    entries = list(mood_journal_col.find(
        {"username": username}
    ).sort("timestamp", -1).limit(30))
    
    if len(entries) >= 7:
        dates = [e['timestamp'].date() for e in entries]
        dates.sort(reverse=True)
        
        streak = 1
        for i in range(len(dates) - 1):
            if (dates[i] - dates[i + 1]).days == 1:
                streak += 1
            else:
                break
        
        if streak >= 7:
            unlock_achievement(username, "journal_streak_7")

def calculate_login_streak(username):
    """Calculate consecutive login days"""
    sessions = list(db["sessions"].find(
        {"username": username}
    ).sort("timestamp", -1))
    
    if not sessions:
        return 0
    
    dates = sorted(set([s['timestamp'].date() for s in sessions]), reverse=True)
    
    streak = 1
    for i in range(len(dates) - 1):
        if (dates[i] - dates[i + 1]).days == 1:
            streak += 1
        else:
            break
    
    return streak

# -------------------- 🔔 REMINDERS (Browser Notifications) --------------------
# ==================== ENHANCED REMINDERS PAGE ====================
# Replace the reminders_page() function in your phase2_enhancements.py with this

def reminders_page(username):
    st.title("🔔 Smart Reminders")
    st.markdown("Set up gentle reminders for your wellness activities")
    
    # Instructions
    st.info("""
    💡 **How it works:**
    - Reminders appear in the sidebar when you're using the app
    - You can dismiss or snooze each reminder
    - Reminders reset daily for a fresh start
    """)
    
    # ==================== TEST SECTION ====================
    st.markdown("---")
    st.subheader("🧪 Test Your Reminders")
    st.caption("Click to see what a reminder looks like")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔔 Test Check-in", use_container_width=True):
            st.sidebar.warning("**🔔 Mood Check-in Reminder**")
            st.sidebar.caption("Time to log your mood! Head to Mood Journal.")
            st.sidebar.markdown("---")
            st.success("✅ Check the sidebar to see the test reminder!")
    
    with col2:
        if st.button("🌬️ Test Breathing", use_container_width=True):
            st.sidebar.info("**🌬️ Breathing Exercise Reminder**")
            st.sidebar.caption("Take 2 minutes for a breathing break! Visit the Exercises tab.")
            st.sidebar.markdown("---")
            st.success("✅ Check the sidebar to see the test reminder!")
    
    with col3:
        if st.button("🎯 Test Goals", use_container_width=True):
            st.sidebar.success("**🎯 Goal Progress Check**")
            st.sidebar.caption("Review your wellness goals today! Check the Goals tab.")
            st.sidebar.markdown("---")
            st.success("✅ Check the sidebar to see the test reminder!")
    
    # ==================== DAILY CHECK-IN ====================
    st.markdown("---")
    st.subheader("📅 Daily Mood Check-in Reminder")
    st.markdown("Get reminded to log your mood every day")
    
    # Get existing settings
    existing_checkin = reminders_col.find_one({"username": username, "type": "checkin"})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        checkin_enabled = st.checkbox(
            "Enable daily mood check-in reminder", 
            value=existing_checkin.get('enabled', False) if existing_checkin else False,
            key="checkin_reminder"
        )
        
        default_time = datetime.time(20, 0)
        if existing_checkin and 'time' in existing_checkin:
            try:
                h, m = map(int, existing_checkin['time'].split(':'))
                default_time = datetime.time(h, m)
            except:
                pass
        
        checkin_time = st.time_input("Reminder time", default_time)
        st.caption("🕐 Best time: Evening, before bed (e.g., 8:00 PM)")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Check-in Settings", key="save_checkin", use_container_width=True):
            reminders_col.update_one(
                {"username": username, "type": "checkin"},
                {"$set": {
                    "enabled": checkin_enabled,
                    "time": checkin_time.strftime("%H:%M"),
                    "updated_at": datetime.datetime.utcnow()
                }},
                upsert=True
            )
            st.success("✅ Check-in reminder saved!")
            st.balloons()
    
    # Show status
    if checkin_enabled:
        st.success(f"✅ Active: You'll be reminded at {checkin_time.strftime('%I:%M %p')} daily")
    else:
        st.info("ℹ️ Currently disabled")
    
    # ==================== BREATHING EXERCISE ====================
    st.markdown("---")
    st.subheader("🌬️ Breathing Exercise Reminders")
    st.markdown("Regular breathing breaks reduce stress and anxiety")
    
    # Get existing settings
    existing_breathing = reminders_col.find_one({"username": username, "type": "breathing"})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        breathing_enabled = st.checkbox(
            "Enable breathing exercise reminders",
            value=existing_breathing.get('enabled', False) if existing_breathing else False,
            key="breathing_reminder"
        )
        
        default_freq = existing_breathing.get('frequency', 'Every 4 hours') if existing_breathing else 'Every 4 hours'
        breathing_frequency = st.selectbox(
            "How often?",
            ["Every 2 hours", "Every 4 hours", "Twice daily"],
            index=["Every 2 hours", "Every 4 hours", "Twice daily"].index(default_freq)
        )
        
        st.caption("💡 Recommendation: Every 4 hours for balanced practice")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Breathing Settings", key="save_breathing", use_container_width=True):
            reminders_col.update_one(
                {"username": username, "type": "breathing"},
                {"$set": {
                    "enabled": breathing_enabled,
                    "frequency": breathing_frequency,
                    "updated_at": datetime.datetime.utcnow()
                }},
                upsert=True
            )
            st.success("✅ Breathing reminder saved!")
            st.balloons()
    
    # Show status
    if breathing_enabled:
        if breathing_frequency == "Every 2 hours":
            st.success("✅ Active: Reminders every 2 hours (12 PM, 2 PM, 4 PM, 6 PM, 8 PM)")
        elif breathing_frequency == "Every 4 hours":
            st.success("✅ Active: Reminders every 4 hours (12 PM, 4 PM, 8 PM)")
        else:
            st.success("✅ Active: Reminders twice daily (9 AM, 6 PM)")
    else:
        st.info("ℹ️ Currently disabled")
    
    # ==================== GOAL PROGRESS ====================
    st.markdown("---")
    st.subheader("🎯 Goal Progress Check-ins")
    st.markdown("Stay on track with regular goal reviews")
    
    # Get existing settings
    existing_goal = reminders_col.find_one({"username": username, "type": "goal"})
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        goal_enabled = st.checkbox(
            "Enable goal progress reminders",
            value=existing_goal.get('enabled', False) if existing_goal else False,
            key="goal_reminder"
        )
        
        default_goal_freq = existing_goal.get('frequency', 'Daily') if existing_goal else 'Daily'
        goal_frequency = st.selectbox(
            "Check-in frequency",
            ["Daily", "Every 3 days", "Weekly"],
            index=["Daily", "Every 3 days", "Weekly"].index(default_goal_freq)
        )
        
        st.caption("📊 Recommendation: Daily for best results")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 Save Goal Settings", key="save_goal", use_container_width=True):
            reminders_col.update_one(
                {"username": username, "type": "goal"},
                {"$set": {
                    "enabled": goal_enabled,
                    "frequency": goal_frequency,
                    "updated_at": datetime.datetime.utcnow()
                }},
                upsert=True
            )
            st.success("✅ Goal reminder saved!")
            st.balloons()
    
    # Show status
    if goal_enabled:
        if goal_frequency == "Daily":
            st.success("✅ Active: Reminder every morning at 9 AM")
        elif goal_frequency == "Every 3 days":
            st.success("✅ Active: Reminder every 3 days at 9 AM")
        else:
            st.success("✅ Active: Reminder every Monday at 9 AM")
    else:
        st.info("ℹ️ Currently disabled")
    
    # ==================== SUMMARY ====================
    st.markdown("---")
    st.subheader("📊 Your Reminder Summary")
    
    all_reminders = list(reminders_col.find({"username": username}))
    
    if not all_reminders:
        st.info("🔕 No reminders set yet. Configure them above!")
    else:
        active_count = sum(1 for r in all_reminders if r.get('enabled', False))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Reminders", len(all_reminders))
        with col2:
            st.metric("Active", active_count)
        with col3:
            st.metric("Inactive", len(all_reminders) - active_count)
        
        # List all reminders
        st.markdown("### 📋 All Reminders")
        
        for reminder in all_reminders:
            reminder_type = reminder.get('type', 'unknown')
            is_enabled = reminder.get('enabled', False)
            
            icon_map = {
                'checkin': '📅',
                'breathing': '🌬️',
                'goal': '🎯'
            }
            
            name_map = {
                'checkin': 'Daily Mood Check-in',
                'breathing': 'Breathing Exercise',
                'goal': 'Goal Progress'
            }
            
            icon = icon_map.get(reminder_type, '🔔')
            name = name_map.get(reminder_type, 'Reminder')
            status = "✅ Active" if is_enabled else "🔕 Inactive"
            
            with st.expander(f"{icon} {name} - {status}"):
                if reminder_type == 'checkin':
                    st.write(f"**Time:** {reminder.get('time', 'Not set')}")
                elif reminder_type == 'breathing':
                    st.write(f"**Frequency:** {reminder.get('frequency', 'Not set')}")
                elif reminder_type == 'goal':
                    st.write(f"**Frequency:** {reminder.get('frequency', 'Not set')}")
                
                if 'updated_at' in reminder:
                    st.caption(f"Last updated: {reminder['updated_at'].strftime('%b %d, %Y %I:%M %p')}")
    
    # ==================== TIPS ====================
    st.markdown("---")
    st.subheader("💡 Reminder Tips")
    
    st.markdown("""
    **Getting the most from reminders:**
    
    1. 🕐 **Set realistic times** - Choose times when you're usually free
    2. 📱 **Keep the app open** - Reminders show when you're using the app
    3. ✅ **Act on reminders** - Take action when you see them
    4. 🔄 **Adjust as needed** - Change frequencies if they're too much/little
    5. 🎯 **Start small** - Begin with 1-2 reminders, add more later
    
    **Best practices:**
    - Morning reminders work best for goal reviews
    - Evening reminders are ideal for mood journaling
    - Breathing reminders help during work hours
    """)
    
    # ==================== QUICK ACTIONS ====================
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔕 Disable All", use_container_width=True):
            reminders_col.update_many(
                {"username": username},
                {"$set": {"enabled": False}}
            )
            st.success("All reminders disabled")
            st.rerun()
    
    with col2:
        if st.button("✅ Enable All", use_container_width=True):
            reminders_col.update_many(
                {"username": username},
                {"$set": {"enabled": True}}
            )
            st.success("All reminders enabled")
            st.rerun()
    
    with col3:
        if st.button("🗑️ Delete All", use_container_width=True):
            count = reminders_col.delete_many({"username": username}).deleted_count
            st.success(f"Deleted {count} reminders")
            st.rerun()

# -------------------- MAIN PHASE 2 ROUTER --------------------
def phase2_main(username, page):
    """
    Main router for Phase 2 features
    
    Args:
        username: Current logged-in user
        page: Which page to display
    """
    
    if page == "🗓️ Mood Journal":
        mood_journal_page(username)
    
    elif page == "🎯 Goals":
        goal_tracking_page(username)
    
    elif page == "📚 Exercises":
        guided_exercises_page(username)
    
    elif page == "🏆 Achievements":
        gamification_page(username)
    
    elif page == "🔔 Reminders":
        reminders_page(username)

# -------------------- INTEGRATION EXAMPLE --------------------
"""
HOW TO INTEGRATE WITH YOUR MAIN APP:

1. Import this module in your main app:
   
   import phase2_enhancements as phase2

2. Add Phase 2 options to your sidebar navigation:
   
   page = st.radio("📍 Navigate", [
       "💬 Chat", 
       "virtual_chat",
       "📊 Analytics", 
       "ℹ️ Resources",
       "🗓️ Mood Journal",    # NEW
       "🎯 Goals",           # NEW
       "📚 Exercises",       # NEW
       "🏆 Achievements",    # NEW
       "🔔 Reminders"        # NEW
   ])

3. Route to Phase 2 features:
   
   if page in ["🗓️ Mood Journal", "🎯 Goals", "📚 Exercises", 
               "🏆 Achievements", "🔔 Reminders"]:
       phase2.phase2_main(st.session_state.username, page)
   elif page == "💬 Chat":
       chat_interface()
   # ... rest of your pages

4. That's it! All Phase 2 features are now integrated.

FEATURES INCLUDED:
✅ Mood Journal with calendar heatmap
✅ Goal tracking with progress bars
✅ Guided breathing exercises
✅ CBT thought records
✅ Gratitude journaling
✅ Gamification with achievements
✅ Smart reminders
✅ Comprehensive analytics

All data is stored in your existing MongoDB database!
"""
