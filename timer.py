import threading
import time

timer_state = {
    "remaining_seconds": 0,
    "current_cycle": 1,
    "is_running": False,
    "phase": "work",  # Nuevo: 'work' o 'rest'
}

_timer_thread = None
_timer_lock = threading.Lock()
_stop_event = threading.Event()

def _timer_tick(page, timer_display, initial_state, folder_path, callback, work_minutes, rest_minutes, cycles, phase_callback=None):
    print("[Timer] Thread started")
    while not _stop_event.is_set():
        with _timer_lock:
            if not timer_state["is_running"]:
                print("[Timer] Timer stopped flag detected, exiting thread.")
                break

            if timer_state["current_cycle"] > cycles:
                print("[Timer] Todas las ciclos completadas, saliendo del timer.")
                break

            if timer_state["remaining_seconds"] > 0:
                mins, secs = divmod(timer_state["remaining_seconds"], 60)
                # Mostrar fase actual en timer_display
                phase_emoji = "💼" if timer_state["phase"] == "work" else "🛌"
                timer_display.value = f"{phase_emoji} {mins:02d}:{secs:02d} - Ciclo {timer_state['current_cycle']}/{cycles} ({timer_state['phase']})"
                page.update()
                timer_state["remaining_seconds"] -= 1
            else:
                # Alterna entre trabajo y descanso
                if timer_state["phase"] == "work":
                    # Termina periodo trabajo -> descanso
                    timer_state["phase"] = "rest"
                    timer_state["remaining_seconds"] = rest_minutes * 60
                    print(f"[Timer] Descanso iniciado: {rest_minutes} minutos.")
                else:
                    # Termina descanso -> siguiente ciclo de trabajo
                    timer_state["current_cycle"] += 1
                    if timer_state["current_cycle"] > cycles:
                        print("[Timer] Se completaron todos los ciclos.")
                        break
                    timer_state["phase"] = "work"
                    timer_state["remaining_seconds"] = work_minutes * 60
                    print(f"[Timer] Trabajo iniciado: {work_minutes} minutos.")

                # Informar cambio de fase a UI si hay callback
                if phase_callback:
                    phase_callback(timer_state["phase"])

        time.sleep(1)

    with _timer_lock:
        timer_state["is_running"] = False

    print("[Timer] Thread finalizado.")
    callback()

def start_timer(page, timer_display, initial_state, folder_path, callback, work_minutes, rest_minutes, cycles, phase_callback=None):
    global _timer_thread, timer_state, _stop_event

    with _timer_lock:
        if timer_state["is_running"]:
            print("[Timer] Timer ya está corriendo, ignorando start.")
            return
        # Inicializamos contador si no está activo
        if timer_state["remaining_seconds"] == 0 or timer_state["current_cycle"] > cycles:
            timer_state["remaining_seconds"] = work_minutes * 60
            timer_state["current_cycle"] = 1
            timer_state["phase"] = "work"  # Inicia en work
        timer_state["is_running"] = True

    if _timer_thread and _timer_thread.is_alive():
        print("[Timer] Esperando que thread anterior termine...")
        _stop_event.set()
        _timer_thread.join()

    _stop_event.clear()

    _timer_thread = threading.Thread(target=_timer_tick,
                                     args=(page, timer_display, initial_state, folder_path, callback,
                                           work_minutes, rest_minutes, cycles, phase_callback))
    _timer_thread.daemon = True
    _timer_thread.start()
    print("[Timer] Timer iniciado.")

def stop_timer():
    global _timer_thread, _stop_event
    print("[Timer] stop_timer called")
    with _timer_lock:
        timer_state["is_running"] = False  # Forzar flag a False
    _stop_event.set()
    if _timer_thread and _timer_thread.is_alive():
        print("[Timer] Joining thread to wait for it to stop...")
        _timer_thread.join()
        print("[Timer] Thread stopped")
    else:
        print("[Timer] No active thread to join")

def reset_timer_state():
    global timer_state, _stop_event
    print("[Timer] reset_timer_state llamado")
    with _timer_lock:
        timer_state = {
            "remaining_seconds": 0,
            "current_cycle": 1,
            "is_running": False,
            "phase": "work",
        }
    _stop_event.set()
