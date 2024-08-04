# СДЕЛАТЬ

- Сделать настройки

- Пофиксить мелкие баги, если имеются/будут имется

- Сделать установщик чтобы он делал изминения в реестре

- Сделать получение аргументов для запуска файлов:

    ```
    Windows Registry Editor Version 5.00

    [HKEY_CLASSES_ROOT\.mp3]
    @="AudioPlayer.MP3"

    [HKEY_CLASSES_ROOT\AudioPlayer.MP3\DefaultIcon]
    @="C:\\Path\\To\\your_icon.ico"

    [HKEY_CLASSES_ROOT\AudioPlayer.MP3]
    @="Audio-Player type audio file"

    [HKEY_CLASSES_ROOT\AudioPlayer.MP3\shell\open\command]
    @="\"C:\\Path\\To\\Audio-Player.exe\" \"%1\""
    ```

    ```python
    # Пример получения аргументов
    import sys
    import flet as ft

    def main(page: ft.Page):
        # Проверка наличия аргументов командной строки
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            # Обработка файла
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    # Здесь вы можете добавить код для обработки содержимого файла
                    page.add(ft.Text(f"Содержимое файла: {content}"))
            except Exception as e:
                page.add(ft.Text(f"Не удалось открыть файл: {e}"))

        page.add(ft.Text("Приложение Flet готово к работе."))

    if __name__ == "__main__":
        ft.app(target=main)
    ```