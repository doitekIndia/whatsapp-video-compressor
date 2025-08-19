import streamlit as st
import subprocess
import tempfile
import os

st.set_page_config(page_title="WhatsApp Video Helper", layout="centered")
st.title("📱 WhatsApp Video Helper")
st.markdown("""
Easily convert and compress videos for WhatsApp sharing.

- Normal video (<16 MB) ✅
- Document mode (<100 MB) ✅
- Compatible with any format FFmpeg supports ⚠️
- Large Video Warning: Videos over 300 MB may fail to upload.
""")

# Upload video
uploaded_file = st.file_uploader(
    "📂 Drag & drop or select a video",
    type=["mp4", "mov", "avi", "mpeg4"],
    help="Limit 200MB per file"
)

if uploaded_file:
    st.success(f"Uploaded {uploaded_file.name} ({uploaded_file.size / 1e6:.1f} MB)")

    output_type = st.radio(
        "Output type:",
        ("Normal WhatsApp video (<16 MB)", "WhatsApp document (<100 MB)")
    )

    # Set target bitrate based on output type
    if output_type.startswith("Normal"):
        target_bitrate = "800k"  # smaller for <16MB
        scale_width = 640
    else:
        target_bitrate = "1200k"  # for <100MB
        scale_width = 640

    if st.button("Compress & Convert"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_input:
            temp_input.write(uploaded_file.read())
            temp_input_path = temp_input.name

        temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

        cmd = [
            "ffmpeg",
            "-y",
            "-i", temp_input_path,
            "-vcodec", "libx264",
            "-profile:v", "baseline",
            "-level", "3.0",
            "-pix_fmt", "yuv420p",
            "-b:v", target_bitrate,
            "-vf", f"scale={scale_width}:-2",
            "-acodec", "aac",
            "-b:a", "128k",
            temp_output_path
        ]

        try:
            st.info("Processing video...")
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            st.success("Video conversion complete!")

            # Provide download link
            with open(temp_output_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download Converted Video",
                    data=f,
                    file_name=f"converted_{uploaded_file.name}",
                    mime="video/mp4"
                )
        except subprocess.CalledProcessError as e:
            st.error(f"FFmpeg failed:\n{e.stderr.decode()}")
        finally:
            # Cleanup temporary files
            if os.path.exists(temp_input_path):
                os.remove(temp_input_path)
            if os.path.exists(temp_output_path):
                os.remove(temp_output_path)
