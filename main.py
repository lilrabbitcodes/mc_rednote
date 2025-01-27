import streamlit as st

# Basic page config must be first
st.set_page_config(page_title="Test App")

# Debug message comes after
st.write("Testing basic app...")

# Simple test
st.title("Hello World")
if st.button("Click me"):
    st.write("Button clicked!")
