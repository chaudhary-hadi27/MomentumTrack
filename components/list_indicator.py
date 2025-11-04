from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics import Color, Ellipse
from kivy.metrics import dp


class ListIndicator(MDBoxLayout):
    """Shows dots to indicate which list you're on"""

    def __init__(self, total_lists=1, current_index=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.height = dp(20)
        self.spacing = dp(8)
        self.total_lists = total_lists
        self.current_index = current_index
        self.pos_hint = {'center_x': 0.5}

        self.update_indicators()

    def update_indicators(self):
        """Draw indicator dots"""
        self.clear_widgets()
        self.width = (dp(12) + dp(8)) * self.total_lists

        for i in range(self.total_lists):
            indicator = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(12), dp(12))
            )

            with indicator.canvas:
                if i == self.current_index:
                    Color(0.1, 0.45, 0.91, 1)  # Blue for current
                else:
                    Color(0.5, 0.5, 0.5, 0.3)  # Gray for others

                Ellipse(
                    pos=indicator.pos,
                    size=(dp(8), dp(8))
                )

            self.add_widget(indicator)