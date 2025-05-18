import flet as ft
from timer import start_timer, stop_timer, reset_timer_state, timer_state
from file_watcher import compare_files, generate_code_from_diff, save_initial_state
from summarizer import summarize_code
from datetime import datetime

class SessionPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.start_session_callback = None
        self.stop_callback = None
        self.exit_callback = None

        self.output_status = ft.Text(value="", size=14, color="blue")
        self.output_ia = ft.TextField(value="", width=600, height=300, multiline=True, disabled=True)
        self.timer_display = ft.Text(value="", size=30, weight=ft.FontWeight.BOLD)

        self.start_button = ft.ElevatedButton("Iniciar sesión")
        self.start_button.on_click = self.start_stop_session

        self.exit_button = ft.ElevatedButton("Salir")
        self.exit_button.on_click = self.exit_session
        self.exit_button.disabled = False

        self.session_start_time = None
        self.initial_state = {}
        self.folder_path = None
        self.mode_data = None

    def set_exit_callback(self, callback):
        self.exit_callback = callback

    def set_session_data(self, mode_data, folder_path):
        self.mode_data = mode_data
        self.folder_path = folder_path

        stop_timer()
        reset_timer_state()

        self.output_status.value = ""
        self.output_ia.value = ""
        self.timer_display.value = ""
        self.start_button.text = "Iniciar sesión"
        self.exit_button.disabled = False
        self.page.update()

    def set_stop_callback(self, callback):
        self.stop_callback = callback

    def show(self):
        self.page.controls.clear()

        col = ft.Column(
            [
                self.output_status,
                self.start_button,
                self.exit_button,
                self.timer_display,
                self.output_ia
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        )

        container = ft.Container(
            content=col,
            padding=20,
            alignment=ft.alignment.center
        )

        self.page.add(container)
        self.page.update()

    def start_stop_session(self, e):
        if not self.folder_path:
            self.output_status.value = "❌ Selecciona una carpeta primero."
            self.page.update()
            return

        if self.start_button.text == "Iniciar sesión":
            if timer_state["is_running"]:
                self.output_status.value = "⏳ La sesión ya está en curso."
                self.page.update()
                return

            work_m = self.mode_data["work"]
            rest_m = self.mode_data["rest"]
            cycles = self.mode_data["cycles"]

            self.output_status.value = "🕒 Iniciando sesión..."
            self.output_ia.value = ""
            self.page.update()

            if timer_state["remaining_seconds"] == 0 or timer_state["current_cycle"] > cycles:
                self.initial_state = save_initial_state(self.folder_path)
                self.session_start_time = datetime.now()

            start_timer(self.page, self.timer_display, self.initial_state, self.folder_path,
                        self.process_summary_and_save,
                        work_m, rest_m, cycles)

            self.start_button.text = "Parar sesión"
            self.exit_button.disabled = True
            self.page.update()

        else:
            self.stop_session()

    def stop_session(self):
        print(f"[stop_session] is_running antes de stop: {timer_state['is_running']}")

        if timer_state["is_running"]:
            self.timer_display.value = "⏹️ Temporizador detenido"
            self.output_status.value = "🛑 Sesión ya estaba detenida."
            self.start_button.text = "Iniciar sesión"
            self.exit_button.disabled = False
            self.page.update()
            print("[stop_session] Timer ya estaba parado, saliendo.")
            return

        stop_timer()  # Esto ahora espera al thread

        print(f"[stop_session] is_running después de stop: {timer_state['is_running']}")

        self.timer_display.value = "⏹️ Temporizador detenido"
        self.output_status.value = "🛑 Sesión detenida por el usuario."
        self.start_button.text = "Iniciar sesión"
        self.exit_button.disabled = False
        self.page.update()

    def reset_session(self):
        stop_timer()
        reset_timer_state()

        self.initial_state = {}
        self.session_start_time = None
        self.mode_data = None
        self.folder_path = None

        self.output_status.value = ""
        self.output_ia.value = ""
        self.timer_display.value = ""
        self.start_button.text = "Iniciar sesión"
        self.exit_button.disabled = False
        self.page.update()

    def exit_session(self, e):
        if timer_state["is_running"]:
            self.output_status.value = "❌ Para salir, primero para la sesión."
            self.page.update()
            return

        self.reset_session()
        if self.exit_callback:
            self.exit_callback()

    def process_summary_and_save(self):
        try:
            changes = compare_files(self.initial_state, self.folder_path)
            resumen_input = generate_code_from_diff(changes)
            self.output_ia.value = "⏳ Generando resumen IA, espera por favor..."
            self.page.update()

            summary_text = summarize_code(resumen_input)
            self.output_ia.value = f"📋 Resumen IA:\n{summary_text}"
            self.page.update()

            from utils import save_changes_to_file
            save_changes_to_file(changes, self.folder_path, self.session_start_time, datetime.now())

        except Exception as e:
            self.output_ia.value = f"❌ Error al generar resumen: {e}"
            self.page.update()

            def _callback_after_timer(self):
                # Se llama al finalizar el timer o al parar
                self.process_summary_and_save()

                # Si terminaron los ciclos, cambiamos texto botón y activamos salir
                if timer_state["current_cycle"] > self.mode_data["cycles"]:
                    self.output_status.value = "✅ Todos los ciclos han finalizado."
                    self.start_button.text = "Volver a empezar"
                    self.exit_button.disabled = False
                    self.page.update()
