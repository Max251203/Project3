from datetime import datetime


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_internal()
        return cls._instance

    def _init_internal(self):
        self.text_log = []

    def info(self, message: str): self._add("info", message)
    def warning(self, message: str): self._add("warning", message)
    def error(self, message: str): self._add("error", message)
    def success(self, message: str): self._add("success", message)

    def _add(self, icon: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon_html = f'<img src=":/icons/{icon}.png" width="16" height="16" style="vertical-align:middle;">'
        self.text_log.append(f"[{timestamp}] {icon_html} {message}<br/>")

    def get_text_log(self) -> str:
        return "".join(self.text_log)

    def clear(self):
        self.text_log = []


def get_logger() -> Logger:
    return Logger()
