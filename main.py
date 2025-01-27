import streamlit as st
import os
import hashlib
from gtts import gTTS

# Must be the first Streamlit command
st.set_page_config(page_title="Chinese Meme Flashcards", layout="centered")

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

.stButton {
    text-align: center;
}

/* Audio player styling */
.stAudio {
    width: 100% !important;
    margin: 5px auto !important;
    display: flex !important;
    justify-content: center !important;
}

.stAudio > audio {
    width: 200px !important;
    height: 40px !important;
}

audio::-webkit-media-controls-panel {
    background-color: #f0f2f6 !important;
}

audio::-webkit-media-controls-play-button {
    transform: scale(1.5) !important;
    margin: 0 10px !important;
}
</style>
""", unsafe_allow_html=True)

def generate_audio(text):
    """Generate audio for the given text in Mandarin"""
    os.makedirs("audio_cache", exist_ok=True)
    audio_path = f"audio_cache/{hashlib.md5(text.encode()).hexdigest()}.mp3"
    
    if not os.path.exists(audio_path):
        try:
            tts = gTTS(text=text, lang='zh-cn', slow=False)
            tts.save(audio_path)
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")
            return None
    
    return audio_path

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
    
    # Generate and display audio
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
