from kivy.lang import Builder
from kivy.utils import platform
from kivy.factory import Factory as F
from custom_reloader import RootScreen, BaseApp, App
from kivymd.app import MDApp
import trio
import os


if platform != "android":
    from kivy.core.window import Window

    Window.size = (375, 667)
    # Window.size = (1312 * 0.306777, 2460 * 0.306777)
    Window._set_window_pos(1040, 100)


class TabNewsApp(BaseApp, MDApp):
    should_send_app_to_phone = False

    def __init__(self, nursery):
        super().__init__()
        self.nursery = nursery

    def build_and_reload(self):
        self.root_screen = RootScreen()
        self.screen_manager = self.root_screen.screen_manager
        initial_screen = "Main Screen"
        self.change_screen(initial_screen)
        return self.root_screen

    def change_screen(self, screen_name):
        if screen_name not in self.screen_manager.screen_names:
            screen_object = self.get_screen_object_from_screen_name(screen_name)
            self.screen_manager.add_widget(screen_object)

        self.screen_manager.current = screen_name

    def get_screen_object_from_screen_name(self, screen_name):
        # Parsing module 'my_screen.py' and object 'MyScreen' from screen_name 'My Screen'
        screen_module_in_str = "_".join([i.lower() for i in screen_name.split()])
        screen_object_in_str = "".join(screen_name.split())

        # Importing screen object
        exec(f"from screens.{screen_module_in_str} import {screen_object_in_str}")

        # Instantiating the object
        screen_object = eval(f"{screen_object_in_str}()")

        return screen_object

    def restart(self):
        print("Restarting the app on smartphone")
        from jnius import autoclass

        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        System = autoclass("java.lang.System")

        activity = PythonActivity.mActivity
        intent = Intent(activity.getApplicationContext(), PythonActivity)
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
        activity.startActivity(intent)
        System.exit(0)


# Start kivy app as an asynchronous task
async def main() -> None:
    async with trio.open_nursery() as nursery:
        server = TabNewsApp(nursery)
        await server.async_run("trio")
        nursery.cancel_scope.cancel()


try:
    trio.run(main)

except Exception as e:
    print(e)
    raise
