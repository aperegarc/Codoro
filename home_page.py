import flet as ft

class HomePage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.folder_path = None

        self.session_modes = {
            "Pomodoro (25/5)": {"work": 25, "rest": 5, "cycles": 4},
            "Sesión larga": {"work": 50, "rest": 10, "cycles": 1},
            "Personalizado": {"work": None, "rest": None, "cycles": 1}
        }

        self.status_text = ft.Text(value="", size=14, color="blue")

        self.mode_dropdown = ft.Dropdown(
            label="Selecciona modo de sesión",
            options=[ft.dropdown.Option(k) for k in self.session_modes.keys()],
            value="Pomodoro (25/5)",
            width=250,
            on_change=self.update_duration_inputs
        )

        self.duration_input = ft.TextField(label="Duración trabajo (minutos)", width=200, value="25", disabled=True)
        self.rest_input = ft.TextField(label="Duración descanso (minutos)", width=200, value="5", disabled=True)
        self.cycles_input = ft.TextField(label="Ciclos (pomodoros)", width=200, value="4", disabled=True)

        self.start_button = ft.ElevatedButton("Iniciar sesión", disabled=True, on_click=self.start_session)
        self.folder_picker = ft.FilePicker()
        self.page.overlay.append(self.folder_picker)
        self.folder_picker.on_result = self.on_folder_result

        self.select_folder_button = ft.ElevatedButton("Seleccionar carpeta de proyecto", on_click=self.select_folder)

        self.start_session_callback = None

    def update_duration_inputs(self, e):
        mode = self.mode_dropdown.value
        if mode == "Personalizado":
            self.duration_input.disabled = False
            self.rest_input.disabled = False
            self.cycles_input.disabled = False
        else:
            self.duration_input.disabled = True
            self.rest_input.disabled = True
            self.cycles_input.disabled = True
            self.duration_input.value = str(self.session_modes[mode]["work"])
            self.rest_input.value = str(self.session_modes[mode]["rest"])
            self.cycles_input.value = str(self.session_modes[mode]["cycles"])
        self.page.update()

    def select_folder(self, e):
        self.folder_picker.get_directory_path()

    def on_folder_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.folder_path = e.path
            self.status_text.value = f"📁 Carpeta seleccionada:\n{self.folder_path}"
            self.start_button.disabled = False
            self.page.update()

    def start_session(self, e):
        if not self.folder_path:
            self.status_text.value = "❌ Selecciona una carpeta primero."
            self.page.update()
            return

        mode = self.mode_dropdown.value
        if mode == "Personalizado":
            try:
                work_m = int(self.duration_input.value)
                rest_m = int(self.rest_input.value)
                cycles = int(self.cycles_input.value)
            except:
                self.status_text.value = "❌ Valores personalizados no válidos."
                self.page.update()
                return
        else:
            work_m = self.session_modes[mode]["work"]
            rest_m = self.session_modes[mode]["rest"]
            cycles = self.session_modes[mode]["cycles"]

        # Validación para que no sean 0 ni negativos
        if work_m <= 0 or rest_m < 0 or cycles <= 0:
            self.status_text.value = "❌ Todos los valores deben ser almenos 1"
            self.page.update()
            return

        mode_data = {
            "mode": mode,
            "work": work_m,
            "rest": rest_m,
            "cycles": cycles
        }

        if self.start_session_callback:
            self.start_session_callback(mode_data, self.folder_path)

    def show(self, start_session_callback):
        self.start_session_callback = start_session_callback
        self.page.controls.clear()

        col = ft.Column(
            [
                ft.Text("Codoro", size=36, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                self.select_folder_button,
                self.status_text,
                self.mode_dropdown,
                self.duration_input,
                self.rest_input,
                self.cycles_input,
                self.start_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            tight=False
        )

        container = ft.Container(
            content=col,
            padding=20,
            alignment=ft.alignment.center
        )

        self.page.add(container)
        self.update_duration_inputs(None)
        self.page.update()
