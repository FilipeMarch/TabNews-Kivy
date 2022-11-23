from shutil import copytree, ignore_patterns, rmtree
from kivy.utils import platform
import subprocess
import os


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
