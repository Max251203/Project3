import sys
import os

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QHeaderView, QTableWidgetItem
)
from PySide6.QtCore import QFile, QTextStream

# UI
from ui.main_window import Ui_MainWindow
from ui.settings_tab import SettingsTab
import ui.resources_rc

# Логика
from logic import file_manager
from logic.exif_handler import process_images, find_exiftool
from logic.gpx_parser import parse_gpx_metadata
from logic.logger import get_logger
from logic.dialog_utils import show_error, show_info, show_warning
from logic.workers import Worker      # универсальный
from logic.workers import GeoTagWorker  # спец. для геотаггинга


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.image_folder = None
        self.gpx_file_path = None
        self.logger = get_logger()
        self.current_theme = "dark"

        self.active_threads = []  # 👉 Храним активные потоки

        self.setup_ui()
        self.connect_signals()
        self.apply_theme(self.current_theme)
        self.logger.info("Приложение запущено")
        self.refresh_logs()

    def setup_ui(self):
        self.setWindowTitle("GeoTagger")
        self.setMinimumSize(900, 600)
        self.ui.tableFiles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Удаляем прогресс-бар визуально и из логики
        if hasattr(self.ui, 'progressBar'):
            self.ui.progressBar.deleteLater()
            self.ui.progressBar = None

        # Увеличим поле поправки
        self.ui.editTimeCorrection.setMinimumHeight(32)
        self.ui.editTimeCorrection.setMinimumWidth(180)

        # Настройки
        self.settings_tab = SettingsTab(self)
        self.ui.verticalLayoutSettings.addWidget(self.settings_tab)

        exiftool = find_exiftool()
        self.settings_tab.update_exiftool_status(exiftool)

    def connect_signals(self):
        self.ui.btnSelectFolder.clicked.connect(self.select_folder)
        self.ui.btnLoadGPX.clicked.connect(self.load_gpx)
        self.ui.btnStart.clicked.connect(self.run_geotagging)
        self.ui.btnClearLogs.clicked.connect(self.clear_logs)
        self.settings_tab.theme_changed.connect(self.apply_theme)
        self.settings_tab.test_data_requested.connect(self.create_test_data)

    def apply_theme(self, theme):
        self.current_theme = theme
        style_file = f":/style/style_{theme}.qss"
        file = QFile(style_file)
        if file.open(QFile.ReadOnly | QFile.Text):
            QApplication.instance().setStyleSheet(QTextStream(file).readAll())
            file.close()

    def update_status(self, message: str):
        self.ui.statusLabel.setText(message)

    def refresh_logs(self):
        self.ui.textEditLogs.setHtml(self.logger.get_text_log())
        scrollbar = self.ui.textEditLogs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        self.logger.clear()
        self.refresh_logs()
        self.logger.info("Логи очищены")
        self.refresh_logs()

    def set_buttons_enabled(self, state: bool):
        self.ui.btnSelectFolder.setEnabled(state)
        self.ui.btnLoadGPX.setEnabled(state)
        self.ui.btnStart.setEnabled(state)

    def cleanup_thread(self, thread):
        if thread in self.active_threads:
            self.active_threads.remove(thread)
        thread.quit()
        thread.wait()

    # ---------------- Загрузка изображений ----------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Выберите папку с изображениями")
        if not folder:
            return
        self.image_folder = folder
        self.load_images(folder)

    def load_images(self, folder):
        self.update_status("Загрузка изображений...")
        self.set_buttons_enabled(False)

        worker = Worker(file_manager.get_image_files, folder)
        self.active_threads.append(worker)
        worker.signals.result.connect(self.on_images_loaded)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.finished.connect(lambda: self.cleanup_thread(worker))
        worker.signals.finished.connect(lambda: self.set_buttons_enabled(True))
        worker.start()

    def on_images_loaded(self, images):
        self.ui.tableFiles.setRowCount(0)
        for i, img in enumerate(images):
            self.ui.tableFiles.insertRow(i)
            self.ui.tableFiles.setItem(i, 0, QTableWidgetItem(img.filename))
            self.ui.tableFiles.setItem(
                i, 1, QTableWidgetItem(img.datetime_original or "-"))
            self.ui.tableFiles.setItem(
                i, 2, QTableWidgetItem(img.gps_string or "-"))
        self.logger.success(f"Загружено {len(images)} изображений")
        self.update_status("Изображения загружены")
        self.refresh_logs()

    # ---------------- Загрузка GPX ----------------
    def load_gpx(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите GPX-файл", filter="*.gpx")
        if not path:
            return

        self.gpx_file_path = path
        self.update_status("Загрузка GPX-файла...")
        self.set_buttons_enabled(False)

        worker = Worker(parse_gpx_metadata, path)
        self.active_threads.append(worker)
        worker.signals.result.connect(self.on_gpx_loaded)
        worker.signals.error.connect(self.on_worker_error)
        worker.signals.finished.connect(lambda: self.cleanup_thread(worker))
        worker.signals.finished.connect(lambda: self.set_buttons_enabled(True))
        worker.start()

    def on_gpx_loaded(self, metadata):
        self.ui.lblStartUTC.setText(metadata["start"])
        self.ui.lblEndUTC.setText(metadata["end"])
        self.ui.lblStartLocal.setText(metadata["start_local"])
        self.logger.success("GPX-файл успешно загружен")
        self.update_status("GPX-файл загружен")
        self.refresh_logs()

    # ---------------- Обработка геотегов ----------------
    def run_geotagging(self):
        if not self.image_folder or not self.gpx_file_path:
            show_warning(self, "Ошибка",
                         "Выберите папку и GPX-файл перед запуском")
            return

        correction = self.ui.editTimeCorrection.text().strip() or "0:00"
        self.logger.info(f"Запуск обработки — поправка {correction}")
        self.update_status("Обработка изображений...")
        self.refresh_logs()
        self.set_buttons_enabled(False)

        from logic.workers import GeoTagWorker
        self.geo_worker = GeoTagWorker(
            process_func=process_images,
            folder_path=self.image_folder,
            gpx_path=self.gpx_file_path,
            time_correction=correction
        )
        self.active_threads.append(self.geo_worker)

        self.geo_worker.signals.result.connect(self.on_geotagging_done)
        self.geo_worker.signals.error.connect(self.on_worker_error)
        self.geo_worker.signals.finished.connect(
            lambda: self.cleanup_thread(self.geo_worker))
        self.geo_worker.signals.finished.connect(
            lambda: self.set_buttons_enabled(True))
        self.geo_worker.signals.request_confirm_gps.connect(
            self.confirm_overwrite_dialog)

        self.geo_worker.start()

    def on_geotagging_done(self, result):
        updated, total = result
        msg = f"Геометки добавлены в {updated} из {total} файлов"
        self.logger.success(msg)
        self.update_status("Геометки добавлены")
        show_info(self, "Готово", msg)
        self.refresh_logs()
        self.load_images(self.image_folder)

    def on_worker_error(self, err):
        exctype, value, trace = err
        self.logger.error(f"Ошибка: {value}")
        self.update_status("Ошибка")
        show_error(self, "Ошибка", value)
        self.refresh_logs()
        self.set_buttons_enabled(True)

    # ---------------- Тестовые данные ----------------
    def create_test_data(self):
        from logic.test_utils import create_test_dataset
        folder = QFileDialog.getExistingDirectory(
            self, "Папка для тестовых данных")
        if not folder:
            return

        self.update_status("Создание тестов...")
        self.set_buttons_enabled(False)

        try:
            result = create_test_dataset(folder)
            if not result:
                raise Exception("Ошибка генерации")

            self.gpx_file_path = result["main_gpx_path"]
            self.image_folder = os.path.dirname(self.gpx_file_path)

            metadata = parse_gpx_metadata(self.gpx_file_path)
            self.ui.lblStartUTC.setText(metadata["start"])
            self.ui.lblEndUTC.setText(metadata["end"])
            self.ui.lblStartLocal.setText(metadata["start_local"])

            self.load_images(self.image_folder)
            self.update_status("Тестовые данные загружены")
            self.logger.success("Тесты созданы")
            show_info(self, "Готово", "Тестовые данные созданы")
            self.refresh_logs()

        except Exception as e:
            self.on_worker_error((type(e), str(e), ""))
        self.set_buttons_enabled(True)

    def confirm_overwrite_dialog(self, filename, callback):
        from logic.dialog_utils import confirm_overwrite_gps
        result = confirm_overwrite_gps(filename)
        callback(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
