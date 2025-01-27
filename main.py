import streamlit as st

st.title("Chinese Meme Flashcards")
st.write("Testing deployment...")

# Add just one flashcard to test
flashcard = {
    "chinese": "牛马",
    "pinyin": "niú mǎ",
    "english": "Overworked employees",
    "meme_url": "https://i.imgur.com/TWVsq0o.png"
}

st.image(flashcard["meme_url"])
st.write(flashcard["chinese"])
