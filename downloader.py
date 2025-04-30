import os
from urllib.parse import urlparse

from pytube import YouTube
from pytube.exceptions import RegexMatchError, VideoUnavailable, LiveStreamError
import yt_dlp

from utils import sanitize_filename

# Default directory for downloads
DEFAULT_OUTPUT_DIR = "downloads"

def download_pytube(url: str, output_dir: str = None, progress_callback=None, itag: int = None):
    """
    Download a YouTube video using pytube.
    Returns (success: bool, filepath or error message).
    """
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    try:
        yt = YouTube(url, on_progress_callback=progress_callback)
    except RegexMatchError:
        return False, "Invalid YouTube URL."
    except VideoUnavailable:
        return False, "Video unavailable or restricted."
    except Exception as e:
        return False, f"Error initializing pytube: {e}"

    try:
        # Choose stream
        if itag:
            stream = yt.streams.get_by_itag(itag)
            if not stream:
                return False, f"No stream found with itag {itag}."
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').get_highest_resolution()
            if not stream:
                return False, "No suitable video stream found."

        # Prepare filename
        title = sanitize_filename(yt.title) or "video"
        filename = f"{title}.mp4"
        filepath = stream.download(output_path=output_dir, filename=filename)
        return True, filepath
    except LiveStreamError:
        return False, "Video is a live stream (cannot download)."
    except Exception as e:
        return False, f"Pytube download error: {e}"

def download_ytdlp(url: str, output_dir: str = None, progress_hook=None):
    """
    Download a video using yt-dlp.
    Returns (success: bool, filepath or error message).
    """
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
    }
    if progress_hook:
        ydl_opts["progress_hooks"] = [progress_hook]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return True, filename
    except yt_dlp.utils.DownloadError as e:
        return False, f"yt-dlp download error: {e}"
    except Exception as e:
        return False, f"yt-dlp error: {e}"

def download_video(url: str, method: str, output_dir: str = None, progress_callback=None, itag: int = None):
    """
    Unified download function that selects pytube or yt-dlp.
    """
    if method == "pytube":
        return download_pytube(url, output_dir, progress_callback, itag)
    elif method == "yt-dlp":
        return download_ytdlp(url, output_dir, progress_callback)
    else:
        return False, f"Unknown method '{method}'."

def get_video_streams(url: str):
    """
    Return a list of available progressive video streams for the given URL.
    Each item is a dict with resolution, mime_type, and itag (used for selecting streams).
    """
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        return [
            {
                "resolution": s.resolution,
                "mime_type": s.mime_type,
                "itag": s.itag,
                "fps": s.fps,
                "filesize": s.filesize,
            }
            for s in streams.order_by("resolution").desc()
        ]
    except Exception as e:
        return []
