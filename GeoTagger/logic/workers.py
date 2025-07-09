from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot
import traceback
import sys


class WorkerSignals(QObject):
    """
    Сигналы, доступные из рабочего потока
    """
    started = Signal()
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    Рабочий поток для выполнения задач в фоне
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Сохраняем аргументы функции
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Добавляем callback для прогресса, если он есть в kwargs
        if 'progress_callback' in kwargs:
            self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        """
        Запускает рабочий поток
        """
        # Сигнал о начале работы
        self.signals.started.emit()

        try:
            # Выполняем функцию
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            # Отправляем сигнал об ошибке
            exctype, value = type(e), str(e)
            traceback_str = traceback.format_exc()
            self.signals.error.emit((exctype, value, traceback_str))
        else:
            # Отправляем результат
            self.signals.result.emit(result)
        finally:
            # Сигнал о завершении
            self.signals.finished.emit()


class GeoTagWorker(QRunnable):
    """
    Специализированный рабочий поток для геотеггинга
    """

    def __init__(self, process_func, folder_path, gpx_path, time_correction):
        super(GeoTagWorker, self).__init__()
        self.process_func = process_func
        self.folder_path = folder_path
        self.gpx_path = gpx_path
        self.time_correction = time_correction
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Запускает обработку геотегов
        """
        self.signals.started.emit()

        try:
            # Выполняем функцию обработки
            result = self.process_func(
                folder_path=self.folder_path,
                gpx_path=self.gpx_path,
                time_correction=self.time_correction,
                progress_callback=self.signals.progress
            )
            self.signals.result.emit(result)
        except Exception as e:
            exctype, value = type(e), str(e)
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()
