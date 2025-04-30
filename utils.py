import re
import logging
import os

def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for filenames.
    Removes or replaces problematic characters.
    """
    # Remove illegal filesystem characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace spaces with underscores
    name = name.strip().replace(" ", "_")
    # Truncate to a reasonable length if necessary
    return name[:200]

# Set up a simple logger (appends to 'downloader.log')
logger = logging.getLogger("youtube_downloader")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("downloader.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
