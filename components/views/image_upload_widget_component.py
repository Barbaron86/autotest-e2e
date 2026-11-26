from pathlib import Path

import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from components.views.empty_view_component import EmptyViewComponent
from elements.button import Button
from elements.file_input import FileInput
from elements.icon import Icon
from elements.image import Image
from elements.text import Text


class ImageUploadWidgetComponent(BaseComponent):
    def __init__(self, root: Page | Locator, identifier: str) -> None:
        """Связывает предпросмотр и управление изображением по префиксу test ID.

        Args:
            root: Область поиска виджета загрузки.
            identifier: Префикс test ID виджета и сообщения о пустом предпросмотре.
        """
        super().__init__(root)
        prefix = f"{identifier}-image-upload-widget"
        self.preview_empty_view = EmptyViewComponent(root, identifier)
        self.preview_image = Image(root, f"{prefix}-preview-image")
        self.image_upload_info_icon = Icon(root, f"{prefix}-info-icon")
        self.image_upload_info_title = Text(root, f"{prefix}-info-title-text")
        self.image_upload_info_description = Text(root, f"{prefix}-info-description-text")
        self.upload_button = Button(root, f"{prefix}-upload-button")
        self.remove_button = Button(root, f"{prefix}-remove-button")
        self.upload_input = FileInput(root, f"{prefix}-input")
        self.error_alert = Text(root, f"{prefix}-error")

    @allure.step("Check visible image upload widget")
    def check_visible(self, is_image_uploaded: bool = False, is_removable: bool = True) -> None:
        """Сверяет подсказки, предпросмотр и доступность удаления изображения.

        Args:
            is_image_uploaded: Ожидается загруженный предпросмотр при True,
                сообщение о пустом выборе при False.
            is_removable: При загруженном изображении определяет ожидаемую
                видимость кнопки удаления.
        """
        self.image_upload_info_icon.check_visible()
        self.image_upload_info_title.check_have_text("Choose a PNG or JPEG image up to 10 MiB")
        self.image_upload_info_description.check_have_text("Recommended dimensions 540 × 300 px")
        self.upload_button.check_visible()
        if is_image_uploaded:
            self.preview_image.check_loaded()
        else:
            self.preview_empty_view.check_visible(
                title="No image selected", description="Preview of selected image will be displayed here"
            )
        if is_image_uploaded and is_removable:
            self.remove_button.check_visible()
        else:
            self.remove_button.check_hidden()

    def upload_preview_image(self, file: str | Path) -> None:
        """Выбирает локальный файл и ожидает его предпросмотр в форме.

        Args:
            file: Путь к изображению для выбора через файловое поле.
                Загрузка на сервер происходит при сохранении курса.
        """
        self.upload_input.set_input_files(file)
        self.preview_image.check_loaded()
        self.remove_button.check_visible()

    @allure.step("Remove preview image")
    def click_remove_image_button(self) -> None:
        """Нажимает удаление изображения из текущего предпросмотра."""
        self.remove_button.click()
