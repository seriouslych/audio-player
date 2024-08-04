import flet as ft

from utils import get_filename, get_metadata, extract_album_cover, contains_cyrillic

class metaData:
    def __init__(self, title: str, cover, artist: str):
        self.title = title
        self.artist = artist
        self.cover = cover

class trackList:
    def __init__(self, number: int, md: metaData, title_rus, artist_rus, on_click):
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

        if title_rus:
            self.metadata.controls[0].font_family = "Montserrat"
        if artist_rus:
            self.metadata.controls[1].font_family = "Montserrat"

    def trackRow(self):
        track_row = ft.Container(
            content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    alignment=ft.MainAxisAlignment.START,
                    spacing=25,
                    tight=True,
                    controls=[
                        self.number,
                        self.cover,
                        self.metadata
                    ],
                ),
            on_click=self.on_click,
            ink=True
        )

        return track_row

def tracks(page: ft.Page, track_queue, color, change_track_by_index):
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
        e.control.page.dialog = dlg_info
        dlg_info.open = True
        e.control.page.update()

    def track_load(e, index):
        page.go("/")
        change_track_by_index(index)

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
        content=ft.Text("Audio Player 4.0.0 - 31.07.2024\nMIT License\nCopyright (c) 2024 Alexander Seriously")
    )

    drawer = ft.NavigationDrawer(
        on_dismiss=handle_drawer_dismissal,
        on_change=handle_drawer_change,
        selected_index=1,
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

    if color:
        appbar.bgcolor = color

    track_controls = []
    for index, track in enumerate(track_queue):
        title = get_metadata(track, 'title', get_filename(track))
        artist = get_metadata(track, 'artist', 'Неизвестно')
        title_rus = contains_cyrillic(title)
        artist_rus = contains_cyrillic(artist)
        image_path = extract_album_cover(track)
        cover = ft.Container(content=ft.Image(src=image_path), width=60, height=60) if image_path else ft.Container(ft.Icon(icon=ft.icons.AUDIO_FILE), width=60, height=60)

        md = metaData(title, cover, artist)
        tl = trackList(index + 1, md, title_rus, artist_rus, on_click=lambda e, idx=index: track_load(e, idx))
        track_controls.append(tl.trackRow())

    track_list_view = ft.ListView(
        controls=track_controls,
        expand=True,
        spacing=10,
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
            drawer=drawer
        )
    )
