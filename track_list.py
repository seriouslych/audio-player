import flet as ft
import asyncio
import os
import hashlib
import time
import threading
import json
import re
from PIL import Image
from utils import get_filename, get_metadata, extract_album_cover, contains_cyrillic

CACHE_DIR = "cache"
CACHE_EXPIRATION_TIME = 7 * 24 * 60 * 60  # 7 days in seconds
CACHE_CLEANUP_INTERVAL = 24 * 60 * 60  # 24 hours in seconds
HASH_MAP_FILE = os.path.join(CACHE_DIR, "cover_hash_map.json")

# In-memory cache for image hashes
hash_cache = {}

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def load_hash_map():
    if os.path.exists(HASH_MAP_FILE):
        with open(HASH_MAP_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_hash_map(hash_map):
    with open(HASH_MAP_FILE, 'w') as f:
        json.dump(hash_map, f)

def hash_image(image_path):
    """Calculate the MD5 hash of an image file, using an in-memory cache."""
    if image_path in hash_cache:
        return hash_cache[image_path]

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img_data = img.tobytes()
        img_hash = hashlib.md5(img_data).hexdigest()
        hash_cache[image_path] = img_hash
        return img_hash

def get_cached_cover(track):
    """Get or cache the album cover for a track."""
    image_path = extract_album_cover(track)
    
    if image_path:
        cover_hash = hash_image(image_path)
        cached_cover_path = os.path.join(CACHE_DIR, f"{cover_hash}.png")
        
        hash_map = load_hash_map()

        if cover_hash in hash_map and os.path.exists(hash_map[cover_hash]):
            cached_cover_path = hash_map[cover_hash]
            os.utime(cached_cover_path, None)  # Update access time
            return cached_cover_path

        # Cache the new cover
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            with open(cached_cover_path, 'wb') as cache_file:
                cache_file.write(img_data)
        
        hash_map[cover_hash] = cached_cover_path
        save_hash_map(hash_map)
        return cached_cover_path

    return None

def cleanup_cache():
    """Periodically clean up expired cache files."""
    while True:
        now = time.time()
        hash_map = load_hash_map()
        for cover_hash, file_path in list(hash_map.items()):
            if os.path.isfile(file_path):
                last_access_time = os.path.getatime(file_path)
                if now - last_access_time > CACHE_EXPIRATION_TIME:
                    os.remove(file_path)
                    del hash_map[cover_hash]
        save_hash_map(hash_map)
        time.sleep(CACHE_CLEANUP_INTERVAL)

# Start the cache cleanup in a separate daemon thread
cleanup_thread = threading.Thread(target=cleanup_cache, daemon=True)
cleanup_thread.start()

class metaData:
    def __init__(self, title: str, cover, artist: str):
        self.title = title
        self.artist = artist
        self.cover = cover

class trackList:
    def __init__(self, number: int, md: metaData, title_rus, artist_rus, is_current, on_click):
        self.number = ft.Text(value=str(number), size=20)
        self.metadata = ft.Column(
            [
                ft.Text(value=md.title, size=15),
                ft.Text(value=md.artist, size=12)
            ],
            spacing=5, tight=True
        )
        self.cover = md.cover
        self.on_click = on_click
        self.is_current = is_current

        if title_rus:
            self.metadata.controls[0].font_family = "Montserrat"
        if artist_rus:
            self.metadata.controls[1].font_family = "Montserrat"

    def trackRow(self):
        track_row = ft.Container(
            key=self.number.value,  # Присваиваем ключ как номер трека
            content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    alignment=ft.MainAxisAlignment.START,
                    spacing=25,
                    tight=True,
                    controls=[
                        self.number,
                        self.cover,
                        self.metadata,
                    ],
                ),
            on_click=self.on_click,
            ink=True
        )
                # Подсветка текущего трека
        if self.is_current:
            track_row = ft.Container(
                content=track_row, 
                border=ft.border.all(2, ft.colors.WHITE),
                border_radius=5,
            )

        return track_row

