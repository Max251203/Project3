from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QComboBox, QFileDialog, QMessageBox, QApplication
)
from PySide6.QtCore import QFile, QTextStream, Signal
from PySide6.QtGui import QIcon
import subprocess
import os

from logic.config import set_exiftool_path
from logic.logger import get_logger

logger = get_logger()


class SettingsTab(QWidget):
    theme_changed = Signal(str)
    test_data_requested = Signal()
    exiftool_status_changed = Signal(bool)  # True если ExifTool готов

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("settingsTab")

        self.ui_group = QGroupBox("Настройки интерфейса")
        ui_layout = QVBoxLayout(self.ui_group)
        theme_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная", "Светлая"])
        self.theme_combo.setMaximumWidth(200)
        theme_layout.addRow("Тема:", self.theme_combo)
        ui_layout.addLayout(theme_layout)

        layout.addWidget(self.ui_group)

        self.app_group = QGroupBox("ExifTool")
        app_layout = QVBoxLayout(self.app_group)

        info_layout = QFormLayout()
        self.version_label = QLabel("1.0.0")
        info_layout.addRow("Версия:", self.version_label)

        self.exiftool_label = QLabel("Не найден")
        self.exiftool_label.setStyleSheet("color: red;")
        info_layout.addRow("Статус:", self.exiftool_label)

        app_layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        self.create_test_data_button = QPushButton("Создать тестовые данные")
        self.create_test_data_button.setIcon(QIcon(":/icons/folder.png"))

        self.select_exiftool_button = QPushButton("Выбрать exiftool вручную")
        self.select_exiftool_button.setIcon(QIcon(":/icons/folder.png"))

        button_layout.addWidget(self.create_test_data_button)
        button_layout.addWidget(self.select_exiftool_button)
        button_layout.addStretch()

        app_layout.addLayout(button_layout)
        layout.addWidget(self.app_group)
        layout.addStretch()

    def _connect_signals(self):
        self.theme_combo.currentTextChanged.connect(self._change_theme)
        self.create_test_data_button.clicked.connect(self._create_test_data)
        self.select_exiftool_button.clicked.connect(self.select_exiftool)

    def _change_theme(self, theme_name):
        theme = "dark" if theme_name == "Темная" else "light"
        style_file = f":/style/style_{theme}.qss"
        file = QFile(style_file)
        if file.open(QFile.ReadOnly | QFile.Text):
            style_content = QTextStream(file).readAll()
            QApplication.instance().setStyleSheet(style_content)
            file.close()
        self.theme_changed.emit(theme)

    def _create_test_data(self):
        self.test_data_requested.emit()

    def update_exiftool_status(self, path):
        """
        Обновляет label в настройках.
        Возвращает True если всё хорошо, иначе False
        """
        from logic.config import set_exiftool_path
        try:
            if path:
                folder = os.path.dirname(path)
                files_dir = os.path.join(folder, "exiftool_files")
                if not os.path.isdir(files_dir):
                    self.exiftool_label.setText("❌ Нет папки exiftool_files")
                    self.exiftool_label.setStyleSheet("color: red;")
                    logger.error(
                        "Папка exiftool_files не найдена рядом с exiftool.")
                    self.exiftool_status_changed.emit(False)
                    return False

                result = subprocess.run([path, "-ver"],
                                        capture_output=True, text=True)
                version = result.stdout.strip()
                set_exiftool_path(path)
                self.exiftool_label.setText(f"Найден (v{version})")
                self.exiftool_label.setStyleSheet("color: green;")
                logger.info(f"Запуск exiftool успешен: {version}")
                self.exiftool_status_changed.emit(True)
                return True
        except Exception as e:
            self.exiftool_label.setText(f"❌ Ошибка запуска ExifTool")
            self.exiftool_label.setStyleSheet("color: red;")
            logger.error(f"Ошибка запуска exiftool: {e}")
            self.exiftool_status_changed.emit(False)
        self.exiftool_label.setText("❌ Не найден")
        self.exiftool_label.setStyleSheet("color: red;")
        self.exiftool_status_changed.emit(False)
        return False

    def select_exiftool(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите exiftool.exe", filter="ExifTool (exiftool*.exe)"
        )
        if path and os.path.isfile(path):
            ok = self.update_exiftool_status(path)
            if not ok:
                QMessageBox.critical(
                    self,
                    "ExifTool не работает",
                    "ExifTool не запущен или рядом с ним нет папки exiftool_files/.\n"
                    "Обработка RAW (ARW) файлов будет недоступна.",
                )
        else:
            QMessageBox.warning(
                self,
                "Путь не выбран",
                "Вы не выбрали файл exiftool.exe.",
            )
