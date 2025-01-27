import streamlit as st

# Must be the first Streamlit command
st.set_page_config(page_title="Chinese Meme Flashcards", layout="centered")

# CSS styles
st.markdown("""
<style>
.stApp {
    background-color: white !important;
    padding: 5px 10px !important;
}

.character {
    font-size: 36px;
    font-weight: bold;
    margin: 10px 0;
    text-align: center;
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
}

.stButton {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

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
    
    # Next button
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Next Card"):
            st.session_state.index = (st.session_state.index + 1) % len(flashcards)
            st.rerun()

if __name__ == "__main__":
    main()
