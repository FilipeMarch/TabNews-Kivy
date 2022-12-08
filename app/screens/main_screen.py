from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory as F
from kivy.utils import platform
from kivy.clock import Clock

# from icecream import ic
import asks
import os

kv_path = os.path.join(os.getcwd(), "screens", "main_screen.kv")
if kv_path not in Builder.files:
    Builder.load_file(kv_path)


class Post(F.BoxLayout):
    post_number = F.NumericProperty()
    post_title = F.StringProperty()
    post_tabcoins = F.NumericProperty()
    post_number_of_comments = F.NumericProperty()
    post_author = F.StringProperty()
    post_date = F.StringProperty()
    post_slug = F.StringProperty()

    def open_post(self):
        # ic("Opening post")
        self.title.text = f"[u][ref=[b]{self.post_title}"

        # Change to post screen and update the text again to remove [u]
        app = App.get_running_app()
        app.change_screen("Post Screen")
        post_screen = app.screen_manager.get_screen("Post Screen")
        post_screen.slug = self.post_slug
        post_screen.author = self.post_author


class MainScreen(F.Screen):
    app = App.get_running_app()
    screen_loaded = F.BooleanProperty(False)
    data = F.ListProperty()

    def on_enter(self):
        print("Entered main screen")

        self.load_main_screen_data()

    def load_main_screen_data(self):
        self.app.nursery.start_soon(self.request_posts)

    async def request_posts(self):
        """
        Get the content from tabnews.com.br and load it into the screen
        """
        url = "https://tabnews.com.br/"
        route = "api/v1/contents"

        session = asks.Session()

        response = await session.get(url + route)

        # ic(response.json()[0])

        if response.status_code == 200:
            self.screen_loaded = True
            self.data = []
            for index, item in enumerate(response.json(), start=1):
                self.data.append(
                    {
                        "post_number": index,
                        "post_title": item["title"],
                        "post_tabcoins": item["tabcoins"],
                        "post_number_of_comments": item["children_deep_count"],
                        "post_author": item["owner_username"],
                        "post_date": item["created_at"][:10],
                        "post_slug": item["slug"],
                    }
                )
