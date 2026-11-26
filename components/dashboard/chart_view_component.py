import allure
from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent
from elements.text import Text


class ChartViewComponent(BaseComponent):
    def __init__(self, root: Page | Locator, identifier: str, chart_type: str) -> None:
        """Связывает заголовок и диаграмму по составным test ID.

        Args:
            root: Область поиска элементов диаграммы.
            identifier: Префикс test ID заголовка и диаграммы.
            chart_type: Часть test ID, обозначающая тип диаграммы.
        """
        super().__init__(root)
        self.title = Text(root, f"{identifier}-widget-title-text")
        self.chart = Text(root, f"{identifier}-{chart_type}-chart")

    @allure.step("Check visible chart")
    def check_visible(self, title: str) -> None:
        """Ожидает видимую диаграмму и заданный текст её заголовка."""
        self.title.check_visible()
        self.title.check_have_text(title)
        self.chart.check_visible()
