import pygame
import time
import threading

from tkinter import *
from tkinter import ttk, filedialog

def audio_play():
    global playing, music, paused, start_time, pause_start_time
    if file and not playing:
        mixer = pygame.mixer
        mixer.init()
        music = mixer.music
        
        music.load(file)
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

def open_file():
    global file
    if file:
        audio_unload()
    
    file = filedialog.askopenfilename(
        title="Open file",
        filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*"))
    )
    
    update_button()

def update_button():
    if file:
        play_button.config(state=NORMAL)
        if paused or not playing:
            play_button.config(text="Play", command=audio_play)
            stop_button.config(state=DISABLED)
        elif playing:
            play_button.config(text="Pause", command=audio_pause)
            stop_button.config(state=NORMAL)
    else:
        play_button.config(state=DISABLED)
        stop_button.config(state=DISABLED)

def update_time_label():
    global play_time, start_time
    if playing and not paused:
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        play_time = f"{int(minutes):02}:{int(seconds):02}"
        time_label.config(text=play_time)
        root.after(1000, update_time_label)
    elif not playing:
        time_label.config(text="00:00")

def monitor_music():
    global playing
    while playing and not paused:
        if not music.get_busy():
            audio_unload()
        time.sleep(1)

def interface():
    global play_button, stop_button, time_label, root
    root = Tk()

    frm = ttk.Frame(root, padding=100)
    frm.grid()

    ttk.Button(frm, text="File", command=open_file).grid(column=0, row=0)

    play_button = ttk.Button(frm, text="Play", command=audio_play, state=DISABLED)
    play_button.grid(column=0, row=1)
    
    stop_button = ttk.Button(frm, text="Stop", command=audio_stop, state=DISABLED)
    stop_button.grid(column=0, row=2)
    
    time_label = ttk.Label(frm, text="00:00")
    time_label.grid(column=1, row=2)

    update_button()

    root.title("Audio Player")
    root.mainloop()

file = None
music = None

playing = False
paused = False
play_time = "00:00"
start_time = 0
pause_start_time = 0

interface()
