import flet as ft

from utils import milliseconds_to_time, extract_album_cover, get_filename, get_metadata

def main(page: ft.Page):
    global playing, paused, src, file, duration, formatted_duration, formatted_time, audio1, released

    page.title = "Audio Player"

    src = ''
    
    playing = False
    paused = False
    released = False
    file = False
    
    audio1 = None
    
    duration = 0
    formatted_duration = "00:00"
    formatted_time = "00:00"

    def open_file(e: ft.FilePickerResultEvent):
        global src, file, audio1, paused, playing, released
        if e.files:
            src = e.files[0].path
            
            file = True
            
            filename = get_filename(src)
            title = get_metadata(src, 'title', filename)
            artist = get_metadata(src, 'artist', 'Неизвестно')
            
            if audio1 is None:
                audio1 = ft.Audio(
                    src=src,
                    autoplay=False,
                    volume=0.5,
                    balance=0,
                    on_loaded=lambda _: print("Loaded"),
                    on_duration_changed=on_duration_changed,
                    on_position_changed=on_position_changed,
                    on_state_changed=lambda e: print("State changed:", e.data),
                    on_seek_complete=lambda _: print("Seek complete"),
                )
                page.overlay.append(audio1)
                page.update()
            else:
                audio1.src = src

            image_path = extract_album_cover(src)

            if image_path:
                cover.content = ft.Image(src=image_path)
            else:
                cover.content = ft.Icon(name=ft.icons.AUDIO_FILE)
                
            song_metadata.controls[0].value = artist
            song_metadata.controls[2].value = title
            cover.update()
            song_metadata.update()
            audio1.update()

            # Reset play/pause state
            playing = False
            paused = False
            playback_button.icon = ft.icons.PLAY_ARROW
            playback_button.on_click = audio_play
            playback_button.update()

    def audio_play(e):
        global playing, paused
        if not playing and not paused and file:
            audio1.play()
            playing = True
            playback_button.icon = ft.icons.PAUSE
            playback_button.on_click = audio_pause
            playback_button.update()

    def audio_pause(e):
        global playing, paused
        if playing and not paused:
            audio1.pause()
            playing = False
            paused = True
            playback_button.icon = ft.icons.PLAY_ARROW
            playback_button.on_click = audio_resume
            playback_button.update()

    def audio_resume(e):
        global playing, paused
        if not playing and paused:
            audio1.resume()
            playing = True
            paused = False
            playback_button.icon = ft.icons.PAUSE
            playback_button.on_click = audio_pause
            playback_button.update()

    def slider_changed(e):
        volume = e.control.value / 100
        audio1.volume = volume
        audio1.update()

    def on_position_changed(e):
        global formatted_time
        current_position = int(e.data)
        formatted_time = milliseconds_to_time(current_position)
        print(f"Current position: {formatted_time}/{formatted_duration}")
        position = (current_position / duration) * 100
        update_time_label(formatted_time, formatted_duration)
        update_seek_slider(position)

    def on_duration_changed(e):
        global duration, formatted_duration
        duration = int(e.data)
        formatted_duration = milliseconds_to_time(duration)
        print("Current duration:", formatted_duration)

    def update_seek_slider(value):
        slider.value = value
        slider.update()

    def set_audio_position(e):
        global duration
        position = (e.control.value / 100) * duration
        int_position = int(position)
        print(f"Setting position to: {int_position} ms")
        audio1.seek(int_position)
        audio1.update()

    def update_time_label(f_pos, f_dur):
        t1.value = f_pos
        t2.value = f_dur
        t1.update()
        t2.update()

    def open_dlg(e):
        e.control.page.dialog = dlg_modal
        dlg_modal.open = True
        e.control.page.update()

    def handle_close(e):
        dlg_modal.open = False
        if e.control.text == "Да":
            page.window_destroy()
        else:
            page.update()
            
    def info(e):
        e.control.page.dialog = dlg_info
        dlg_info.open = True
        e.control.page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Выход"),
        content=ft.Text("Вы точно хотите выйти?"),
        actions=[
            ft.TextButton("Да", on_click=handle_close),
            ft.TextButton("Нет", on_click=handle_close),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    dlg_info = ft.AlertDialog(
        modal=False,
        title=ft.Text("О Audio Player"),
        content=ft.Text("Audio Player 3.0.1 - 30.07.2024\nby seriouslych")
    )

    slider = ft.Slider(
        min=0, max=100, on_change=set_audio_position, expand=True
    )

    volume_slider = ft.Slider(
        min=0, max=100, divisions=20, label="{value}%", on_change=slider_changed, width=350, value=50
    )

    playback_button = ft.IconButton(
        icon=ft.icons.PLAY_ARROW, icon_size=40, on_click=audio_play
    )

    t1 = ft.Text()
    t2 = ft.Text()

    file_picker = ft.FilePicker(on_result=open_file)

    cover = ft.Container(
        content=ft.Icon(name=ft.icons.AUDIO_FILE),
        margin=10,
        alignment=ft.alignment.center,
        bgcolor=ft.colors.BLACK,
        width=250,
        height=250,
        border_radius=10,
    )

    song_metadata = ft.Row(
        [
            ft.Text(value="Неизвестно", size=20), ft.Text(value="-", size=20), ft.Text(value="Неизвестно", size=20)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.bottom_appbar = ft.BottomAppBar(
        content=ft.Row(
            [
                t1, slider, t2, ft.Divider(height=10, color="white"), ft.Icon(name=ft.icons.SPEAKER), volume_slider
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.AUDIOTRACK),
        leading_width=40,
        title=ft.Text("Audio Player"),
        center_title=True,
        bgcolor=ft.colors.PURPLE,
        actions=[
            ft.IconButton(ft.icons.FILE_OPEN, on_click=lambda _: file_picker.pick_files(
                allow_multiple=False, file_type=ft.FilePickerFileType.AUDIO
            )),
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(text="О программе...", on_click=info),
                    ft.PopupMenuItem(
                        text="Выход", on_click=open_dlg
                    ),
                ]
            ),
        ],
    )

    page.overlay.append(file_picker)
    page.add(
        cover,
        song_metadata,
        ft.Container(
            content=playback_button,
            width=100,
            height=60
        )
    )

ft.app(target=main)
