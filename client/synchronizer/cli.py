import json
import os
import pprint
import time

import requests
from watchdog import events, observers
from watchdog.events import FileSystemEvent

DEBUG = bool(int(os.environ.get("DEBUG", "0")))

if DEBUG:
    SLEEP_TIME = 1
    PROTOCOL = "http://"
    HOSTNAME = "localhost"
else:
    SLEEP_TIME = 12
    PROTOCOL = "https://"
    HOSTNAME = "synchronizer.soiree.tech"


class LocalSettings:
    def __init__(self) -> None:
        with open("settings.json") as file_pointer:
            all_settings = json.load(file_pointer)
        self.token = all_settings["token"]
        self.station_id = all_settings["station_id"]
        self.path = None

    def set_path(self, path: str) -> None:
        self.path = path


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
        station_connections = self.fetch_station_connections()
        for station in station_connections:
            if (
                station["station_a"] == self.settings.station_id
                or station["station_b"] == self.settings.station_id
            ):
                station = self.fetch_station(self.settings.station_id)
                path = station["path"]
                self.settings.set_path(path)
                return
        else:
            raise ValueError("No matching station found.")


class EventHandler(events.FileSystemEventHandler):
    def on_created(self, event: FileSystemEvent) -> None:
        pprint.pprint(event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        pprint.pprint(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        pprint.pprint(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        pprint.pprint(event)


def initialize(path: str) -> observers.Observer:
    event_handler = EventHandler()
    observer = observers.Observer()
    observer.schedule(event_handler, path, recursive=True)
    return observer


def log() -> None:
    print(f"Sleeping for {SLEEP_TIME} seconds.")
    time.sleep(SLEEP_TIME)


def main() -> None:
    settings = LocalSettings()
    api_caller = APICaller(settings)
    api_caller.setup()

    observer = initialize(settings.path)
    observer.start()
    try:
        while True:
            log()
    except KeyboardInterrupt:
        print("\nEnding synchronizer main procedure.")
        observer.stop()
    observer.join()
