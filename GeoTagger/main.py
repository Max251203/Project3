import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QHeaderView, QTableWidgetItem,
    QLabel
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFile, QTextStream, QThreadPool

# UI
from ui.main_window import Ui_MainWindow
import ui.resources_rc
from ui.settings_tab import SettingsTab

# Логика
from logic import file_manager
from logic.gpx_parser import parse_gpx_metadata, analyze_gpx_file
from logic.exif_handler import process_images, find_exiftool
from logic.dialog_utils import show_warning, show_info, show_error
from logic.logger import get_logger
from logic.workers import GeoTagWorker
from logic.test_utils import create_test_dataset


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
        self.thread_pool = QThreadPool()

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
        exiftool_path = find_exiftool()
        if exiftool_path:
            self.logger.info(f"ExifTool найден: {exiftool_path}")
            self.settings_tab.update_exiftool_status(exiftool_path)
        else:
            self.logger.warning(
                "ExifTool не найден. Обработка RAW-файлов будет недоступна.")

        # Настройка прогресс-бара и статуса
        self.ui.progressBar.setVisible(False)
        self.ui.statusLabel.setText("")

        # Стилизация меток информации о треке
        self.ui.lblStartUTCLabel.setProperty("labelType", "title")
        self.ui.lblEndUTCLabel.setProperty("labelType", "title")
        self.ui.lblStartLocalLabel.setProperty("labelType", "title")

    def connect_signals(self):
        """Подключение сигналов"""
        self.ui.btnSelectFolder.clicked.connect(self.select_folder)
        self.ui.btnLoadGPX.clicked.connect(self.load_gpx)
        self.ui.btnStart.clicked.connect(self.run_geotagging)
        self.ui.btnClearLogs.clicked.connect(self.clear_logs)

        # Подключаем сигнал изменения темы
        self.settings_tab.theme_changed.connect(self.apply_theme)

        # Подключаем сигнал создания тестовых данных
        self.settings_tab.test_data_requested.connect(self.create_test_data)

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
            # Показываем прогресс
            self.ui.progressBar.setVisible(True)
            self.ui.progressBar.setValue(0)
            self.ui.statusLabel.setText("Загрузка изображений...")

            # Блокируем кнопки
            self.set_buttons_enabled(False)

            # Создаем рабочий поток
            worker = GeoTagWorker(
                lambda folder_path, **kwargs: file_manager.get_image_files(
                    folder_path),
                folder, None, None
            )

            # Подключаем сигналы
            worker.signals.finished.connect(
                lambda: self.on_worker_finished("Загрузка завершена"))
            worker.signals.result.connect(self.on_images_loaded)
            worker.signals.error.connect(self.on_worker_error)
            worker.signals.progress.connect(self.on_progress_update)

            # Запускаем поток
            self.thread_pool.start(worker)

        except Exception as e:
            self.ui.progressBar.setVisible(False)
            self.set_buttons_enabled(True)
            self.logger.error(f"Ошибка при загрузке изображений: {e}")
            self.refresh_logs()
            show_error(self, "Ошибка",
                       f"Не удалось загрузить изображения: {e}")

    def on_images_loaded(self, images):
        """Обработка загруженных изображений"""
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

    def load_gpx(self):
        """Загрузка GPX-файла"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать GPX-файл", filter="GPX файлы (*.gpx)")
        if path:
            self.gpx_file_path = path
            try:
                # Показываем прогресс
                self.ui.progressBar.setVisible(True)
                self.ui.progressBar.setValue(
                    50)  # Устанавливаем прогресс на 50%
                self.ui.statusLabel.setText("Загрузка GPX...")

                # Блокируем кнопки
                self.set_buttons_enabled(False)

                # Загружаем GPX напрямую (без потока)
                metadata = parse_gpx_metadata(path)

                self.ui.lblStartUTC.setText(metadata['start'])
                self.ui.lblEndUTC.setText(metadata['end'])
                self.ui.lblStartLocal.setText(metadata['start_local'])

                self.logger.success(f"Загружен GPX: {os.path.basename(path)}")

                # Анализируем GPX-файл для логов
                self.analyze_gpx(path)

                # Обновляем логи
                self.refresh_logs()

                # Разблокируем кнопки и скрываем прогресс
                self.set_buttons_enabled(True)
                self.ui.progressBar.setVisible(False)
                self.ui.statusLabel.setText("GPX загружен")

            except Exception as e:
                self.ui.progressBar.setVisible(False)
                self.set_buttons_enabled(True)
                self.logger.error(f"Ошибка при загрузке GPX: {e}")
                self.refresh_logs()
                show_error(self, "Ошибка GPX",
                           f"Не удалось загрузить GPX: {e}")

    def analyze_gpx(self, path):
        """Анализирует GPX-файл и выводит информацию в логи"""
        try:
            worker = GeoTagWorker(
                lambda gpx_path, **kwargs: analyze_gpx_file(gpx_path),
                None, path, None
            )

            worker.signals.result.connect(self.on_gpx_analyzed)
            worker.signals.error.connect(lambda error: self.logger.warning(
                f"Не удалось проанализировать GPX: {error[1]}"))

            self.thread_pool.start(worker)
        except Exception as e:
            self.logger.warning(f"Не удалось проанализировать GPX: {e}")

    def on_gpx_analyzed(self, info):
        """Обработка результатов анализа GPX"""
        if info:
            self.logger.info(
                f"Анализ GPX: {info.get('point_count', 0)} точек, {info.get('points_with_time', 0)} с временем")
            if 'time_range' in info:
                self.logger.info(
                    f"Продолжительность трека: {info['time_range']}")
            if 'geo_range' in info:
                self.logger.info(f"Географический охват: {info['geo_range']}")

    def on_gpx_loaded(self, metadata):
        """Обработка загруженного GPX"""
        self.ui.lblStartUTC.setText(metadata['start'])
        self.ui.lblEndUTC.setText(metadata['end'])
        self.ui.lblStartLocal.setText(metadata['start_local'])

        self.logger.success(
            f"Загружен GPX: {os.path.basename(self.gpx_file_path)}")
        self.refresh_logs()

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
            # Показываем прогресс
            self.ui.progressBar.setVisible(True)
            self.ui.progressBar.setValue(0)
            self.ui.statusLabel.setText("Обработка геометок...")

            # Блокируем кнопки
            self.set_buttons_enabled(False)

            # Создаем рабочий поток
            worker = GeoTagWorker(
                process_images,
                self.image_folder,
                self.gpx_file_path,
                correction
            )

            # Подключаем сигналы
            worker.signals.finished.connect(
                lambda: self.on_worker_finished("Обработка завершена"))
            worker.signals.result.connect(self.on_geotagging_completed)
            worker.signals.error.connect(self.on_worker_error)
            worker.signals.progress.connect(self.on_progress_update)

            # Запускаем поток
            self.thread_pool.start(worker)

        except Exception as e:
            self.ui.progressBar.setVisible(False)
            self.set_buttons_enabled(True)
            self.logger.error(f"Ошибка при обработке: {e}")
            self.refresh_logs()
            show_error(self, "Ошибка", f"Произошла ошибка при обработке:\n{e}")

    def on_geotagging_completed(self, result):
        """Обработка результатов геотеггинга"""
        count, total = result
        self.logger.success(
            f"Геометки успешно записаны в {count} из {total} файлов")
        self.refresh_logs()
        show_info(self, "Готово",
                  f"Геометки успешно записаны в {count} из {total} файлов")

        # Обновляем таблицу
        self.load_image_data(self.image_folder)

    def set_buttons_enabled(self, enabled):
        """Включает/выключает кнопки"""
        self.ui.btnSelectFolder.setEnabled(enabled)
        self.ui.btnLoadGPX.setEnabled(enabled)
        self.ui.btnStart.setEnabled(enabled)

    def on_worker_finished(self, message=""):
        """Обработка завершения работы потока"""
        # Разблокируем кнопки
        self.set_buttons_enabled(True)

        # Скрываем прогресс
        self.ui.progressBar.setVisible(False)
        self.ui.statusLabel.setText(message)

    def on_worker_error(self, error_info):
        """Обработка ошибки в потоке"""
        exctype, value, traceback = error_info
        self.logger.error(f"Ошибка: {value}")
        self.refresh_logs()
        show_error(self, "Ошибка", str(value))

        # Разблокируем кнопки
        self.set_buttons_enabled(True)

        # Скрываем прогресс
        self.ui.progressBar.setVisible(False)
        self.ui.statusLabel.setText("Ошибка")

    def on_progress_update(self, value):
        """Обновление прогресса"""
        self.ui.progressBar.setValue(value)

    def create_test_data(self):
        """Создает тестовые данные для проверки приложения"""
        try:
            folder = QFileDialog.getExistingDirectory(
                self, "Выберите папку для тестовых данных")
            if not folder:
                return

            self.logger.info(f"Создание тестовых данных в папке: {folder}")

            # Показываем прогресс
            self.ui.progressBar.setVisible(True)
            self.ui.progressBar.setValue(10)
            self.ui.statusLabel.setText("Создание тестовых данных...")

            # Блокируем кнопки
            self.set_buttons_enabled(False)

            # Импортируем функцию создания тестовых данных
            from logic.test_utils import create_test_dataset

            # Создаем тестовые данные напрямую (без потока)
            self.ui.progressBar.setValue(30)
            result = create_test_dataset(folder)
            self.ui.progressBar.setValue(80)

            if result:
                self.logger.success(
                    f"Создано {len(result['gpx_paths'])} GPX-файлов")
                self.logger.success(
                    f"Создано {len(result['image_paths'])} тестовых изображений")

                # Автоматически загружаем тестовые данные
                self.gpx_file_path = result['main_gpx_path']
                self.image_folder = os.path.dirname(result['main_gpx_path'])

                # Загружаем GPX
                metadata = parse_gpx_metadata(self.gpx_file_path)
                self.ui.lblStartUTC.setText(metadata['start'])
                self.ui.lblEndUTC.setText(metadata['end'])
                self.ui.lblStartLocal.setText(metadata['start_local'])

                # Загружаем изображения
                self.load_image_data(self.image_folder)

                show_info(self, "Готово",
                          "Тестовые данные созданы и загружены")
            else:
                self.logger.error("Не удалось создать тестовые данные")
                show_error(self, "Ошибка",
                           "Не удалось создать тестовые данные")

            # Обновляем логи
            self.refresh_logs()

            # Разблокируем кнопки и скрываем прогресс
            self.set_buttons_enabled(True)
            self.ui.progressBar.setVisible(False)
            self.ui.statusLabel.setText("Тестовые данные созданы")

        except Exception as e:
            self.ui.progressBar.setVisible(False)
            self.set_buttons_enabled(True)
            self.logger.error(f"Ошибка при создании тестовых данных: {e}")
            self.refresh_logs()
            show_error(self, "Ошибка",
                       f"Не удалось создать тестовые данные:\n{e}")

    def on_test_data_created(self, result):
        """Обработка результатов создания тестовых данных"""
        if result:
            self.logger.success(
                f"Создано {len(result['gpx_paths'])} GPX-файлов")
            self.logger.success(
                f"Создано {len(result['image_paths'])} тестовых изображений")

            # Автоматически загружаем тестовые данные
            self.gpx_file_path = result['main_gpx_path']
            self.image_folder = os.path.dirname(result['main_gpx_path'])

            # Загружаем GPX
            self.load_gpx()

            # Загружаем изображения
            self.load_image_data(self.image_folder)

            show_info(self, "Готово", "Тестовые данные созданы и загружены")
        else:
            self.logger.error("Не удалось создать тестовые данные")
            show_error(self, "Ошибка", "Не удалось создать тестовые данные")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
