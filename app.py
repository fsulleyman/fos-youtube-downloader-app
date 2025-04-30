# --- Updated app.py ---
import os
from datetime import datetime

import streamlit as st

from downloader import download_video, get_video_streams
from scheduler import schedule_download, get_scheduler
from utils import sanitize_filename

# Set up the page
st.set_page_config(page_title="YouTube Video Downloader", layout="wide")
st.title("🎬 YouTube Video Downloader")
st.markdown("""
   This app lets you download YouTube videos using **yt-dlp** (for now ).
    Enter a YouTube URL and click **Download** to get the video.
""")

# Initialize download history in session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar: video URL input and backend selection
st.sidebar.header("Download Options")
url = st.sidebar.text_input("YouTube Video URL")
method = st.sidebar.radio("Downloader Backend", ("pytube", "yt-dlp"))
quality = st.sidebar.selectbox("Select Video Quality", [
    "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"
])
output_dir = "downloads"

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Helper function to append to history
def add_to_history(timestamp, title, method, status):
    st.session_state.history.append({
        "Time": timestamp,
        "Title": title,
        "Method": method,
        "Status": status
    })

# Download Now functionality
if st.sidebar.button("Download Now"):
    if not url:
        st.sidebar.error("Please enter a YouTube URL.")
    else:
        try:
            with st.spinner(f"Downloading with {method}..."):
                if method == "pytube":
                    progress_bar = st.sidebar.progress(0)
                    def progress_fn(stream, chunk, bytes_remaining):
                        total = stream.filesize
                        done = total - bytes_remaining
                        percent = int(done * 100 / total)
                        progress_bar.progress(percent)
                    success, result = download_video(url, method, output_dir, progress_fn, quality)
                else:
                    success, result = download_video(url, method, output_dir, None, quality)

            if success:
                filename = os.path.basename(result)
                title = os.path.splitext(filename)[0]
                st.sidebar.success("Download completed!")
                with open(result, "rb") as fp:
                    st.sidebar.download_button("Download File", data=fp, file_name=filename)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_to_history(timestamp, title, method, "Completed")
            else:
                st.sidebar.error(f"Download failed: {result}")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                add_to_history(timestamp, "", method, f"Failed: {result}")
        except Exception as e:
            st.sidebar.error(f"Unexpected error: {e}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            add_to_history(timestamp, "", method, f"Error: {e}")

# Schedule Download functionality
st.sidebar.header("Schedule Download")
schedule_date = st.sidebar.date_input("Pick a date")
schedule_time = st.sidebar.time_input("Pick a time")
if st.sidebar.button("Schedule Download"):
    if not url:
        st.sidebar.error("Please enter a YouTube URL.")
    else:
        run_datetime = datetime.combine(schedule_date, schedule_time)
        if run_datetime <= datetime.now():
            st.sidebar.error("Scheduled time must be in the future.")
        else:
            try:
                job = schedule_download(url, method, run_datetime)
                st.sidebar.success(f"Download scheduled at {run_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                timestamp = run_datetime.strftime("%Y-%m-%d %H:%M:%S")
                add_to_history(timestamp, "", method, "Scheduled")
            except Exception as e:
                st.sidebar.error(f"Scheduling failed: {e}")

# Display scheduled jobs
st.subheader("📅 Scheduled Downloads")
scheduler = get_scheduler()
jobs = scheduler.get_jobs()
if jobs:
    job_list = [(job.next_run_time.strftime("%Y-%m-%d %H:%M:%S"), *(job.args or ["", ""])) for job in jobs]
    st.table({"Run At": [j[0] for j in job_list], "URL": [j[1] for j in job_list], "Backend": [j[2] for j in job_list]})
else:
    st.info("No downloads scheduled.")

# Display download history with styled table
if st.session_state.history:
    st.subheader("📜 Download History")
    history_table = {key: [item[key] for item in st.session_state.history] for key in ["Time", "Title", "Method", "Status"]}
    st.dataframe(history_table, use_container_width=True, height=300)
else:
    st.info("No download history yet.")
# Footer
st.markdown("""
<hr style="margin-top:50px;">

<div style="text-align:center; color: gray;">
    Developed by <strong>Fuseini Sulleyman</strong> |
    📧 <a href="mailto:sulleymanfuseini1@gmail.com">sulleymanfuseini1@gmail.com</a>
</div>
""", unsafe_allow_html=True)
