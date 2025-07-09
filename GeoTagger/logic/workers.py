from PySide6.QtCore import QObject, Signal, QThread
import traceback


# === Общие сигналы потока ===
class WorkerSignals(QObject):
    started = Signal()
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    request_confirm_gps = Signal(str, object)  # Только для GeoTagWorker


# === Универсальный однократный поток ===
class Worker(QThread):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        self.signals.started.emit()
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit((type(e), str(e), traceback.format_exc()))
        finally:
            self.signals.finished.emit()


# === Спец-поток геотеггинга с подтверждениями ===
class GeoTagWorker(QThread):
    def __init__(self, process_func, folder_path, gpx_path, time_correction):
        super().__init__()
        self.func = process_func
        self.folder = folder_path
        self.gpx = gpx_path
        self.correction = time_correction
        self.signals = WorkerSignals()

    def run(self):
        self.signals.started.emit()
        try:
            result = self.func(
                folder_path=self.folder,
                gpx_path=self.gpx,
                time_correction=self.correction,
                confirm_callback=self.ask_confirmation
            )
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit((type(e), str(e), traceback.format_exc()))
        self.signals.finished.emit()

    def ask_confirmation(self, filename):
        result_container = []

        def callback(result):
            result_container.append(result)

        self.signals.request_confirm_gps.emit(filename, callback)

        while not result_container:
            self.msleep(100)

        return result_container[0]
