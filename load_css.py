import streamlit as st
import os

def load_custom_css(css_file : str):
    assert os.path.exists(css_file), f"The {css_file = } does not exist"
    with open(css_file) as f:st.html(f'<style>{f.read()}</style>')