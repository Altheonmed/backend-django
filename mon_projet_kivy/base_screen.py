# base_screen.py
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle

# Importez la couleur de fond depuis votre fichier pythoncolor.py
from pythoncolor import BACKGROUND_COLOR

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*BACKGROUND_COLOR)
            self.background_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        self.background_rect.pos = instance.pos
        self.background_rect.size = instance.size