import tempfile
import os

import eyed3
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

from PIL import Image
from io import BytesIO

def milliseconds_to_time(milliseconds):
    seconds = milliseconds // 1000
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    formatted_time = f"{minutes:02}:{remaining_seconds:02}"
    return formatted_time

def get_filename(src):
    filename = os.path.splitext(os.path.basename(src))[0]
    return filename

def get_metadata(src, tag, default_value):
    audio = MP3(src, ID3=EasyID3)
    
    if audio.get('title') and audio.get('artist') == None:
        return default_value
    
    return audio.get(tag, [default_value])[0]

def extract_album_cover(src):
    audiofile = eyed3.load(src)
    if audiofile.tag is None or not audiofile.tag.images:
        image_path = None
        return image_path
        
    image_data = audiofile.tag.images[0].image_data
    image = Image.open(BytesIO(image_data))
    image.thumbnail((250, 250))
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        image.save(temp_file, format='PNG')
        image_path = temp_file.name
    
    return image_path