import streamlit as st

# Debug message
st.write("Testing basic app...")

# Basic page config
st.set_page_config(page_title="Test App")

# Simple test
st.title("Hello World")
if st.button("Click me"):
    st.write("Button clicked!")
