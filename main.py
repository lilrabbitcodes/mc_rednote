import streamlit as st
import os
import hashlib

# Must be the first Streamlit command
st.set_page_config(page_title="Chinese Meme Flashcards", layout="centered")

# At the top of the file, add more detailed error handling
try:
    from gtts import gTTS
    AUDIO_ENABLED = True
except ImportError as e:
    AUDIO_ENABLED = False
    st.error(f"Detailed error: {str(e)}")
    st.warning("Audio functionality is not available. Installing required packages...")
    try:
        import subprocess
        subprocess.check_call(["pip", "install", "gTTS==2.5.0", "click>=7.0"])
        from gtts import gTTS
        AUDIO_ENABLED = True
        st.success("Successfully installed audio packages!")
    except Exception as e:
        st.error(f"Failed to install packages: {str(e)}")

# CSS styles
st.markdown("""
<style>
.stApp {
    background-color: white !important;
    padding: 5px 10px !important;
    color: black !important;
}

.character {
    font-size: 36px;
    font-weight: bold;
    margin: 10px 0;
    text-align: center;
    color: black !important;
}

.pinyin {
    font-size: 18px;
    color: #666;
    margin: 5px 0;
    text-align: center;
}

.explanation {
    font-size: 16px;
    margin: 10px 0;
    text-align: center;
    text-transform: uppercase;
    font-weight: bold;
    color: black !important;
}

/* Button styling */
.stButton {
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
}

.stButton > button {
    background-color: white !important;
    color: black !important;
    border: 2px solid black !important;
    border-radius: 5px !important;
    padding: 5px 15px !important;
    font-weight: 500 !important;
    margin: 0 auto !important;
}

.stButton > button:hover {
    background-color: #f0f0f0 !important;
    border-color: black !important;
}

/* Audio player styling */
.stAudio {
    width: 50% !important;
    margin: 5px auto !important;
    display: flex !important;
    justify-content: center !important;
}

.stAudio > audio {
    width: 90px !important;
    height: 30px !important;
}

audio::-webkit-media-controls-panel {
    background-color: #e0e0e0 !important;
}

audio::-webkit-media-controls-play-button {
    transform: scale(1.2) !important;
    margin: 0 8px !important;
}

audio::-webkit-media-controls-current-time-display,
audio::-webkit-media-controls-time-remaining-display {
    color: white !important;
    font-size: 12px !important;
}

/* Center column content */
[data-testid="column"] {
    display: flex !important;
    justify-content: center !important;
}
</style>
""", unsafe_allow_html=True)

def generate_audio(text):
    """Generate audio for the given text in Mandarin"""
    if not AUDIO_ENABLED:
        return None
        
    try:
        os.makedirs("audio_cache", exist_ok=True)
        audio_path = f"audio_cache/{hashlib.md5(text.encode()).hexdigest()}.mp3"
        
        if not os.path.exists(audio_path):
            tts = gTTS(text=text, lang='zh-cn', slow=False)
            tts.save(audio_path)
        
        return audio_path
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None

# Flashcard data
flashcards = [
    {
        "chinese": "牛马",
        "pinyin": "niú mǎ",
        "english": "Overworked employees, treated like animals",
        "meme_url": "https://i.imgur.com/TWVsq0o.png"
    },
    {
        "chinese": "摸鱼",
        "pinyin": "mō yú",
        "english": "Slacking off, quiet quitting",
        "meme_url": "https://i.imgur.com/sRUAKan.png"
    },
    # ... (add all other flashcards here)
]

def main():
    # Initialize session state
    if 'index' not in st.session_state:
        st.session_state.index = 0

    # Get current flashcard
    current_card = flashcards[st.session_state.index]
    
    # Display media
    st.markdown(f'''
        <div style="width:100%;max-width:350px;margin:0 auto;">
            <img src="{current_card['meme_url']}" 
                 style="width:100%;border-radius:15px;object-fit:cover;">
        </div>
    ''', unsafe_allow_html=True)
    
    # Display text
    st.markdown(f"""
        <div class="character">{current_card['chinese']}</div>
        <div class="pinyin">{current_card['pinyin']}</div>
        <div class="explanation">{current_card['english']}</div>
    """, unsafe_allow_html=True)
    
    # Generate and display audio only if enabled
    if AUDIO_ENABLED:
        audio_path = generate_audio(current_card["chinese"])
        if audio_path and os.path.exists(audio_path):
            st.audio(audio_path, format='audio/mp3')
    
    # Next button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Next Card"):
            st.session_state.index = (st.session_state.index + 1) % len(flashcards)
            st.rerun()

if __name__ == "__main__":
    main()
