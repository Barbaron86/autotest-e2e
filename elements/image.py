from playwright.sync_api import expect

from elements.base_element import BaseElement


class Image(BaseElement):
    def check_loaded(self) -> None:
        """Ожидает видимое изображение с завершённой загрузкой и ненулевой шириной.

        Raises:
            AssertionError: Загрузка завершилась, но изображение не декодировано.
        """
        with self.step("Check image loaded"):
            image = self.get_locator()
            expect(image).to_be_visible()
            expect(image).to_have_js_property("complete", True)
            if not image.evaluate("image => image.naturalWidth > 0"):
                raise AssertionError(f"Image {self.test_id!r} did not load")
