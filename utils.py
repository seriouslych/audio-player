import tempfile
import os
import numpy as np

import eyed3
import re
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

from PIL import Image
from collections import Counter
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

def contains_cyrillic(text):
    pattern = re.compile('[\u0400-\u04FF]')
    return bool(pattern.search(text))

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

def scan_directory_for_audio_files(directory):
    supported_extensions = ['.mp3']
    audio_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in supported_extensions):
                audio_files.append(os.path.join(root, file))
    return audio_files

def get_dominant_color(image_path, num_colors=1):
    def rgb_to_hex(rgb):
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    image = Image.open(image_path)
    
    image = image.convert('RGB')
    
    pixels = np.array(image)
    
    pixels = pixels.reshape(-1, 3)
    
    pixels = [tuple(pixel) for pixel in pixels]
    
    counter = Counter(pixels)
    
    most_common = counter.most_common(num_colors)
    
    dominant_color = most_common[0][0]
    return rgb_to_hex(dominant_color)