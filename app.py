import streamlit as st
import subprocess
import tempfile
import os
import re

# ====================================================
# 1️⃣ PAGE SETUP
# ====================================================
st.set_page_config(page_title="WhatsApp Video Helper", layout="centered")
st.title("📱 WhatsApp Video Helper")

# ====================================================
# 2️⃣ DARK MODE TOGGLE
# ====================================================
dark_mode = st.checkbox("🌙 Dark Mode", value=False)

# Inject CSS for dark/light mode
if dark_mode:
    st.markdown("""
        <style>
        .stApp {
            background-color: #111111;
            color: #f0f0f0;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #111111;
        }
        </style>
    """, unsafe_allow_html=True)

# ====================================================
# 3️⃣ INTRODUCTION & FFmpeg LOCAL INSTRUCTIONS
# ====================================================
st.write("""
Easily **convert and compress videos** for WhatsApp sharing.
- Normal video (<16 MB) ✅
- Document mode (<100 MB) ✅
- Compatible with any format FFmpeg supports
""")

st.info('''
⚠️ **Large Video Warning**  
Videos over **300 MB** may fail to upload.  
Compress locally first if needed:

