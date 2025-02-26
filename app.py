import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langchain_community.llms import Ollama
from datetime import datetime
from models import Conversation, Message, initialize_db, db
import speech_recognition as sr

# Simplified emotions mapping with highly contrasting colors
EMOTIONS = {
    'Joy': {'color': '#00FF00', 'icon': '😊'},
    'Sadness': {'color': '#0000FF', 'icon': '😢'},
    'Anger': {'color': '#FF0000', 'icon': '😠'},
    'Fear': {'color': '#800080', 'icon': '😨'},
    'Anxiety': {'color': '#FFA500', 'icon': '😰'},
    'Neutral': {'color': '#808080', 'icon': '😐'},
    'Hope': {'color': '#00FFFF', 'icon': '🤗'},
    'Surprise': {'color': '#FFFF00', 'icon': '😮'}
}

TRUSTED_RESOURCES = {
    'Joy': [
        {'title': 'Positive Psychology Exercises - Berkeley', 'url': 'https://ggia.berkeley.edu/'},
        {'title': 'The Science of Happiness | Harvard Health', 'url': 'https://www.health.harvard.edu/mind-and-mood/the-science-of-happiness'},
        {'title': 'Mindfulness Meditation Guide - Mindful.org', 'url': 'https://www.mindful.org/meditation/mindfulness-getting-started/'}
    ],
    'Sadness': [
        {'title': 'Coping with Depression - HelpGuide.org', 'url': 'https://www.helpguide.org/articles/depression/coping-with-depression.htm'},
        {'title': 'Depression Support & Resources - NIMH', 'url': 'https://www.nimh.nih.gov/health/topics/depression'},
        {'title': 'Self-Care Strategies - Mind.org', 'url': 'https://www.mind.org.uk/information-support/tips-for-everyday-living/self-care/'}
    ],
    'Anxiety': [
        {'title': 'Anxiety Management Techniques - HelpGuide', 'url': 'https://www.helpguide.org/articles/anxiety/anxiety-disorders-and-anxiety-attacks.htm'},
        {'title': 'Anxiety & Panic - Mayo Clinic', 'url': 'https://www.mayoclinic.org/diseases-conditions/anxiety/symptoms-causes/syc-20350961'},
        {'title': 'Relaxation Techniques - NHS', 'url': 'https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/relaxation/'}
    ],
    'Fear': [
        {'title': 'Overcoming Fears - Psychology Today', 'url': 'https://www.psychologytoday.com/intl/basics/fear'},
        {'title': 'Managing Fear & Anxiety - CDC', 'url': 'https://www.cdc.gov/mentalhealth/managing-fear-anxiety/index.html'},
        {'title': 'Coping with Fear - Mind.org', 'url': 'https://www.mind.org.uk/information-support/types-of-mental-health-problems/anxiety-and-panic-attacks/'}
    ],
    'Anger': [
        {'title': 'Anger Management - Mayo Clinic', 'url': 'https://www.mayoclinic.org/healthy-lifestyle/adult-health/in-depth/anger-management/art-20045434'},
        {'title': 'Controlling Anger - NHS', 'url': 'https://www.nhs.uk/mental-health/feelings-symptoms-behaviours/feelings-and-symptoms/anger/'},
        {'title': 'Anger Management Strategies - APA', 'url': 'https://www.apa.org/topics/anger/control'}
    ],
    'Hope': [
        {'title': 'Building Hope - Psychology Today', 'url': 'https://www.psychologytoday.com/intl/basics/hope'},
        {'title': 'Cultivating Hope - VeryWellMind', 'url': 'https://www.verywellmind.com/cultivating-hope-when-life-seems-hopeless-4157602'},
        {'title': 'Hope & Optimism - Berkeley', 'url': 'https://ggia.berkeley.edu/practice/finding_hope'}
    ],
    'Neutral': [
        {'title': 'Mental Health Self-Help - NHS', 'url': 'https://www.nhs.uk/mental-health/self-help/'},
        {'title': 'Wellness Resources - HelpGuide', 'url': 'https://www.helpguide.org/articles/mental-health/building-better-mental-health.htm'},
        {'title': 'Self-Care Guide - Mind.org', 'url': 'https://www.mind.org.uk/information-support/tips-for-everyday-living/wellbeing/'}
    ],
    'Surprise': [
        {'title': 'Managing Unexpected Changes - HelpGuide', 'url': 'https://www.helpguide.org/articles/stress/dealing-with-uncertainty.htm'},
        {'title': 'Adapting to Change - Mind.org', 'url': 'https://www.mind.org.uk/information-support/tips-for-everyday-living/managing-change/'},
        {'title': 'Coping with Change - VeryWellMind', 'url': 'https://www.verywellmind.com/coping-with-change-2795735'}
    ]
}

# Initialize database
initialize_db()

# Initialize Streamlit page
st.set_page_config(page_title='AI Mental Health Assistant', page_icon='🧠', layout='wide')

# Initialize session state
if 'current_conversation' not in st.session_state:
    latest_conv = Conversation.select().order_by(Conversation.created_at.desc()).first()
    if latest_conv:
        st.session_state.current_conversation = latest_conv.id

