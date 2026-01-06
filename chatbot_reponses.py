"""
chatbot_responses.py
Complete conversational response library for MindSync AI chatbot
"""

# ========== RESPONSE LIBRARY ==========

RESPONSES = {
    # ========== CRISIS & SAFETY ==========
    "injury": """🩹 Oh no! I'm sorry to hear you got hurt! Are you okay?

🚨 **First things first**:
- If it's serious, please get medical help right away
- For minor injuries, apply first aid
- Tell your parents/family what happened
- Rest and take care of yourself

💙 **I'm here if you need to talk about it**. Accidents can be scary. Take your time to recover, both physically and emotionally.

Stay safe! 💚""",

    "crisis": """⚠️ I'm deeply concerned about what you're sharing. Your life matters.

🆘 **Please reach out immediately**:
- AASRA: 91-22-27546669 (24/7)
- Vandrevala Foundation: 1860-2662-345 (24/7)
- iCall: 022-25521111

You don't have to face this alone. Please talk to someone you trust right now. 💙""",

    # ========== GREETINGS & BASICS ==========
    "greeting": """Hey there! 😊 How are you doing today? 

I'm here to listen to whatever's on your mind - whether it's something exciting, challenging, or you just want to chat. What's going on with you?""",

    "how_are_you": """I'm doing well, thank you for asking! 😊 

More importantly though - how are *you* doing? I'm here to listen to whatever you'd like to share. What's been happening in your day?""",

    "thank_you": """You're very welcome! 😊 I'm really glad I could help!

Feel free to come back anytime you want to chat or share anything. I'm always here for you! 💙""",

    "goodbye": """Take care! 😊 It was nice talking with you.

Remember, I'm here whenever you need someone to talk to. Have a great day ahead! 🌟""",

    # ========== DAILY LIFE ==========
    "school_day": """How was your day at school/college? 📚

Tell me more! Did anything interesting happen? How are your classes going? Sometimes even ordinary days have little moments worth sharing. I'm all ears! 😊""",

    "weekend_plans": """Ooh, weekend/holiday time! 🎉

Do you have any fun plans? Whether it's chilling at home, hanging with friends, or finally catching up on sleep - it all sounds good! What are you thinking of doing?""",

    "food_talk": """Mmm, food talk! 🍕

What are you in the mood for? Or did you try something new? Food is one of life's simple pleasures. Share more - I'd love to hear about it!""",

    "friends_hangout": """Friends make everything better! 👥

Tell me more! What did you guys do? Or are you planning something fun? It's great that you have people to share moments with. 😊

By the way, good friends are precious - make sure to cherish them and let them know you appreciate them!""",

    "hobbies": """Nice! Doing things you enjoy is so important! 🎮🎬🎵

What are you into? I'd love to hear more about it! Whether it's a new game, show, song, or hobby - share away! What do you like about it?

Sometimes our hobbies can actually help us relax and recharge. Keep making time for what you love!""",

    "weather": """Weather can really affect the day, right? 🌤️

How's the weather where you are? Perfect day to go out or more of a cozy-indoors kind of day? What do you feel like doing?""",

    "tired": """Sounds like you need some rest! 😴

Have you been having a busy time? Make sure to take care of yourself and get some good sleep when you can. Your body and mind will thank you! 💙

Is something keeping you up, or just a long day? Want to talk about it?""",

    "bored": """Boredom, huh? 😅

Sometimes those "nothing to do" moments are actually good for resetting! But if you want ideas:
- Try something creative (draw, write, music)
- Learn something new (YouTube tutorials!)
- Message a friend you haven't talked to in a while
- Go for a walk
- Start that show/game you've been meaning to try

What sounds interesting to you?""",

    # ========== ACHIEVEMENTS & CELEBRATIONS ==========
    "success": """🎉 CONGRATULATIONS! That's amazing news!

You must have worked really hard for this! How are you feeling? This is definitely worth celebrating! 

Make sure to share this with your loved ones and do something special for yourself. You deserve it! 🌟✨

What's next for you? Enjoy this moment!""",

    "birthday": """🎂🎉 HAPPY BIRTHDAY! 🎉🎂

I hope you have an absolutely wonderful day filled with joy, laughter, and all your favorite things! 

Did you do anything special? Any birthday wishes you're hoping come true? Enjoy your day to the fullest! 🎈✨

May this year bring you happiness, success, and all the good things you deserve!""",

    # ========== CHALLENGES ==========
    "exam_stress": """📚 Exams can definitely be stressful! I get it.

**Quick tips that help**:
- Study in short bursts (25 min sessions with breaks)
- Don't pull all-nighters - sleep helps memory!
- Take deep breaths when anxious
- Believe in yourself - you've prepared!

How's your preparation going? Want to talk about what's worrying you?

Remember: One exam doesn't define you. You're capable and you've got this! 💪""",

    "job_success": """🎊 That's fantastic news about the job! Congratulations!

This is a huge milestone! How are you feeling about it? New beginnings are exciting! 

**Some tips for your new role**:
- Be yourself and stay confident
- Ask questions - it shows you're engaged
- Build good relationships with colleagues
- Give yourself time to adjust

Make sure to celebrate properly - you earned this! 🚀✨""",

    "job_search": """💼 Job hunting can be really tough and exhausting, I understand.

The right opportunity will come along - these things take time. Keep your head up!

**Meanwhile**:
- Keep networking and applying
- Take care of your mental health
- Talk to friends/family for support
- Update your skills if possible
- Don't take rejections personally - it's part of the process

You've got this! Want to talk more about it? Sometimes venting helps! 💪""",

    "relationship_conflict": """💙 Relationship challenges are hard. I'm sorry you're going through this.

Want to talk about what happened? Sometimes just sharing helps. Remember:
- It's okay to feel upset
- Give yourself and others time to cool down
- Communication helps when both sides are ready
- Not all conflicts are permanent
- Sometimes disagreements actually strengthen relationships

I'm here to listen if you want to share more. What's on your mind?""",

    # ========== EMOTIONS ==========
    "severe_depression": """💙 I'm really glad you're talking to me about this. What you're feeling matters, and I'm concerned about you.

These heavy feelings don't have to be permanent. Please consider:
- Talking to someone you trust
- Reaching out to a counselor or therapist
- Calling a helpline: AASRA (91-22-27546669)

**Small steps that might help**:
- Get some sunlight today (even 10 minutes)
- Talk to one person you care about
- Do one tiny thing you used to enjoy
- Write down your feelings

You matter. Your life has value. Please don't give up. I'm here for you. 💚

Would you like to talk more about what you're feeling?""",

    "sadness": """💙 I'm sorry you're feeling this way. It's completely okay to have down days - we all do.

Want to talk about what's bothering you? Sometimes sharing helps lighten the load.

**Small things that might help**:
- Talk to a friend or family member
- Go outside for a bit (fresh air works wonders)
- Watch/do something you enjoy
- Remember: feelings are temporary, this will pass

I'm here to listen without judgment. What's going on? 🤗""",

    "anxiety": """😰 Anxiety is really uncomfortable. I hear you and I'm here for you.

**Try this right now**:
- Take 5 deep breaths (4 seconds in, 7 hold, 8 out)
- Ground yourself: Name 5 things you can see right now

**What helps longer term**:
- Exercise (even a short walk)
- Talk to someone about what's worrying you
- Write down your thoughts
- Limit caffeine
- Practice mindfulness

Want to tell me more about what's making you anxious? Sometimes saying it out loud helps.""",

    "anger": """😤 It sounds like something really got to you! That's frustrating.

Anger is valid - it's what we do with it that matters. It's actually healthy to acknowledge when you're angry.

**To cool down**:
- Take a break from the situation
- Physical activity (run, workout, walk)
- Deep breaths - count to 10
- Talk it out with someone

Want to tell me what happened? Sometimes venting helps! I won't judge - just here to listen. 💙""",

    "happiness": """😊 I love your positive energy! That's wonderful!

What's making you happy? I'd love to hear about it! Good moments deserve to be celebrated and shared! 

**Ways to amplify your joy**:
- Share it with loved ones
- Take a mental snapshot of this feeling
- Do something fun to celebrate
- Spread the positivity to others

Keep spreading that joy! You deserve all the happiness! 🌟✨""",

    # ========== RELATIONSHIPS & LOVE ==========
    "family_talk": """👨‍👩‍👧 Family is so important!

Want to share what's on your mind about your family? Whether it's good news, a challenge, or just everyday stuff - I'm here to listen! 💙

Family relationships can be complex, but they're also some of the most meaningful connections we have. What's going on?""",

    "crush_love": """💕 Ooh, matters of the heart! These feelings can be both exciting and confusing!

Want to talk about it? Whether it's:
- Exciting butterflies and new feelings
- Confusion about what to do
- Nervousness about expressing feelings
- Wondering if they like you back

I'm here to listen! Love and attraction are beautiful parts of life. What's on your mind? 😊

Remember: Be yourself - that's who they should fall for!""",

    "relationship_advice": """💑 Relationships are a beautiful journey!

Whether you're:
- Just starting to date someone
- In a relationship and facing challenges
- Wondering how to make it work
- Dealing with ups and downs

I'm here to listen and support! Want to share what's on your mind?

**Quick relationship tips**:
- Communication is key - talk openly
- Respect each other's boundaries
- Keep your individuality
- Trust and honesty are foundations
- Don't lose yourself in the relationship""",

    "breakup_heartbreak": """💔 Breakups are really painful. I'm so sorry you're going through this.

It's okay to feel hurt, sad, angry, or confused. All these feelings are valid. Heartbreak is a real form of grief.

**Healing takes time, but here's what helps**:
- Allow yourself to feel the emotions
- Talk to friends/family who care about you
- Stay busy with things you enjoy
- Take care of yourself - eat, sleep, exercise
- Don't rush into another relationship
- Block/unfollow if seeing their posts hurts
- Write down your feelings

Want to talk about it? I'm here to listen. You will get through this, I promise. 💙

Remember: This ending makes space for something better.""",

    "friendship_issues": """👥 Friend troubles can be really difficult!

Whether it's:
- A fight or misunderstanding
- Feeling left out
- Changing friendships
- Betrayal or hurt
- Growing apart

These situations hurt because friends matter. Want to share what happened?

**Remember**:
- True friends work through conflicts
- It's okay to outgrow some friendships
- Communication can resolve many issues
- Your feelings are valid
- Some friendships are seasonal, some are lifelong

I'm here to listen! 💙""",

    "loneliness": """💙 Feeling lonely is tough, and I want you to know you're not alone in feeling this way.

Loneliness is actually really common, even when we're surrounded by people sometimes.

**Things that might help**:
- Reach out to someone - even a simple "hi, how are you?"
- Join a club/group/class for something you like
- Volunteer - helping others connects us
- Online communities for your interests
- Talk to family members
- Don't compare your social life to others' social media

Would you like to talk about what's making you feel lonely? Sometimes just connecting with someone (even here) helps. 

You matter, and you deserve meaningful connections. 🤗""",

    # ========== SPECIFIC SITUATIONS ==========
    "parent_problems": """👨‍👩‍👧 Parent issues can be really stressful, especially when you're living with them.

Whether it's:
- Not understanding you
- Too strict rules
- Expectations and pressure
- Arguments and fights
- Feeling controlled

These are common struggles. Want to talk about what's happening?

**Remember**:
- Parents usually come from a place of care (even if it doesn't feel like it)
- Try calm communication when emotions are low
- They're human too and make mistakes
- It's okay to disagree respectfully
- Some things get better with time and age

I'm here to listen without judgment! 💙""",

    "peer_pressure": """😕 Peer pressure is real and can be really stressful!

Feeling pressure to:
- Fit in with a group
- Do things you're uncomfortable with
- Change who you are
- Make choices you don't agree with

This is tough! Want to talk about what's going on?

**Remember**:
- Real friends respect your choices
- It's okay to say no
- Being yourself is cooler than fitting in
- Your comfort and values matter
- You don't owe anyone an explanation

Stay true to yourself! The right people will appreciate the real you. 💪""",

    "self_esteem": """💙 Self-esteem struggles are so common, and I'm glad you're opening up about it.

Feeling:
- Not good enough
- Comparing yourself to others
- Focusing on flaws
- Doubting your worth

These feelings are tough but NOT the truth about you!

**Building self-esteem**:
- List 3 things you like about yourself (start small!)
- Celebrate small wins
- Stop comparing - everyone's on different paths
- Surround yourself with positive people
- Challenge negative self-talk
- Focus on what you CAN control

You are valuable just as you are. Want to talk more about what's affecting your confidence? 💚""",

    "bullying": """🛑 Bullying is NEVER okay, and I'm really sorry you're experiencing this.

Whether it's:
- Physical bullying
- Verbal insults
- Cyberbullying
- Exclusion and isolation
- Spreading rumors

**This is NOT your fault. You don't deserve this.**

**What you can do**:
- Tell a trusted adult (parent, teacher, counselor)
- Document everything (screenshots, dates, what happened)
- Don't respond to bullies - they want a reaction
- Block them online
- Stay with friends/groups for safety
- Report to authorities if serious

Please don't face this alone. Talk to someone who can help. You deserve to feel safe. 💙

Want to talk more about what's happening?""",

    # ========== DEFAULT RESPONSES ==========
    "default": """I'm here to listen! 😊

Tell me more about what's on your mind. Whether it's something big or small, exciting or challenging, or you just want to chat - I'm all ears! 

What would you like to talk about? 💙""",

    "casual_chat": """That's interesting! Tell me more! 😊

I'm here to chat about whatever's on your mind. Life is made up of these everyday moments and conversations. 

What else is going on with you today?""",
}


