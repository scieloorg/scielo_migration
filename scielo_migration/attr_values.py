import csv
import json


def read_csv_file(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row


def write_csv_file(file_path, items):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['isis', 'sps']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item)


def read_json_file(file_path):
    with open(file_path, "r") as fp:
        return json.loads(fp.read())


def get_isis_and_sps_items(sps_to_isis_dict):
    return [
        {"isis": v, "sps": k}
        for k, v in sps_to_isis_dict.items()
    ]


class AttrValues:

    def __init__(self, items):
        self._items = items
        self._sps = None
        self._isis = None

    def _load_values(self):
        self._sps = {}
        self._isis = {}
        for item in self._items:
            isis_value = item['isis']
            sps_value = item['sps']
            self._sps[isis_value] = sps_value
            self._isis[sps_value] = isis_value

    def get_sps_value(self, isis_value):
        if not self._sps:
            self._load_values()
        return self._sps.get(isis_value)

    def get_isis_value(self, sps_value):
        if not self._isis:
            self._load_values()
        return self._isis.get(sps_value)

