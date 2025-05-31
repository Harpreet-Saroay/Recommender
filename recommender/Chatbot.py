import streamlit as st
import requests
import pyttsx3
import speech_recognition as sr

def selected_page():

    # Initialize TTS engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech

    # Initialize chat history and mute setting
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are chatting with AI!"}
        ]
    if "mute" not in st.session_state:
        st.session_state.mute = False  # Voice output is ON by default

    # Streamlit page layout
    st.title("💬 Chat with AI")
    st.markdown("----")

    # Top Row: Refresh and Mute/Unmute buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Refresh Chat"):
            st.session_state.messages = [
                {"role": "system", "content": "Chat refreshed. Start a new conversation!"}
            ]

    with col2:
        if st.button("🔇 Mute" if not st.session_state.mute else "🔊 Unmute"):
            st.session_state.mute = not st.session_state.mute

    # Display the chat history
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Option to choose Input Method
    input_mode = st.radio("Choose input method:", ("🖊️ Type", "🎤 Speak"))

    user_input = None

    # Text input mode
    if input_mode == "🖊️ Type":
        user_input = st.chat_input("Type your message here...")

    # Voice input mode
    if input_mode == "🎤 Speak":
        if st.button("🎙️ Click and Speak"):
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("Listening...")
                try:
                    audio = recognizer.listen(source, timeout=10)
                    user_input = recognizer.recognize_google(audio)
                    st.success(f"You said: {user_input}")
                except sr.UnknownValueError:
                    st.error("Sorry, I could not understand your speech.")
                except sr.RequestError as e:
                    st.error(f"Could not request results; {e}")
                except sr.WaitTimeoutError:
                    st.error("Listening timed out. Please try again.")

    # If there is input, send it
    if user_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Send API request
        url = "https://open-ai21.p.rapidapi.com/conversationllama"
        payload = {
            "messages": st.session_state.messages,
            "web_access": False
        }
        headers = {
            "x-rapidapi-key": "794944115fmsh76d05a1427bb5a7p1a409djsn5272edad9d9e",
            "x-rapidapi-host": "open-ai21.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        with st.spinner("Waiting for reply..."):
            response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            reply = data.get("result", "No reply from Llama.")

            # Add assistant message to history
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Show the assistant's reply
            with st.chat_message("assistant"):
                st.markdown(reply)

            # Text-to-Speech: Only if not muted
            if not st.session_state.mute:
                engine.say(reply)
                engine.runAndWait()

        else:
            st.error(f"API Error: {response.status_code}")