# ========== KEYWORD MAPPINGS ==========

KEYWORD_MAPPINGS = {
    # Crisis & Safety
    "injury": ['hurt', 'injured', 'accident', 'pain', 'bleeding', 'wound', 'broken', 
               'fell', 'crash', 'hit', 'bruise', 'cut', 'sprain', 'twisted', 'fracture'],
    
    "crisis": ['suicide', 'kill myself', 'end my life', 'i want to die', 'self harm',
               "i don't want to live", "i can't go on", 'better off dead'],
    
    # Greetings
    "greeting": ['hi', 'hello', 'hey', 'hii', 'hiii', 'sup', "what's up", 'wassup', 
                 'good morning', 'good afternoon', 'good evening', 'yo', 'hola'],
    
    "how_are_you": ['how are you', 'how r u', 'whats up with you', 'how have you been',
                    'hows it going', 'how you doing'],
    
    "thank_you": ['thank', 'thanks', 'appreciate', 'grateful', 'thx', 'tysm', 'thank u'],
    
    "goodbye": ['bye', 'goodbye', 'see you', 'gotta go', 'talk later', 'gtg', 'catch you later'],
    
    # Daily Life
    "school_day": ['came from school', 'school was', 'college was', 'had classes today', 
                   'school day', 'college day', 'at school', 'at college'],
    
    "weekend_plans": ['weekend', 'saturday', 'sunday', 'holiday', 'vacation', 'break coming',
                      'holidays', 'days off'],
    
    "food_talk": ['hungry', 'food', 'eating', 'lunch', 'dinner', 'breakfast', 'snack', 
                  'pizza', 'burger', 'cooking', 'recipe', 'meal', 'hungry'],
    
    "friends_hangout": ['my friend', 'friends', 'hanging out', 'met someone', 'party', 
                        'gathering', 'fun with', 'chillin with', 'squad'],
    
    "hobbies": ['watching', 'playing', 'game', 'gaming', 'movie', 'series', 'anime', 
                'music', 'song', 'reading', 'book', 'sport', 'exercise', 'hobby'],
    
    "weather": ['weather', 'raining', 'sunny', 'hot', 'cold', 'rain', 'storm'],
    
    "tired": ['tired', 'sleepy', 'exhausted', 'need sleep', 'cant sleep', 'insomnia'],
    
    "bored": ['bored', 'boring', 'nothing to do', 'so bored'],
    
    # Achievements
    "success": ['got promoted', 'got job', 'won', 'achieved', 'accomplished', 
                'passed exam', 'cleared exam', 'got selected', 'offer letter', 'good news',
                'got in', 'accepted', 'made it'],
    
    "birthday": ['birthday', 'bday', 'born day', "it's my birthday"],
    
    # Challenges
    "exam_stress": ['exam tomorrow', 'exam stress', 'failed exam', 'exam preparation', 
                    'studying for', 'exam results', 'board exam', 'test tomorrow'],
    
    "job_success": ['got the job', 'hired', 'job offer accepted', 'starting new job'],
    
    "job_search": ['looking for job', 'job search', 'got fired', 'lost job', 'interview tomorrow',
                   'unemployed', 'need a job'],
    
    "relationship_conflict": ['fight with', 'argument', 'relationship problem', 
                              'not talking', 'mad at each other'],
    
    # Emotions
    "severe_depression": ['hopeless', 'worthless', 'no reason to live', 'hate myself', 
                          'life is meaningless', 'severely depressed', 'no point'],
    
    "sadness": ['sad', 'feeling low', 'down', 'upset', 'crying', 'bad day', 'not good',
                'unhappy', 'miserable'],
    
    "anxiety": ['anxious', 'anxiety', 'panic', 'worried', 'overwhelmed', 
                'stressed', 'nervous', 'cant relax', 'overthinking', 'stress'],
    
    "anger": ['angry', 'furious', 'frustrated', 'pissed', 'mad', 'annoyed', 'irritated'],
    
    "happiness": ['happy', 'excited', 'wonderful', 'amazing', 'great day', 'awesome',
                  'fantastic', 'thrilled', 'ecstatic'],
    
    # Relationships & Love
    "family_talk": ['mom', 'dad', 'mother', 'father', 'parents', 'family', 'sibling', 
                    'brother', 'sister', 'grandma', 'grandpa'],
    
    "crush_love": ['crush', 'like someone', 'have feelings', 'falling for'],
    
    "relationship_advice": ['dating', 'girlfriend', 'boyfriend', 'relationship', 
                            'in a relationship', 'my partner'],
    
    "breakup_heartbreak": ['broke up', 'breakup', 'ex girlfriend', 'ex boyfriend', 
                           'heartbroken', 'dumped', 'split up'],
    
    "friendship_issues": ['friend fight', 'friend problem', 'lost a friend', 
                          'fake friends', 'friend betrayed'],
    
    "loneliness": ['lonely', 'alone', 'no friends', 'isolated', 'feel alone'],
    
    # Specific Situations
    "parent_problems": ['parents fight', 'parents angry', 'parents strict', 
                        'parents dont understand', 'fight with parents'],
    
    "peer_pressure": ['peer pressure', 'forced to', 'everyone is doing', 'feel pressured'],
    
    "self_esteem": ['low self esteem', 'hate myself', 'not confident', 'insecure',
                    'feel ugly', 'not good enough'],
    
    "bullying": ['bullied', 'bully', 'bullying', 'picked on', 'made fun of', 'teased'],
}