if 'first_message' not in st.session_state:
    st.session_state.first_message = True

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None

def safe_db_operation(operation, max_retries=5):
    for attempt in range(max_retries):
        with db.atomic():
            return operation()

def save_message(conversation, role, content, sentiment=None, sentiment_score=None):
    return Message.create(
        conversation=conversation,
        role=role,
        content=content,
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        created_at=datetime.now()
    )

def delete_conversation_messages(conv):
    return Message.delete().where(Message.conversation == conv).execute()

def delete_conversation(conv):
    delete_conversation_messages(conv)
    return conv.delete_instance()

# Sidebar for conversations
with st.sidebar:
    st.title("💭 Conversations")
    
    if st.button("➕ New Chat"):
        new_conv = safe_db_operation(
            lambda: Conversation.create(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
        )
        st.session_state.current_conversation = new_conv.id
        st.session_state.first_message = True
    
    conversations = safe_db_operation(
        lambda: list(Conversation.select().order_by(Conversation.created_at.desc()))
    )
    for conv in conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(f"   {conv.title}", key=f"conv_{conv.id}"):
                st.session_state.current_conversation = conv.id
                st.session_state.first_message = True
        with col2:
            if st.button("🗑️", key=f"del_{conv.id}"):
                delete_conversation(conv)
                if 'current_conversation' in st.session_state and st.session_state.current_conversation == conv.id:
                    del st.session_state.current_conversation
                st.session_state.first_message = True

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    
    compound = scores['compound']
    pos = scores['pos']
    neg = scores['neg']
    neu = scores['neu']
    
    # تحديد المشاعر والشدة مع تحسين التمييز بين Sadness و Fear
    if compound >= 0.5:
        emotion = 'Joy'
        intensity = pos
    elif compound >= 0.2:
        emotion = 'Hope'
        intensity = pos
    elif compound > -0.2 and compound < 0.2:
        emotion = 'Neutral'
        intensity = neu
    elif compound <= -0.5:
        if 'angry' in text.lower() or neg > 0.6:
            emotion = 'Anger'
            intensity = neg
        else:
            emotion = 'Sadness'
            intensity = neg
    elif compound < -0.2:
        if 'cry' in text.lower() or 'sad' in text.lower():  # إضافة كلمات مفتاحية للحزن
            emotion = 'Sadness'
            intensity = neg
        elif neu > 0.6:
            emotion = 'Anxiety'
            intensity = neg
        else:
            emotion = 'Fear'
            intensity = neg
    else:
        emotion = 'Neutral'
        intensity = neu
    
    return emotion, intensity

def get_ai_response(emotion, intensity, message, conversation_history=""):
    llm = Ollama(model="llama3.2:1b")
    
    prompt = f"""You are an empathetic mental health assistant. A person is feeling {emotion} with {int(intensity * 100)}% intensity.
    They said: "{message}"
    
    Previous conversation context:
    {conversation_history}

    Provide a response in the following format:

    RESPONSE
    [Write a warm, empathetic 2-3 sentence response acknowledging their feelings and showing support]

    RECOMMENDATIONS
    [Provide 5 detailed, creative recommendations. Each should be 2-3 sentences long and include:
    - Specific steps or instructions
    - Expected benefits
    - How it relates to their current emotional state
    - Any scientific backing if relevant]

    Make recommendations unique and creative, avoiding generic advice. Consider both immediate relief and long-term growth.
    Focus on holistic well-being: emotional, physical, social, and mental aspects.
    """
    
    response = llm.invoke(prompt)
    
    sections = {'response': '', 'recommendations': [], 'resources': TRUSTED_RESOURCES.get(emotion, TRUSTED_RESOURCES['Neutral'])}
    current_section = None
    
    for line in response.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line == 'RESPONSE':
            current_section = 'response'
            continue
        elif line == 'RECOMMENDATIONS':
            current_section = 'recommendations'
            continue
            
        if current_section == 'response':
            sections['response'] += line + ' '
        elif current_section == 'recommendations' and line[0].isdigit():
            sections['recommendations'].append(line[2:].strip())
    
    if not sections['response']:
        sections['response'] = f"I understand you're feeling {emotion}. I'm here to listen and support you. Would you like to tell me more about what's troubling you?"
        
    if not sections['recommendations']:
        sections['recommendations'] = [
            f"Practice mindful breathing: Take 5 deep breaths, focusing on the sensation of air moving through your body. This activates your parasympathetic nervous system, helping to reduce {emotion}.",
            "Engage in expressive writing: Spend 10-15 minutes writing freely about your feelings and experiences. Research shows this can help process emotions and reduce stress.",
            "Try progressive muscle relaxation: Systematically tense and relax each muscle group, promoting physical and emotional release.",
            "Create a comfort playlist: Curate songs that uplift your mood or match your current emotions. Music therapy has been shown to influence emotional regulation.",
            "Practice the 5-4-3-2-1 grounding technique: Name 5 things you see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste."
        ]
    
    return sections

def generate_ai_response(user_input, conversation_history, sentiment):
    response = get_ai_response(sentiment, 0.5, user_input, conversation_history)
    return response['response']

def get_recommendations(emotion, intensity, message_content):
    response = get_ai_response(emotion, intensity, message_content)
    return {
        'recommendations': response['recommendations'],
        'resources': response['resources']
    }

def display_sentiment_analysis(emotion, intensity, scores=None, message_content=None):
    emotion_container = st.container()
    with emotion_container:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(
                f"""
                {EMOTIONS[emotion]['icon']} Current Emotional State
                
                {emotion}
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown("### Intensity Level")
            intensity_percentage = int(intensity * 100)
            st.progress(intensity_percentage / 100)  # تحويل النسبة إلى قيمة بين 0 و1
            st.caption(f"{emotion} Intensity: {'Low' if intensity_percentage < 33 else 'Medium' if intensity_percentage < 66 else 'High'} ({intensity_percentage}%)")

def display_message_with_analysis(msg, show_recommendations=True):
    with st.chat_message(msg.role):
        if msg.role == 'user' and msg.sentiment:
            base_color = EMOTIONS[msg.sentiment]['color']
            gradient_style = f"""
                <style>
                .chat-message-{msg.id} {{
                    background: linear-gradient(to bottom, {base_color}EE, {base_color}00);
                    border-radius: 10px;
                    padding: 10px;
                    margin: 5px 0;
                }}
                </style>
            """
            st.markdown(gradient_style, unsafe_allow_html=True)
            st.markdown(f'<div class="chat-message-{msg.id}">', unsafe_allow_html=True)
        
        st.markdown(msg.content)
        
        if msg.role == 'user' and msg.sentiment:
            display_sentiment_analysis(msg.sentiment, msg.sentiment_score)
            if show_recommendations and getattr(st.session_state, 'recommendations', None):
                with st.expander("💡 Personalized Recommendations", expanded=False):
                    for i, rec in enumerate(st.session_state.recommendations.get('recommendations', []), 1):
                        st.markdown(f"{i}. {rec}")
                    
                    st.markdown("### 🔗 Helpful Resources")
                    for resource in st.session_state.recommendations.get('resources', []):
                        st.markdown(f"• [{resource['title']}]({resource['url']})")
            st.markdown('</div>', unsafe_allow_html=True)

def recognize_speech(language="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)
        text = recognizer.recognize_google(audio, language=language)
        st.success(f"Recognized: {text}")
        return text

# Main chat interface
st.title('AI Mental Health Assistant')

language_options = {
    "English": "en-US",
    "Arabic": "ar-SA",
    "German": "de-DE"
}

language_code = st.selectbox("Select the language of speech", options=list(language_options.keys()), index=0)
language = language_options[language_code]

if 'current_conversation' in st.session_state:
    current_conv = safe_db_operation(
        lambda: Conversation.get_by_id(st.session_state.current_conversation)
    )
    st.subheader(f"Current: {current_conv.title}")
    
    messages = safe_db_operation(
        lambda: list(Message.select().where(
            Message.conversation == current_conv
        ).order_by(Message.created_at))
    )
    
    for msg in messages:
        display_message_with_analysis(msg, show_recommendations=False)

    if st.button("🎤 Use Voice Input"):
        user_input = recognize_speech(language=language)
        emotion, intensity = analyze_sentiment(user_input)
        
        new_user_message = save_message(current_conv, 'user', user_input, emotion, intensity)
        recommendations = get_recommendations(emotion, intensity, user_input)
        st.session_state.recommendations = recommendations
        
        display_message_with_analysis(new_user_message, show_recommendations=True)
        st.session_state.first_message = False
        
        history = "\n".join([f"{m.role}: {m.content}" for m in messages[-5:]])
        response = generate_ai_response(user_input, history, emotion)
        resp_emotion, resp_intensity = analyze_sentiment(response)
        
        new_assistant_message = save_message(current_conv, 'assistant', response, resp_emotion, resp_intensity)
        display_message_with_analysis(new_assistant_message, show_recommendations=False)
        
        current_conv.last_updated = datetime.now()
        current_conv.save()

    if prompt := st.chat_input("Share how you're feeling..."):
        if not prompt.strip():
            st.warning("Please enter a valid message.")
        else:
            emotion, intensity = analyze_sentiment(prompt)
            
            new_user_message = save_message(current_conv, 'user', prompt, emotion, intensity)
            recommendations = get_recommendations(emotion, intensity, prompt)
            st.session_state.recommendations = recommendations
            
            display_message_with_analysis(new_user_message, show_recommendations=True)
            st.session_state.first_message = False
            
            history = "\n".join([f"{m.role}: {m.content}" for m in messages[-5:]])
            response = generate_ai_response(prompt, history, emotion)
            resp_emotion, resp_intensity = analyze_sentiment(response)
            
            new_assistant_message = save_message(current_conv, 'assistant', response, resp_emotion, resp_intensity)
            display_message_with_analysis(new_assistant_message, show_recommendations=False)
            
            current_conv.last_updated = datetime.now()
            current_conv.save()
else:
    st.info("Select a conversation from the sidebar or start a new one")