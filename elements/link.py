from re import Pattern

from playwright.sync_api import expect

from elements.base_element import BaseElement


class Link(BaseElement):
    def check_href(self, href: str | Pattern[str]) -> None:
        """Ожидает значение href по строке или регулярному выражению."""
        with self.step("Check link target"):
            expect(self.get_locator()).to_have_attribute("href", href)
