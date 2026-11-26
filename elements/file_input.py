from pathlib import Path

from elements.base_element import BaseElement


class FileInput(BaseElement):
    def set_input_files(self, file: str | Path) -> None:
        """Выбирает локальный файл через файловое поле браузера."""
        with self.step("Select file"):
            self.get_locator().set_input_files(file)
