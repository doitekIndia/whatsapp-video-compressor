import streamlit as st
import tempfile
import os
import subprocess
import re

# =========================
# 1️⃣ PAGE SETUP
# =========================
st.set_page_config(
    page_title="📱 WhatsApp Video Helper",
    page_icon="🎬",
    layout="centered",
)

st.title("📱 WhatsApp Video Helper")
st.write("Easily convert and compress videos for WhatsApp sharing.")

st.info(
    "Normal video (<16 MB) ✅\n"
    "Document mode (<100 MB) ✅\n"
    "Compatible with any format FFmpeg supports\n"
    "⚠️ Large Video Warning: Videos over 300 MB may fail to upload.\n"
    "Compress locally first if needed:\n\n"
    "`ffmpeg -i input_video.mp4 -vcodec libx264 -profile:v baseline -level 3.0 "
    "-pix_fmt yuv420p -b:v 1200k -vf \"scale=640:-2\" -acodec aac -b:a 128k output_video.mp4`"
)

# =========================
# 2️⃣ FILE UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "📂 Drag & drop or select a video",
    type=["mp4", "mov", "avi", "mpeg4"],
    accept_multiple_files=False,
)

output_type = st.radio(
    "Output type:",
    ["Normal WhatsApp video (<16 MB)", "WhatsApp document (<100 MB)"],
)

if uploaded_file:
    # Save uploaded file to a temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1])
    tfile.write(uploaded_file.read())
    tfile.close()

    st.write(f"Uploaded `{uploaded_file.name}` ({round(os.path.getsize(tfile.name)/1024/1024, 1)} MB)")

    # =========================
    # 3️⃣ FFmpeg PROCESSING
    # =========================
    with st.spinner("Processing your video…"):
        # Determine output path
        output_suffix = ".mp4"
        output_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=output_suffix)
        output_path = output_tmp.name
        output_tmp.close()

        # Set bitrate/scale based on type
        if output_type == "Normal WhatsApp video (<16 MB)":
            # Aggressive compression for small WhatsApp videos
            vf_scale = "640:-2"
            video_bitrate = "800k"
        else:
            # Slightly higher quality for document mode
            vf_scale = "-2:-2"  # keep original resolution
            video_bitrate = "1200k"

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", tfile.name,
            "-vcodec", "libx264",
            "-profile:v", "baseline",
            "-level", "3.0",
            "-pix_fmt", "yuv420p",
            "-b:v", video_bitrate,
            "-vf", vf_scale,
            "-acodec", "aac",
            "-b:a", "128k",
            "-y",  # overwrite output
            output_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            st.error(f"FFmpeg failed:\n{e.stderr.decode()}")
        else:
            st.success("✅ Video processed successfully!")

            # Display download button
            st.download_button(
                label="⬇️ Download Video",
                data=open(output_path, "rb").read(),
                file_name=f"whatsapp_{os.path.basename(uploaded_file.name)}",
                mime="video/mp4"
            )

    # Cleanup temp files
    try:
        os.remove(tfile.name)
        os.remove(output_path)
    except:
        pass
