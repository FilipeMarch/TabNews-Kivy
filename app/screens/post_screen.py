from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock
from icecream import ic
import asks
import os

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon
from kivymd.uix.behaviors import RectangularRippleBehavior


class RectangleIconButton(
    RectangularRippleBehavior, F.ButtonBehavior, MDBoxLayout, MDIcon
):
    pass


kv_path = os.path.join(os.getcwd(), "screens", "post_screen.kv")
if kv_path not in Builder.files:
    Builder.load_file(kv_path)


class PostScreen(F.Screen):
    app = App.get_running_app()
    screen_loaded = F.BooleanProperty(False)
    slug = F.StringProperty()
    author = F.StringProperty()
    date = F.StringProperty()
    tabcoins = F.NumericProperty()
    title = F.StringProperty()
    body = F.StringProperty()

    def on_enter(self):
        print("Entered Post Screen")
        if not self.author:
            self.author = "cleitonmedeiros"
            self.slug = "como-contribuir-para-o-tabnews"
            self.date = "11 horas atrás"
            self.tabcoins = 13
            self.title = "Como contribuir para o TabNews"
        self.app.nursery.start_soon(self.load_screen_data)

    async def load_screen_data(self):
        """
        Get the content from tabnews.com.br/slug and load it into the screen
        """
        url = "https://tabnews.com.br/"
        route = f"/api/v1/contents/{self.author}/{self.slug}"

        session = asks.Session()

        response = await session.get(url + route)

        ic(response.json())

        if response.status_code == 200:
            self.screen_loaded = True
            self.date = response.json()["created_at"][:10]
            self.tabcoins = response.json()["tabcoins"]
            self.title = response.json()["title"]
            self.body = response.json()["body"]