def tracks(page: ft.Page, track_queue, current_track_index, color, change_track_by_index):
    def open_dlg(e):
        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        page.update()

    def handle_close(e):
        dlg_modal.open = False
        if e.control.text == "Yes":
            page.window.destroy()
        else:
            page.update()

    def open_drawer(e):
        drawer.open = True
        page.update()

    def close_drawer():
        drawer.open = False
        page.update()

    def handle_drawer_dismissal(e):
        pass

    def handle_drawer_change(e):
        selected_index = drawer.selected_index
        if selected_index == 0:
            page.go("/")
        drawer.selected_index = 1
        close_drawer()

    def info(e):
        page.overlay.append(dlg_info)
        dlg_info.open = True
        page.update()

    def track_load(e, index):
        page.go("/")
        change_track_by_index(index)

    def filter_tracks(e):
        search_query = e.control.value.lower()
        filtered_tracks = []
        for index, track in enumerate(track_queue):
            title = get_metadata(track, 'title', get_filename(track))
            artist = get_metadata(track, 'artist', 'Unknown')
            if re.search(search_query, title.lower()) or re.search(search_query, artist.lower()):
                title_rus = contains_cyrillic(title)
                artist_rus = contains_cyrillic(artist)
                image_path = get_cached_cover(track)
                cover = ft.Container(content=ft.Image(src=image_path), width=60, height=60) if image_path else ft.Container(ft.Icon(ft.icons.AUDIO_FILE), width=60, height=60)

                is_current = (index == current_track_index)
                md = metaData(title, cover, artist)
                tl = trackList(index + 1, md, title_rus, artist_rus, is_current, on_click=lambda e, idx=index: track_load(e, idx))
                filtered_tracks.append(tl.trackRow())
        
        track_list_view.controls = filtered_tracks
        page.update()

    def open_search_bar(e):
        search_animation.content = search_bar
        page.update()

    def close_search_bar(e):
        search_animation.content = search_button
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Exit"),
        content=ft.Text("Are you sure you want to exit?"),
        actions=[
            ft.TextButton("Yes", on_click=handle_close),
            ft.TextButton("No", on_click=handle_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dlg_info = ft.AlertDialog(
        modal=False,
        title=ft.Text("About Audio Player"),
        content=ft.Text("Audio Player 5.0.0 - 10.08.2024\nMIT License\nCopyright (c) 2024 Alexander Seriously")
    )

    drawer = ft.NavigationDrawer(
        on_dismiss=handle_drawer_dismissal,
        on_change=handle_drawer_change,
        selected_index=1,
        controls=[
            ft.NavigationDrawerDestination(
                icon=ft.icons.PLAY_ARROW,
                label="Now Playing",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.MUSIC_NOTE),
                label="Track List",
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                icon=ft.icons.SETTINGS,
                label="Settings"
            ),
        ],
    )

    search_bar = ft.Row(
        controls=[
        ft.IconButton(icon=ft.icons.CANCEL, on_click=close_search_bar),
        ft.SearchBar(
                bar_hint_text="Search tracks...",
                on_change=filter_tracks,
                on_submit=filter_tracks,
                width=300,
                autofocus=True,
            )
        ]
    )
    
    search_button = ft.IconButton(
                icon=ft.icons.SEARCH,
                on_click=open_search_bar
            )

    search_animation = ft.AnimatedSwitcher(
        search_button,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=400,
        reverse_duration=150,
        switch_in_curve=ft.AnimationCurve.EASE_IN_EXPO,
        switch_out_curve=ft.AnimationCurve.BOUNCE_OUT
    )

    appbar = ft.AppBar(
        leading=ft.IconButton(ft.icons.MENU_ROUNDED, on_click=open_drawer),
        leading_width=40,
        title=ft.Text("Audio Player"),
        center_title=True,
        bgcolor=ft.colors.PURPLE,
        actions=[
            search_animation,
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="About...", on_click=info),
                    ft.PopupMenuItem(
                        text="Exit", on_click=open_dlg
                    ),
                ]
            ),
        ],
    )

    if color:
        appbar.bgcolor = color

    track_controls = []
    progress_ring = ft.Container(
        content=ft.Column(
            controls=[ft.ProgressRing(width=60, height=60, stroke_width=8)],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
        alignment=ft.alignment.center,  # This ensures the container itself is centered
        expand=True
    )

    async def load_tracks():
        page.overlay.append(progress_ring)
        page.update()
        for index, track in enumerate(track_queue):
            title = get_metadata(track, 'title', get_filename(track))
            artist = get_metadata(track, 'artist', 'Unknown')
            title_rus = contains_cyrillic(title)
            artist_rus = contains_cyrillic(artist)
            image_path = get_cached_cover(track)
            cover = ft.Container(content=ft.Image(src=image_path), width=60, height=60) if image_path else ft.Container(ft.Icon(ft.icons.AUDIO_FILE), width=60, height=60)
            is_current = (index == current_track_index)
            md = metaData(title, cover, artist)
            tl = trackList(index + 1, md, title_rus, artist_rus, is_current, on_click=lambda e, idx=index: track_load(e, idx))
            track_controls.append(tl.trackRow())
        page.overlay.remove(progress_ring)
        page.update()

    track_list_view = ft.ListView(
        controls=track_controls,
        expand=True,
        spacing=10,
        auto_scroll=False,
    )

    container = ft.Container(
        content=track_list_view,
        border=ft.border.all(1, ft.colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True,
    )

    page.views.append(
        ft.View(
            "/tracks",
            [
                appbar,
                container
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            drawer=drawer,
        )
    )

    asyncio.run(load_tracks())
