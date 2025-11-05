from kivy.uix.carousel import Carousel
from kivy.metrics import dp


class ListSwiper(Carousel):
    def __init__(self, on_list_change=None, **kwargs):
        super().__init__(**kwargs)
        self.direction = 'right'
        self.loop = False
        self.on_list_change = on_list_change
        self.anim_type = 'out_cubic'
        self.anim_move_duration = 0.3
        self.bind(index=self._on_index_change)

    def _on_index_change(self, instance, value):
        """Handle index change with validation"""
        if self.on_list_change and value is not None:
            # Ensure index is within valid range
            if 0 <= value < len(self.slides):
                self.on_list_change(value)
            else:
                print(f"Warning: Invalid carousel index {value}, total slides: {len(self.slides)}")

    def add_list_slide(self, list_widget):
        """Add a list as a slide"""
        self.add_widget(list_widget)

    def remove_list_slide(self, index):
        """Remove a list slide"""
        if 0 <= index < len(self.slides):
            self.remove_widget(self.slides[index])
        else:
            print(f"Warning: Cannot remove slide at index {index}")

    def clear_slides(self):
        """Clear all slides safely"""
        # Unbind to prevent callback during clearing
        self.unbind(index=self._on_index_change)
        self.clear_widgets()
        # Re-bind after clearing
        self.bind(index=self._on_index_change)

    def safe_set_index(self, index):
        """Safely set carousel index"""
        if 0 <= index < len(self.slides):
            self.index = index
        elif len(self.slides) > 0:
            self.index = 0
        else:
            print("Warning: Cannot set index, no slides available")