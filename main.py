import flet as ft
from home_page import HomePage
from session_page import SessionPage

def main(page: ft.Page):
    page.title = "Codoro"
    page.f = "assets/icono-codoro.ico"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_width = 700
    page.window_height = 600
    page.window_resizable = True
    page.padding = 20

    home = HomePage(page)
    session = SessionPage(page)

    def on_start_session(mode_data, folder_path):
        session.set_session_data(mode_data, folder_path)
        session.show()

    def on_stop_session():
        from timer import stop_timer
        stop_timer()
        home.show(start_session_callback=on_start_session)

    def on_exit_session():
        from timer import stop_timer
        stop_timer()
        home.show(start_session_callback=on_start_session)

    home.show(start_session_callback=on_start_session)
    session.set_stop_callback(on_stop_session)
    session.set_exit_callback(on_exit_session)

if __name__ == "__main__":
    ft.app(target=main)
