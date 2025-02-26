# AI Mental Health Assistant 🧠

[![GitHub License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-v1.24.0-orange.svg)](https://streamlit.io/)

![AI-Mental-health-Assistant-using-Streamlit](https://github.com/FerasAlshash/AI-Mental-health-Assistant-using-Streamlit/blob/main/AI-Mental-health-Assistant-using-Streamlit.png)


## Introduction 🌟

**AI Mental Health Assistant** is an intelligent application powered by artificial intelligence designed to provide emotional support and guidance to users.
The app analyzes the user's textual or voice inputs, identifies their emotional state, and generates empathetic responses tailored to their current mental condition.

This project aims to create a safe and supportive environment to help individuals manage their emotions in a healthy and structured way.

---

## Key Features 💡

- **Sentiment Analysis**: The app uses advanced machine learning techniques to analyze text or speech and determine the user's emotional state (e.g., joy, sadness, anger, fear).
- **Empathetic Responses**: Utilizes LLM models (e.g., Ollama) to generate compassionate and personalized responses that acknowledge the user's feelings.
- **Personalized Recommendations**: Provides actionable recommendations based on the user's emotional state, including mindfulness exercises, coping strategies, and trusted resources.
- **Voice Input Support**: Allows users to interact with the assistant using voice commands, making it more accessible and user-friendly.
- **Conversation History**: Tracks and stores conversation history for continuity and context-aware interactions.
- **Emotion Visualization**: Displays the user's emotional state with intuitive visualizations, including icons and intensity levels.

---

## How It Works 🔍

1. **User Interaction**: Users can input their thoughts or feelings either through text or voice.
2. **Sentiment Detection**: The app analyzes the input using the VADER sentiment analysis library to detect the user's emotional state.
3. **AI Response Generation**: Based on the detected emotion, the app generates an empathetic response using the Ollama LLM model.
4. **Recommendations & Resources**: The app provides personalized recommendations and links to trusted resources related to the user's emotional state.
5. **Database Integration**: All conversations are stored securely in a database for future reference and context-aware interactions.

---

## Technologies Used 🛠️

- **Frontend**: Streamlit for building the interactive web interface.
- **Sentiment Analysis**: VADER Sentiment Analysis Library for detecting emotions.
- **Natural Language Processing**: Ollama LLM for generating empathetic responses.
- **Speech Recognition**: Python `speech_recognition` library for voice input support.
- **Database**: SQLite for storing conversation history and user data.
- **Backend Logic**: Python for implementing the core functionality of the app.

---

## Installation Guide 📦

To set up and run the AI Mental Health Assistant locally, follow these steps:

### Prerequisites:
- Python 3.8 or higher
- Pip package manager

### Steps:
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-mental-health-assistant.git
   cd ai-mental-health-assistant

# Install dependencies:
pip install -r requirements.txt

# Run the application:
streamlit run app.py

Access the app via your browser at http://localhost:8501 

Usage Instructions 📋
Start a New Chat :
Click the "New Chat" button in the sidebar to begin a new conversation.
Input Your Thoughts :
Type your message in the chat input box or use the microphone icon to record voice input.
View Responses :
The app will analyze your input, display your emotional state, and provide an empathetic response along with personalized recommendations.
Explore Resources :
Click on the "Helpful Resources" section to access trusted articles and guides related to your emotional state.


Contributing 🤝
We welcome contributions from the community to enhance the functionality and usability of this project. To contribute:

Fork the repository.
Create a new branch for your feature or bug fix.
Commit your changes and push them to your fork.
Submit a pull request detailing your changes.


Acknowledgments 🙏
VADER Sentiment Analysis : For providing a robust tool for sentiment detection.
Ollama : For enabling empathetic and context-aware responses.
Streamlit : For simplifying the development of interactive web applications.
Trusted Resources : For offering valuable content to support users' mental well-being.


## Contact Information 📞

For any questions or feedback, feel free to reach out:

- **Email**: [ferasalshash@gmail.com](mailto:ferasalshash@gmail.com)  
- **GitHub**: [FerasAlshash](https://github.com/FerasAlshash)  
- **LinkedIn**: [Feras Alshash](https://www.linkedin.com/in/feras-alshash-bb3106a9/)
