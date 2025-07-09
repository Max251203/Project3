from PySide6.QtWidgets import QMessageBox


def show_warning(parent, title: str, message: str):
    QMessageBox.warning(parent, title, message)


def show_error(parent, title: str, message: str):
    QMessageBox.critical(parent, title, message)


def show_info(parent, title: str, message: str):
    QMessageBox.information(parent, title, message)


def confirm_overwrite_gps(filename: str) -> str:
    dlg = QMessageBox()
    dlg.setWindowTitle("EXIF GPS уже существует")
    dlg.setText(f"Файл '{filename}' уже содержит координаты. Что сделать?")
    dlg.setIcon(QMessageBox.Question)

    overwrite = dlg.addButton("Перезаписать", QMessageBox.AcceptRole)
    skip = dlg.addButton("Пропустить", QMessageBox.RejectRole)
    overwrite_all = dlg.addButton("Перезаписать все", QMessageBox.YesRole)
    skip_all = dlg.addButton("Пропустить все", QMessageBox.NoRole)
    cancel = dlg.addButton("Стоп", QMessageBox.DestructiveRole)

    dlg.exec()
    if dlg.clickedButton() == overwrite:
        return "overwrite"
    elif dlg.clickedButton() == skip:
        return "skip"
    elif dlg.clickedButton() == overwrite_all:
        return "overwrite_all"
    elif dlg.clickedButton() == skip_all:
        return "skip_all"
    return "cancel"
