from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QComboBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QFile, QTextStream
from PySide6.QtGui import QIcon
import os
import subprocess


class SettingsTab(QWidget):
    """Вкладка настроек приложения"""

    theme_changed = Signal(str)  # Сигнал для изменения темы
    test_data_requested = Signal()  # Сигнал для создания тестовых данных

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Добавляем идентификатор для стилей
        self.setObjectName("settingsTab")

        # Группа настроек интерфейса
        self.ui_group = QGroupBox("Настройки интерфейса")
        ui_layout = QVBoxLayout(self.ui_group)

        # Настройки темы
        theme_layout = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Темная", "Светлая"])
        self.theme_combo.setMaximumWidth(200)
        theme_layout.addRow("Тема:", self.theme_combo)
        ui_layout.addLayout(theme_layout)

        layout.addWidget(self.ui_group)

        # Группа настроек приложения
        self.app_group = QGroupBox("Настройки приложения")
        app_layout = QVBoxLayout(self.app_group)

        # Информация о приложении
        info_layout = QFormLayout()
        self.version_label = QLabel("1.0.0")
        info_layout.addRow("Версия:", self.version_label)

        self.exiftool_label = QLabel("Не найден")
        info_layout.addRow("ExifTool:", self.exiftool_label)

        app_layout.addLayout(info_layout)

        # Кнопка создания тестовых данных
        test_layout = QHBoxLayout()
        self.create_test_data_button = QPushButton("Создать тестовые данные")
        self.create_test_data_button.setIcon(QIcon(":/icons/folder.png"))
        test_layout.addWidget(self.create_test_data_button)
        test_layout.addStretch()
        app_layout.addLayout(test_layout)

        layout.addWidget(self.app_group)

        # Растягиваем пространство
        layout.addStretch()

    def _connect_signals(self):
        # Тема меняется сразу при выборе
        self.theme_combo.currentTextChanged.connect(self._change_theme)

        # Кнопка создания тестовых данных
        self.create_test_data_button.clicked.connect(self._create_test_data)

    def _change_theme(self, theme_name):
        """Обрабатывает изменение темы"""
        theme = "dark" if theme_name == "Темная" else "light"

        # Загружаем файл стилей
        style_file = f":/style/style_{theme}.qss"
        file = QFile(style_file)
        if file.open(QFile.ReadOnly | QFile.Text):
            style_content = QTextStream(file).readAll()
            # Применяем стиль ко всему приложению
            QApplication.instance().setStyleSheet(style_content)
            file.close()

        # Отправляем сигнал об изменении темы
        self.theme_changed.emit(theme)

    def _create_test_data(self):
        """Создает тестовые данные"""
        # Отправляем сигнал для создания тестовых данных
        self.test_data_requested.emit()

    def update_exiftool_status(self, exiftool_path):
        """Обновляет статус ExifTool"""
        try:
            if exiftool_path:
                result = subprocess.run([exiftool_path, "-ver"],
                                        capture_output=True, text=True, check=True,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
                version = result.stdout.strip()
                self.exiftool_label.setText(f"Найден (v{version})")
                self.exiftool_label.setStyleSheet("color: green;")
                return exiftool_path
        except Exception:
            pass

        self.exiftool_label.setText("Не найден")
        self.exiftool_label.setStyleSheet("color: red;")
        return None
