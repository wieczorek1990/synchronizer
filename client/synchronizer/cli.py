import dataclasses
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
        self.station_id = all_settings["station_id"]

        self.configs = []

    def set_configs(self, configs: list[Config]) -> None:
        self.configs = configs


class APICaller:
    API_ROOT = f"{PROTOCOL}{HOSTNAME}/api"

    def __init__(self, settings: LocalSettings) -> None:
        self.settings = settings

    def headers(self) -> dict:
        dictionary = {"Authorization": f"Bearer {self.settings.token}"}
        return dictionary

    def fetch_station(self, station_id: int) -> dict:
        url = f"{self.API_ROOT}/stations/{station_id}"
        headers = self.headers()
        response = requests.get(url, headers=headers)
        station = response.json()
        return station

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

            if station_a_pk == self.settings.station_id:
                synchronized_path = station_a["path"]
                push_to_station = station_b_pk
            elif station_b_pk == self.settings.station_id:
                synchronized_path = station_b["path"]
                push_to_station = station_a
            else:
                raise ValueError(
                    f"Invalid station connection: {station_connection}"
                )

            config = Config(synchronized_path, push_to_station)
            configs.append(config)
        self.settings.set_configs(configs)


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


def setup():
    pass


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