# ========== MAIN FUNCTION ==========

def get_response(query, emotion=None):
    """
    Main function to get appropriate response based on user query
    """
    query_lower = query.lower()
    
    # Check each category in priority order
    for response_key, keywords in KEYWORD_MAPPINGS.items():
        # Check for pattern match
        if any(keyword in query_lower for keyword in keywords):
            return RESPONSES.get(response_key, RESPONSES["default"])
    
    # If no specific match, return default
    return RESPONSES["default"]


# ========== EMOTION DETECTION ==========

def detect_emotion_from_text(text):
    """Enhanced emotion detection"""
    text_lower = text.lower()
    
    # Crisis (highest priority)
    if any(word in text_lower for word in KEYWORD_MAPPINGS["crisis"]):
        return "fear", 0.95
    
    # Severe depression
    if any(word in text_lower for word in KEYWORD_MAPPINGS["severe_depression"]):
        return "sadness", 0.95
    
    # Strong negative emotions
    if any(word in text_lower for word in KEYWORD_MAPPINGS["anger"]):
        return "anger", 0.9
    
    # Fear/Anxiety
    if any(word in text_lower for word in KEYWORD_MAPPINGS["anxiety"]):
        return "fear", 0.85
    
    # Sadness
    if any(word in text_lower for word in KEYWORD_MAPPINGS["sadness"]):
        return "sadness", 0.85
    
    # Joy/Happiness
    if any(word in text_lower for word in KEYWORD_MAPPINGS["happiness"]):
        return "joy", 0.9
    
    # Success
    if any(word in text_lower for word in KEYWORD_MAPPINGS["success"]):
        return "joy", 0.85
    
    # Default neutral
    return "neutral", 0.5
