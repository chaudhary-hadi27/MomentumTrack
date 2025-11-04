from kivy.uix.carousel import Carousel
from kivy.metrics import dp


class ListSwiper(Carousel):
    def __init__(self, on_list_change=None, **kwargs):
        super().__init__(**kwargs)
        self.direction = 'right'
        self.loop = False  # Changed to False for better UX
        self.on_list_change = on_list_change
        self.anim_type = 'out_cubic'  # Smooth animation
        self.anim_move_duration = 0.3  # Faster swipe
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