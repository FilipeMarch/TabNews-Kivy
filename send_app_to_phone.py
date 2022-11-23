import trio
from colorama import Fore, Style, init

red = Fore.RED
green = Fore.GREEN
yellow = Fore.YELLOW
init(autoreset=True)


def get_last_port_used() -> int:
    last_port_used = open("configs/last_port_used", "r").read()
    print("Última porta usada: ", last_port_used)
    return int(last_port_used)


async def connect_to_server():
    try:
        with trio.move_on_after(1):
            LOCAL_IP = "192.168.0.48"
            client_socket = await trio.open_tcp_stream(
                LOCAL_IP, get_last_port_used()
            )
            return client_socket
    except Exception as e:
        print(f"{red}Error: {e}")
        return None


async def send_app():
    print(green + "Connecting to smartphone...")
    client_socket = await connect_to_server()
    if not client_socket:
        print(yellow + "Couldn't connect to smartphone")
        return
    print(green + f"Connected to smartphone: {client_socket}")

    CHUNK_SIZE = 4096
    with open(
        "app_copy.zip",
        "rb",
    ) as myzip:
        for chunk in iter(lambda: myzip.read(CHUNK_SIZE), b""):
            print("Sending chunk")
            await client_socket.send_all(chunk)
    print(green + "Finished sending app")


trio.run(send_app)
