from shutil import copytree, ignore_patterns, rmtree
from kivy.utils import platform
from kivy.lang import Builder
from kivy.factory import Factory as F
import subprocess
import os


kv = Builder.load_string(
    """
<RootScreen>:
    screen_manager: screen_manager.__self__
    server_layout: server_layout.__self__
    server_icon: server_icon.__self__
    ScreenManager:
        id: screen_manager

    FloatLayout:
        id: server_layout
        opacity: 0
        Label:
            text: root.port_selected
            font_size: sp(18)
            pos: server_icon.right+dp(10),0
            color: 1,1,1,1
            size_hint: 1, None
            height: self.texture_size[1]
        
        Label:
            text: root.ip_selected
            font_size: sp(18)
            pos: server_icon.right+dp(10),server_icon.top
            color: 1,1,1,1
            size_hint: 1, None
            height: self.texture_size[1]
        
        Button:
            id: server_icon
            size_hint: None, None
            size: dp(50), dp(50)
            on_release: root.change_opacity(server_layout)
        Widget:
            
"""
)


class RootScreen(F.Screen):
    port_selected = F.StringProperty("Selected port: 8035")
    ip_selected = F.StringProperty("IP:")

    def __init__(self) -> None:
        super().__init__()
        self.app = App.get_running_app()
        self.initialize_server()

    def initialize_server(self) -> None:
        if platform == "android":
            self.app.nursery.start_soon(self.start_async_server)
            self.server_layout.opacity = 0
        else:
            self.update_last_port_used()
            PORT = int(self.get_last_port_used()) + 1
            self.port_selected = f"Livestream ON\nSelected port: {PORT}"
            self.server_layout.opacity = 0

    def get_last_port_used(self) -> int:
        last_port_used = open("configs/last_port_used", "r").read()
        return last_port_used

    def update_last_port_used(self) -> None:
        last_port_used = self.get_last_port_used()
        with open("configs/last_port_used", "w") as f:
            f.write(str(int(last_port_used) + 1))

    async def start_async_server(self):
        try:
            import socket

            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))

            self.ip_selected = f"IP: {s.getsockname()[0]}"
            PORT = int(self.get_last_port_used()) + 1
            self.update_last_port_used()
            self.port_selected = f"Livestream ON\nSelected port: {PORT}"
            self.server_icon.text_color = 0, 0.7, 0, 1
            await trio.serve_tcp(self.data_receiver, PORT)
        except Exception as e:
            print("Error starting server: ", e)

    def change_opacity(self, layout):
        if layout.opacity:
            layout.opacity = 0
        else:
            layout.opacity = 1

    async def data_receiver(self, data_stream):
        print("Downloading updated app")
        import shutil

        try:
            with open("app_copy.zip", "wb") as myzip:
                async for data in data_stream:
                    print(f"Server: received data")
                    print(f"Data type: {type(data)}, size {len(data)}")
                    print(f"Server: connection closed")
                    myzip.write(data)

            print("Unpacking app")
            shutil.unpack_archive("app_copy.zip")
            print("Updating last port used")
            self.update_last_port_used()

            print("App updated, restarting app")
            self.app.restart()
        except Exception as e:
            print(f"Server crashed: {e!r}")


if platform != "android":
    from kaki.app import App

    class BaseApp(App):

        DEBUG = 1

        should_send_app_to_phone = True

        AUTORELOADER_PATHS = [
            (os.path.join(os.getcwd(), "main.py"), {"recursive": True}),
            (os.path.join(os.getcwd(), "screens"), {"recursive": True}),
        ]

        KV_FILES = {
            os.path.join(os.getcwd(), f"screens/{screen_name}")
            for screen_name in os.listdir("screens")
            if screen_name.endswith(".kv")
        }

        CLASSES = {
            f"{''.join([i.capitalize() for i in screen_name.split('_')])}": f"screens.{screen_name[:-3]}"
            for screen_name in os.listdir("screens")
            if screen_name.endswith(".py")
        }

        def build_app(self):
            return self.build_and_reload()

        def build_and_reload(self):
            pass

        def rebuild(self, *args, **kwargs):
            super().rebuild(*args, **kwargs)

            if self.should_send_app_to_phone:
                self.send_app_to_phone()

        def send_app_to_phone(self):
            # Creating a copy of the files on `temp` folder
            source = os.getcwd()
            destination = os.path.join(os.getcwd(), "temp")
            if os.path.exists(destination):
                rmtree(destination)

            copytree(
                source,
                destination,
                ignore=ignore_patterns(
                    "*.pyc",
                    "tmp*",
                    "__pycache__",
                    ".buildozer",
                    ".venv",
                    ".vscode",
                    "bin",
                    "compile_app.py",
                    "buildozer.spec",
                    "poetry.lock",
                    "pyproject.toml",
                    "app_copy.zip",
                    "camera4kivy",
                    "camerax_provider",
                    ".DS_Store",
                    "images",
                ),
            )

            # Zipping all files inside `temp` folder, except the `temp` folder itself
            # os.system(f"cd {destination} && zip -r ../app_copy.zip ./* -x ./temp")

            # Make the same zip command but using subprocess
            subprocess.run(
                f"cd {destination} && zip -r ../app_copy.zip ./* -x ./temp",
                shell=True,
                stdout=subprocess.DEVNULL,
            )

            # Sending the zip file to the phone
            os.system("python send_app_to_phone.py")

        def _filename_to_module(self, filename):
            rootpath = self.get_root_path()
            if filename.startswith(rootpath):
                filename = filename[len(rootpath) :]

            if platform == "macosx":
                prefix = os.sep
            else:
                prefix = os.path.sep

            if filename.startswith(prefix):
                filename = filename[1:]
            module = filename[:-3].replace(prefix, ".")
            return module

else:
    from kivy.app import App

    class BaseApp(App):
        def build(self):
            return self.build_and_reload()