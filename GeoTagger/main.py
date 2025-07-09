import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QHeaderView, QTableWidgetItem
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream

# UI
from ui.main_window import Ui_MainWindow
import ui.resources_rc
from ui.settings_tab import SettingsTab

# Логика
from logic import file_manager
from logic.gpx_parser import parse_gpx_metadata
from logic.exif_handler import process_images
from logic.dialog_utils import show_warning, show_info, show_error
from logic.logger import get_logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Инициализация UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Состояние
        self.image_folder = None
        self.gpx_file_path = None
        self.current_theme = "dark"  # Тема по умолчанию
        self.logger = get_logger()

        # Настройка UI
        self.setup_ui()
        self.connect_signals()
        self.apply_theme(self.current_theme)

        # Логи
        self.logger.info("Приложение запущено")
        self.refresh_logs()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("GeoTagger")
        self.setMinimumSize(800, 600)

        # Настройка таблицы
        self.ui.tableFiles.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Добавляем вкладку настроек
        self.settings_tab = SettingsTab(self)
        self.ui.verticalLayoutSettings.addWidget(self.settings_tab)

        # Проверяем наличие ExifTool
        self.settings_tab.check_exiftool()

    def connect_signals(self):
        """Подключение сигналов"""
        self.ui.btnSelectFolder.clicked.connect(self.select_folder)
        self.ui.btnLoadGPX.clicked.connect(self.load_gpx)
        self.ui.btnStart.clicked.connect(self.run_geotagging)
        self.ui.btnClearLogs.clicked.connect(self.clear_logs)

        # Подключаем сигнал изменения темы
        self.settings_tab.theme_changed.connect(self.apply_theme)

    def apply_theme(self, theme):
        """Применяет выбранную тему"""
        self.current_theme = theme

        # Загружаем файл стилей
        style_file = f":/style/style_{theme}.qss"
        file = QFile(style_file)
        if file.open(QFile.ReadOnly | QFile.Text):
            style_content = QTextStream(file).readAll()
            # Применяем стиль ко всему приложению
            QApplication.instance().setStyleSheet(style_content)
            file.close()

    def refresh_logs(self):
        """Обновляет отображение логов"""
        html = self.logger.get_text_log()
        self.ui.textEditLogs.setHtml(html)
        scrollbar = self.ui.textEditLogs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        """Очищает логи"""
        self.logger.clear()
        self.refresh_logs()
        self.logger.info("Логи очищены")
        self.refresh_logs()

    def select_folder(self):
        """Выбор папки с изображениями"""
        folder = QFileDialog.getExistingDirectory(
            self, "Выбрать папку с изображениями")
        if folder:
            self.image_folder = folder
            self.load_image_data(folder)
            self.logger.info(f"Выбрана папка: {folder}")
            self.refresh_logs()

    def load_image_data(self, folder):
        """Загрузка информации из изображений в таблицу"""
        self.ui.tableFiles.setRowCount(0)

        try:
            images = file_manager.get_image_files(folder)

            for row, image_info in enumerate(images):
                self.ui.tableFiles.insertRow(row)
                self.ui.tableFiles.setItem(
                    row, 0, file_manager.make_table_item(image_info.filename))
                self.ui.tableFiles.setItem(
                    row, 1, file_manager.make_table_item(image_info.datetime_original))
                self.ui.tableFiles.setItem(
                    row, 2, file_manager.make_table_item(image_info.gps_string or "-"))

            self.logger.success(f"Загружено {len(images)} изображений")
            self.refresh_logs()
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке изображений: {e}")
            self.refresh_logs()
            show_error(self, "Ошибка",
                       f"Не удалось загрузить изображения: {e}")

    def load_gpx(self):
        """Загрузка GPX-файла"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать GPX-файл", filter="GPX файлы (*.gpx)")
        if path:
            self.gpx_file_path = path
            try:
                metadata = parse_gpx_metadata(path)

                self.ui.lblStartUTC.setText(
                    f"Начало трека (UTC): {metadata['start']}")
                self.ui.lblEndUTC.setText(
                    f"Конец трека (UTC): {metadata['end']}")
                self.ui.lblStartLocal.setText(
                    f"Местное время старта: {metadata['start_local']}")

                self.logger.success(f"Загружен GPX: {os.path.basename(path)}")
                self.refresh_logs()
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке GPX: {e}")
                self.refresh_logs()
                show_error(self, "Ошибка GPX",
                           f"Не удалось загрузить GPX: {e}")

    def run_geotagging(self):
        """Запуск обработки геометок"""
        if not self.image_folder or not self.gpx_file_path:
            self.logger.warning("Не выбрана папка или GPX-файл")
            self.refresh_logs()
            show_warning(self, "Недостаточно данных",
                         "Выберите папку и GPX-файл перед запуском")
            return

        correction = self.ui.editTimeCorrection.text().strip() or "0:00"

        self.logger.info(f"Запуск обработки с поправкой времени: {correction}")
        self.refresh_logs()

        try:
            count, total = process_images(
                folder_path=self.image_folder,
                gpx_path=self.gpx_file_path,
                time_correction=correction
            )

            self.logger.success(
                f"Геометки успешно записаны в {count} из {total} файлов")
            self.refresh_logs()
            show_info(self, "Готово",
                      f"Геометки успешно записаны в {count} из {total} файлов")

            # Обновляем таблицу
            self.load_image_data(self.image_folder)

        except Exception as e:
            self.logger.error(f"Ошибка при обработке: {e}")
            self.refresh_logs()
            show_error(self, "Ошибка", f"Произошла ошибка при обработке:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
