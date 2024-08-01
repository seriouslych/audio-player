import flet as ft

from utils import milliseconds_to_time, extract_album_cover, get_filename, get_metadata, scan_directory_for_audio_files, get_dominant_color
import track_list
import rpc

def main(page: ft.Page):
    global playing, paused, src, file, duration, formatted_duration, formatted_time, audio1, released, track_queue, color, current_track_index

    page.title = "Audio Player"

    src = ''
    playing = False
    paused = False
    released = False
    file = False
    audio1 = None
    color = None
    track_queue = []
    current_track_index = 0
    duration = 0
    formatted_duration = "00:00"
    formatted_time = "00:00"

    def open_file(e: ft.FilePickerResultEvent):
        global src, file, audio1, paused, playing, released, title, artist, image_path
        if e.files or e.path:
            src = e.files[0].path
            file = True
            load_track(src)

    def load_track(src):
        global audio1, paused, playing, released, title, artist, image_path, current_track_index, color
        filename = get_filename(src)
        title = get_metadata(src, 'title', filename)
        artist = get_metadata(src, 'artist', 'Неизвестно')

        if audio1 is None:
            audio1 = ft.Audio(
                src=src,
                autoplay=False,
                volume=0.5,
                balance=0,
                on_duration_changed=on_duration_changed,
                on_position_changed=on_position_changed,
                on_state_changed=on_state_changed,
            )
            page.overlay.append(audio1)
            page.update()
        else:
            audio1.src = src

        image_path = extract_album_cover(src)
        if image_path:
            cover.content = ft.Image(src=image_path)
            color = get_dominant_color(image_path, num_colors=1)
        else:
            cover.content = ft.Icon(name=ft.icons.AUDIO_FILE)

        image_name = 'sou'

        if color:
            appbar.bgcolor = color
            appbar.update()

        song_metadata.controls[0].value = artist
        song_metadata.controls[2].value = title
        cover.update()
        song_metadata.update()
        audio1.update()

        playing = False
        paused = False
        
        playback_button.icon = ft.icons.PLAY_ARROW
        playback_button.on_click = audio_play
        playback_button.update()

        rpc.update_discord_rpc(title, artist, image_name)

    def audio_play(e):
        global playing, paused, title, artist, track_queue
        if not playing and file or track_queue:
            audio1.play()
            playing = True
            paused = False
            playback_button.icon = ft.icons.PAUSE
            playback_button.on_click = audio_pause
            playback_button.update()

    def audio_pause(e):
        global playing, paused
        if playing:
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

    def previous_track(e):
        global current_track_index
        if current_track_index > 0:
            current_track_index -= 1
            load_track(track_queue[current_track_index])
            audio_play(None)

    def next_track(e):
        global current_track_index
        if current_track_index < len(track_queue) - 1:
            current_track_index += 1
            load_track(track_queue[current_track_index])
            audio_play(None)
        else:
            audio_pause(None)

    def change_track_by_index(index):
        global current_track_index, playing, paused
        if 0 <= index < len(track_queue) and index != current_track_index:
            current_track_index = index
            load_track(track_queue[index])
            audio_play(None)

    def slider_changed(e):
        volume = e.control.value / 100
        audio1.volume = volume
        audio1.update()

    def on_position_changed(e):
        global formatted_time, formatted_duration, discord_rpc
        current_position = int(e.data)
        formatted_time = milliseconds_to_time(current_position)
        position = (current_position / duration) * 100
        update_time_label(formatted_time, formatted_duration)
        update_seek_slider(position)

    def on_duration_changed(e):
        global duration, formatted_duration
        duration = int(e.data)
        formatted_duration = milliseconds_to_time(duration)

    def on_state_changed(e):
        global track_queue
        if e.data == "completed":
            if track_queue:
                next_track(e)
            else:
                audio_pause(e)

    def update_seek_slider(value):
        slider.value = value
        slider.update()

    def set_audio_position(e):
        global duration
        position = (e.control.value / 100) * duration
        int_position = int(position)
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
    
    def file_alert_dialog_open(e: ft.ControlEvent, file_alert_dialog):
        e.control.page.dialog = file_alert_dialog
        file_alert_dialog.open = True
        e.control.page.update()
        
    
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
        if selected_index == 1 and file or track_queue:
            page.go("/tracks")
        else:
            page.go("/")
            file_alert_dialog = ft.AlertDialog(
                modal=False,
                title=ft.Text("Переход к списку треков"),
                content=ft.Text("Вы должны выбрать файл или директорию!")
            )
            file_alert_dialog_open(e, file_alert_dialog)
            
        drawer.selected_index = 0
        close_drawer()
        
            
    def info(e):
        e.control.page.dialog = dlg_info
        dlg_info.open = True
        e.control.page.update()

    def open_directory_picker(e):
        directory_picker = ft.FilePicker(on_result=select_directory)
        page.overlay.append(directory_picker)
        page.update()
        
        directory_picker.get_directory_path()

    def select_directory(e: ft.FilePickerResultEvent):
        global track_queue, current_track_index
        if e.path:
            directory = e.path
            track_queue = scan_directory_for_audio_files(directory)
            if track_queue:
                current_track_index = 0
                load_track(track_queue[current_track_index])

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
        content=ft.Text("Audio Player 4.0.0 - 01.08.2024\nMIT License\nCopyright (c) 2024 Alexander Seriously")
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

    previous_button = ft.IconButton(
        icon=ft.icons.SKIP_PREVIOUS, icon_size=40, on_click=previous_track
    )

    next_button = ft.IconButton(
        icon=ft.icons.SKIP_NEXT, icon_size=40, on_click=next_track
    )

    playback_buttons = ft.Row(
        [
            previous_button,
            playback_button,
            next_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    t1 = ft.Text()
    t2 = ft.Text()

    file_picker = ft.FilePicker(on_result=open_file)
    page.overlay.append(file_picker)

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
    
    drawer = ft.NavigationDrawer(
        on_dismiss=handle_drawer_dismissal,
        on_change=handle_drawer_change,
        selected_index=0,
        controls=[
            ft.NavigationDrawerDestination(
                icon=ft.icons.PLAY_ARROW,
                label="Сейчас играет",
            ),
            ft.NavigationDrawerDestination(
                icon_content=ft.Icon(ft.icons.MUSIC_NOTE),
                label="Треки",
            ),
            ft.Divider(thickness=2),
            ft.NavigationDrawerDestination(
                icon=ft.icons.SETTINGS,
                label="Настройки"
            ),
        ],
    )
    
    appbar = ft.AppBar(
        leading=ft.IconButton(ft.icons.MENU_ROUNDED, on_click=open_drawer),
        leading_width=40,
        title=ft.Text("Audio Player"),
        center_title=True,
        bgcolor=ft.colors.PURPLE,
        actions=[
            ft.IconButton(ft.icons.FOLDER_OPEN, on_click=open_directory_picker),
            ft.IconButton(ft.icons.FILE_OPEN, on_click=lambda _: file_picker.pick_files(
                allow_multiple=False, allowed_extensions=["mp3"]
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

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [
                        appbar,
                        cover,
                        song_metadata,
                        ft.Container(
                            content=playback_buttons,
                            width=205,
                            height=60
                        ),
                        ft.BottomAppBar(
                            content=ft.Row(
                                [
                                    t1, slider, t2, ft.Divider(height=10, color="white"), ft.Icon(name=ft.icons.SPEAKER), volume_slider
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        ),
                    ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    drawer=drawer
                )
            )
            page.update()
            
        elif page.route == "/tracks":
            track_list.tracks(page, track_queue, color, change_track_by_index=change_track_by_index)
            page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)
