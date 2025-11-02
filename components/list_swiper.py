from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.metrics import dp


class ListSwiper(Carousel):
    def __init__(self, on_list_change=None, **kwargs):
        super().__init__(**kwargs)
        self.direction = 'right'
        self.loop = True
        self.on_list_change = on_list_change
        self.bind(index=self._on_index_change)

    def _on_index_change(self, instance, value):
        if self.on_list_change:
            self.on_list_change(value)

    def add_list_slide(self, list_widget):
        """Add a list as a slide"""
        self.add_widget(list_widget)

    def remove_list_slide(self, index):
        """Remove a list slide"""
        if len(self.slides) > index:
            self.remove_widget(self.slides[index])