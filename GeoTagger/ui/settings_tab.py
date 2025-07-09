from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QFormLayout, QComboBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QFile, QTextStream
from PySide6.QtGui import QIcon


class SettingsTab(QWidget):
    """Вкладка настроек приложения"""

    theme_changed = Signal(str)  # Сигнал для изменения темы

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

        layout.addWidget(self.app_group)

        # Растягиваем пространство
        layout.addStretch()

    def _connect_signals(self):
        # Тема меняется сразу при выборе
        self.theme_combo.currentTextChanged.connect(self._change_theme)

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

    def check_exiftool(self, exiftool_path=None):
        """Проверяет наличие ExifTool и обновляет статус"""
        import os
        import subprocess

        if exiftool_path and os.path.exists(exiftool_path):
            try:
                result = subprocess.run([exiftool_path, "-ver"],
                                        capture_output=True, text=True, check=True)
                version = result.stdout.strip()
                self.exiftool_label.setText(f"Найден (v{version})")
                self.exiftool_label.setStyleSheet("color: green;")
                return True
            except Exception:
                pass

        # Проверяем в текущей директории
        current_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        exiftool_path = os.path.join(current_dir, "exiftool.exe")

        if os.path.exists(exiftool_path):
            try:
                result = subprocess.run([exiftool_path, "-ver"],
                                        capture_output=True, text=True, check=True)
                version = result.stdout.strip()
                self.exiftool_label.setText(f"Найден (v{version})")
                self.exiftool_label.setStyleSheet("color: green;")
                return True
            except Exception:
                pass

        # Проверяем в PATH
        try:
            result = subprocess.run(["exiftool", "-ver"],
                                    capture_output=True, text=True, check=True)
            version = result.stdout.strip()
            self.exiftool_label.setText(f"Найден в PATH (v{version})")
            self.exiftool_label.setStyleSheet("color: green;")
            return True
        except Exception:
            self.exiftool_label.setText("Не найден")
            self.exiftool_label.setStyleSheet("color: red;")
            return False
