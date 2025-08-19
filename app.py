import streamlit as st
import subprocess
import tempfile
import os
import re
from moviepy.editor import VideoFileClip

# =========================
# 1️⃣ PAGE SETUP
# =========================
st.set_page_config(page_title="WhatsApp Video Helper", layout="centered")
st.title("📱 WhatsApp Video Helper")

# =========================
# 2️⃣ DARK MODE TOGGLE
# =========================
dark_mode = st.checkbox("🌙 Dark Mode", value=False)
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

# =========================
# 3️⃣ INTRO & LOCAL FFmpeg TIP
# =========================
st.write("""
Easily **convert and compress videos** for WhatsApp sharing.
- Normal video (<16 MB) ✅
- Document mode (<100 MB) ✅
- Compatible with any format FFmpeg supports
""")

st.info("""
⚠️ **Large Video Warning**  
Videos over **300 MB** may fail to upload.  
Compress locally first if needed:

`ffmpeg -i input_video.mp4 -vcodec libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p -b:v 1200k -vf "scale=640:-2" -acodec aac -b:a 128k output_video.mp4`
""")

# =========================
# 4️⃣ LAYOUT: UPLOAD + OUTPUT OPTIONS
# =========================
col1, col2 = st.columns([3, 1])
with col2:
    target_option = st.radio(
        "Output type:",
        ["Normal WhatsApp video (<16 MB)", "WhatsApp document (<100 MB)"]
    )
with col1:
    uploaded_file = st.file_uploader(
        "📂 Drag & drop or select a video",
        type=["mp4", "mov", "avi"]
    )

# =========================
# 5️⃣ PROCESSING & COMPRESSION
# =========================
if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    output_path = input_path.replace(".mp4", "_whatsapp.mp4")

    if st.button("▶️ Convert & Compress"):
        st.text("Processing your video…")
        st.write("")
        progress_bar = st.progress(0)
        progress_text = st.empty()

        try:
            # ✅ Get video duration with moviepy
            clip = VideoFileClip(input_path)
            duration = clip.duration
            clip.close()

            # Determine target size
            target_size_mb = 16 if target_option.startswith("Normal") else 100

            # Calculate bitrates
            target_bitrate = (target_size_mb * 8192) / duration  # kbps
            audio_bitrate = 128  # kbps
            video_bitrate = int(target_bitrate - audio_bitrate)
            if video_bitrate < 300:
                video_bitrate = 300

            # Build FFmpeg command
            ffmpeg_cmd = [
                "ffmpeg", "-i", input_path,
                "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0",
                "-pix_fmt", "yuv420p",
                "-b:v", f"{video_bitrate}k", "-maxrate", f"{video_bitrate+100}k", "-bufsize", f"{video_bitrate*2}k",
                "-vf", "scale=640:-2",
                "-c:a", "aac", "-b:a", f"{audio_bitrate}k",
                output_path,
                "-y"
            ]

            # Run FFmpeg with progress tracking
            process = subprocess.Popen(
                ffmpeg_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            for line in process.stdout:
                match = re.search(r'time=(\d+):(\d+):(\d+)\.(\d+)', line)
                if match:
                    h, m, s, ms = match.groups()
                    elapsed_seconds = int(h)*3600 + int(m)*60 + int(s) + int(ms)/100
                    progress = min(elapsed_seconds / duration, 1.0)
                    progress_bar.progress(progress)
                    progress_text.text(f"Processing... {int(progress*100)}%")
            process.wait()

            # Check final file size
            final_size_mb = os.path.getsize(output_path) / (1024*1024)
            if final_size_mb > target_size_mb:
                st.warning(
                    f"⚠️ Output video is slightly larger ({final_size_mb:.1f} MB). "
                    "Consider reducing bitrate or resolution."
                )

            # Download button
            st.success("✅ Your video is ready for WhatsApp!")
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Video",
                    data=f,
                    file_name="video_whatsapp.mp4",
                    mime="video/mp4"
                )

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")

        os.remove(input_path)
