from colorama import Fore, Style, init
from multiprocessing import Process
from plyer import notification
from threading import Thread
from icecream import ic
import psutil
import time
import os

red = Fore.RED
green = Fore.GREEN
yellow = Fore.YELLOW
init(autoreset=True)

app_name = [line for line in open("buildozer.spec", 'r').readlines() if line.startswith("title")][0].split("=")[1].strip()

class Compilation:
    @classmethod
    def start(cls, option):
        """
        Starts the compilation process
        """
        if option == '1':
            print(f"{yellow} Starting compilation")
            t1 = time.time()
            cls.notify_that_compilation_started()
            os.system("buildozer -v android debug deploy run")
            t2 = time.time()
            cls.notify_that_compilation_finished(t2 - t1)
            print(f"{green} Finished compilation")
            cls.debug_and_livestream()
        else:
            cls.debug_and_livestream()

    def notify_that_compilation_started():
        """
        Notifies the user that the compilation started
        """
        notification.notify(
            message=f"Compilation started at {time.strftime('%H:%M:%S')}",
            title=f"Compiling {app_name}",
        )

    def notify_that_compilation_finished(time):
        """
        Notifies the user that the compilation finished
        """
        notification.notify(
            message=f"Compilation finished in {time} seconds",
            title=f"Compiled {app_name}",
        )

    @classmethod
    def debug_and_livestream(cls):
        proc = Process(target=cls.debug)
        proc2 = Process(target=cls.livestream)
        proc.start()
        proc2.start()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                proc.terminate()
                proc2.terminate()
                break

    def debug():
        os.system("adb logcat -c")
        os.system("adb logcat | grep -i 'I python'")


    def livestream():
        for proc in psutil.process_iter():
            try:
                if proc.name() == "scrcpy":
                    print("scrcpy is already running")
                    break
            except psutil.NoSuchProcess:
                print("error")
        else:
            # os.system("scrcpy --window-x 1200 --window-y 100 --window-width 280 --always-on-top")
            os.system("scrcpy --always-on-top")


if __name__ == "__main__":
    print(f"{yellow} Choose an option:")
    option = input("1 - Compile, debug and livestream\n2 - Debug and livestream\n")
    Compilation.start(option)
