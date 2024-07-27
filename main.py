import os
import pygame
import time
import threading

# Интерфейс
from tkinter import *
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from gif import AnimatedGIF

# Метаданные
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from io import BytesIO
import eyed3

def audio_load():
    global music
    if file:
        mixer = pygame.mixer
        mixer.init()
        music = mixer.music
        music.load(file)

def audio_play():
    global playing, music, paused, start_time, pause_start_time
    if file and not playing:
        music.play()
        playing = True
        paused = False
        start_time = time.time()
        update_time_label()
        threading.Thread(target=monitor_music, daemon=True).start()
    elif paused:
        music.unpause()
        paused = False
        start_time += time.time() - pause_start_time
        update_time_label()
    update_button()

def audio_pause():
    global playing, music, paused, pause_start_time
    if playing:
        music.pause()
        paused = True
        pause_start_time = time.time()
        update_button()

def audio_stop():
    global playing, music, paused
    if playing:
        music.stop()
        playing = False
        paused = False
        update_button()
    
def audio_unload():
    global music, file
    audio_stop()
    music.unload()
    file = None
    start_time = 0
    update_time_label()
    update_metadata_label()

def open_file():
    global file, total_time, audio, file_name
    if file:
        audio_unload()
    
    file = filedialog.askopenfilename(
        title="Open file",
        filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*"))
    )
    
    if file:
        file_name = os.path.splitext(os.path.basename(file))[0]
        audio = MP3(file, ID3=EasyID3)
        total_time = audio.info.length
        audio_load()
        extract_album_cover()
        update_button()
        update_time_label()
        update_metadata_label()

def cat_jam():
    global gif
    if not gif:
        gif = AnimatedGIF(cat_frame, GIF_PATH)

def extract_album_cover():
    global file, cover_image
    if file:
        audiofile = eyed3.load(file)
        if audiofile.tag is None or not audiofile.tag.images:
            cover_image = None
            return
        
        image_data = audiofile.tag.images[0].image_data
        image = Image.open(BytesIO(image_data))
        image.thumbnail((100, 100))
        cover_image = ImageTk.PhotoImage(image)

def get_metadata(tag, default_value):
    global audio
    return audio.get(tag, [default_value])[0]

def update_metadata_label():
    global title_label, artist_label, cover_image
    if file:
        title = get_metadata('title', file_name)
        artist = get_metadata('artist', '')
        
        title_label.config(text=title)
        artist_label.config(text=artist)
        if cover_image:
            cover_label.config(image=cover_image)
        else:
            cover_label.config(image='')
    else:
        title_label.config(text='')
        artist_label.config(text='')
        cover_label.config(image='')

def update_button():
    global gif
    if file:
        if playing and not gif:
            cat_jam()
        play_button.config(state=NORMAL)
        if paused or not playing:
            play_button.config(text="Play", command=audio_play)
            stop_button.config(state=DISABLED)
            if gif:
                gif.stop()
                gif = None
        elif playing:
            play_button.config(text="Pause", command=audio_pause)
            stop_button.config(state=NORMAL)
            if not gif:
                cat_jam()
    else:
        play_button.config(state=DISABLED)
        stop_button.config(state=DISABLED)
        if gif:
            gif.stop()
            gif = None

def update_time_label():
    global play_time, start_time, total_time
    if file and playing and not paused:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        play_time = f"{int(minutes):02}:{int(seconds):02}"
        total_minutes, total_seconds = divmod(total_time, 60)
        total_time_formatted = f"{int(total_minutes):02}:{int(total_seconds):02}"
        time_label.config(text=f"{play_time}/{total_time_formatted}")
        root.after(1000, update_time_label)
    elif file and not playing:
        total_minutes, total_seconds = divmod(total_time, 60)
        total_time_formatted = f"{int(total_minutes):02}:{int(total_seconds):02}"
        time_label.config(text=f"00:00/{total_time_formatted}")
    elif not file and not paused:
        time_label.config(text="")

def update_volume_label():
    global volume_slider, volume_label
    volume_value = volume_slider.get()
    volume_label.config(text=f"{int(volume_value)}%")

def monitor_music():
    global playing
    while playing and not paused:
        if not music.get_busy():
            audio_unload()
        time.sleep(1)

def set_volume(value):
    global music, file
    volume = float(value) / 100
    if file:
        music.set_volume(volume)
    update_volume_label()

def interface():
    global play_button, stop_button, time_label, root, volume_slider, volume_label, title_label, artist_label, cover_label, cat_frame, gif

    root = Tk()
    root.title("Audio Player")
    root.geometry("500x400")
    root.resizable(False, False)

    style = ttk.Style(root)
    style.configure('TFrame', background='#2e3f4f')
    style.configure('TButton', background='#4a6fa5', foreground='black')
    style.configure('TLabel', background='#2e3f4f', foreground='white', font=('Helvetica', 10, 'bold'))
    style.configure('Vertical.TScale', background='#2e3f4f')

    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(expand=True, fill=BOTH)

    button_frame = ttk.Frame(main_frame, padding=10)
    button_frame.pack(side=TOP, anchor=W, fill=X)

    ttk.Button(button_frame, text="Open File", command=open_file).pack(side=LEFT, padx=5)

    play_button = ttk.Button(button_frame, text="Play", command=audio_play, state=DISABLED)
    play_button.pack(side=LEFT, padx=5)

    stop_button = ttk.Button(button_frame, text="Stop", command=audio_stop, state=DISABLED)
    stop_button.pack(side=LEFT, padx=5)

    info_frame = ttk.Frame(main_frame, padding=0)
    info_frame.pack(side=TOP, anchor=W, fill=X)

    cover_label = ttk.Label(info_frame, image=None)
    cover_label.pack(anchor=W, pady=(0, 5))

    title_label = ttk.Label(info_frame, text="")
    title_label.pack(anchor=W, pady=(0, 5))

    artist_label = ttk.Label(info_frame, text="")
    artist_label.pack(anchor=W, pady=(0, 10))

    time_label = ttk.Label(info_frame, text="")
    time_label.pack(anchor=W, pady=(0, 5))

    volume_frame = ttk.Frame(main_frame, padding=5)
    volume_frame.pack(side=RIGHT, anchor=N, fill=Y)

    volume_label = ttk.Label(volume_frame, text="100%")
    volume_label.pack(anchor=N, pady=(0, 5))

    volume_slider = ttk.Scale(volume_frame, from_=100, to=0, orient='vertical', command=set_volume)
    volume_slider.set(100)
    volume_slider.pack(anchor=N, pady=(0, 10))

    cat_frame = ttk.Frame(root, padding=5)
    cat_frame.place(x=500, y=0, anchor=NE)

    gif = None
    update_button()
    root.mainloop()

file = None
music = None
cover_image = None
frames = None

playing = False
paused = False

play_time = "00:00"
start_time = 0
pause_start_time = 0
total_time = 0
frame_idx = 0

GIF_PATH = 'catjam.gif'

interface()
