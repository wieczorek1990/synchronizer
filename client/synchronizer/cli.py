import dataclasses
import getpass
import json
import os
import pprint
import sys
import time

import requests
from watchdog import events, observers

DEBUG = bool(int(os.environ.get("DEBUG", "0")))

if DEBUG:
    SLEEP_TIME = 1
    PROTOCOL = "http://"
    HOSTNAME = "localhost"
else:
    SLEEP_TIME = 12
    PROTOCOL = "https://"
    HOSTNAME = "synchronizer.soiree.tech"


@dataclasses.dataclass
class Station:
    id: int
    path: str


@dataclasses.dataclass
class Config:
    synchronized_path: str
    push_to_station_pk: int


class LocalSettings:
    def __init__(self) -> None:
        with open("settings.json") as file_pointer:
            all_settings = json.load(file_pointer)

        self.token = all_settings["token"]
        self.station_pk = all_settings["station_pk"]

        self.configs = []

    def set_configs(self, configs: list[Config]) -> None:
        self.configs = configs


class APICaller:
    API_ROOT = f"{PROTOCOL}{HOSTNAME}/api"

    def __init__(self, settings: LocalSettings | None) -> None:
        self.settings = settings

    def headers(self) -> dict:
        dictionary = {"Authorization": f"Bearer {self.settings.token}"}
        return dictionary

    def fetch_token(self, username: str, password: str) -> str:
        url = f"{self.API_ROOT}/auth/token/"
        data = {"username": username, "password": password}
        response = requests.post(url, data=data)
        authorization = response.json()
        token = authorization["token"]
        return token

    def fetch_station(self, station_pk: int) -> dict:
        url = f"{self.API_ROOT}/stations/{station_pk}"
        headers = self.headers()
        response = requests.get(url, headers=headers)
        station = response.json()
        return station

    def fetch_stations(self) -> list:
        url = f"{self.API_ROOT}/stations/"
        headers = self.headers()
        response = requests.get(url, headers=headers)
        stations = response.json()
        return stations

    def fetch_station_connections(self) -> dict:
        url = f"{self.API_ROOT}/station-connections/"
        headers = self.headers()
        response = requests.get(url, headers=headers)
        station_connections = response.json()
        return station_connections

    def setup(self) -> None:
        configs = []
        station_connections = self.fetch_station_connections()
        for station_connection in station_connections:
            station_a_pk = station_connection["station_a"]
            station_b_pk = station_connection["station_b"]

            station_a = self.fetch_station(station_a_pk)
            station_b = self.fetch_station(station_b_pk)

            if station_a_pk == self.settings.station_pk:
                synchronized_path = station_a["path"]
                push_to_station = station_b_pk
            elif station_b_pk == self.settings.station_pk:
                synchronized_path = station_b["path"]
                push_to_station = station_a
            else:
                raise ValueError(
                    f"Invalid station connection: {station_connection}"
                )

            config = Config(synchronized_path, push_to_station)
            configs.append(config)
        self.settings.set_configs(configs)

    def get_station_pk(self) -> int:
        stations = self.fetch_stations()
        print("Available stations:")
        for station in stations:
            print(f"{station["name"]}")
        # TODO(lukasz.wieczorek): Implement.
        station_pk_string = "1"
        station_pk = int(station_pk_string)
        return station_pk


class EventHandler(events.FileSystemEventHandler):
    def __init__(self, config: Config) -> None:
        super().__init__()

        self.config = config

    def __str__(self) -> str:
        return f"{self.config}"

    def on_created(self, event: events.FileSystemEvent) -> None:
        pprint.pprint(event)

    def on_deleted(self, event: events.FileSystemEvent) -> None:
        pprint.pprint(event)

    def on_modified(self, event: events.FileSystemEvent) -> None:
        pprint.pprint(event)

    def on_moved(self, event: events.FileSystemEvent) -> None:
        pprint.pprint(event)


def create_observer(
    event_handler: EventHandler, path: str
) -> observers.Observer:
    observer = observers.Observer()
    observer.schedule(event_handler, path, recursive=True)
    return observer


def log() -> None:
    print(f"Sleeping for {SLEEP_TIME} seconds.")
    time.sleep(SLEEP_TIME)


def run() -> None:
    print("Starting.")

    settings = LocalSettings()
    api_caller = APICaller(settings)
    api_caller.setup()

    all_observers = []
    for config in settings.configs:
        event_handler = EventHandler(config)
        print(f"Creating observer for path: {config.synchronized_path}")
        observer = create_observer(event_handler, config.synchronized_path)
        all_observers.append(observer)

    print("Starting observers.")
    for observer in all_observers:
        observer.start()

    try:
        while True:
            log()
    except KeyboardInterrupt:
        print("\nStopping observers.")
        for observer in all_observers:
            observer.stop()

    print("Joining observers.")
    for observer in all_observers:
        observer.join()

    print("Exiting.")


def save_settings(token: str, station_pk: int | None) -> None:
    settings = {"token": token, "station_pk": station_pk}
    with open("settings.json", "w") as file_pointer:
        json.dump(settings, file_pointer, indent=4)
        file_pointer.write("\n")


def prompt(name: str, password: bool = False) -> str:
    capitalized_name = name.capitalize()
    if not password:
        input_string = input(f"{capitalized_name}: ")
    else:
        input_string = getpass.getpass()
    return input_string


def setup():
    if os.path.exists("settings.json"):
        print("Already setup.")
        return

    username, password = prompt("username"), prompt("password", password=True)

    api_caller = APICaller(None)
    token = api_caller.fetch_token(username, password)
    save_settings(token, None)

    settings = LocalSettings()
    api_caller = APICaller(settings)
    station_pk = api_caller.get_station_pk()
    save_settings(token, station_pk)


def print_help():
    print(
        "Synchronizer client.\n"
        "Usage:\n"
        "\tpython -m synchronizer run|setup|help"
    )


def main() -> None:
    try:
        command = sys.argv[1]
    except IndexError:
        print_help()
        return

    match command:
        case "run":
            print("Starting running.")
            run()
        case "setup":
            print("Starting setup.")
            setup()
        case "help":
            print("Starting help.")
            print_help()
        case command:
            print(f"Invalid command: {command}")
            print_help()
