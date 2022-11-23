from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
import os
from icecream import ic

kv_path = os.path.join(os.getcwd(), "screens", "main_screen.kv")
if kv_path not in Builder.files:
    Builder.load_file(kv_path)


class MainScreen(F.Screen):
    app = App.get_running_app()

    def on_enter(self):
        print("Entered main screen")
