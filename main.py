import streamlit as st

# Basic page config
st.set_page_config(page_title="Chinese Meme Flashcards")

# Debug message
st.write("App is loading...")

# Test data
flashcard = {
    "chinese": "牛马",
    "pinyin": "niú mǎ",
    "english": "Overworked employees",
    "meme_url": "https://i.imgur.com/TWVsq0o.png"
}

# Basic layout
st.title("Chinese Meme Flashcards")

# Display image
st.image(flashcard["meme_url"])

# Display text
st.header(flashcard["chinese"])
st.write(flashcard["pinyin"])
st.write(flashcard["english"])

# Test button
if st.button("Test Button"):
    st.write("Button clicked!")
