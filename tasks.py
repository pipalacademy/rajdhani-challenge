from __future__ import annotations
from cmath import exp
import requests
import yaml
from dataclasses import dataclass, asdict
from collections import namedtuple
from typing import List
from bs4 import BeautifulSoup

from hamr import HamrError, hamr

DOMAIN = "rajdhani.pipal.in"

class Site:
    def __init__(self, name):
        self.name = name
        self.domain = f"{name}.{DOMAIN}"
        self.base_url = f"https://{self.domain}"

    def get(self, path, **kwargs):
        url = self.base_url.rstrip("/") + path
        print("GET", url)
        return requests.get(url, **kwargs)

    def sync(self):
        HamrResponse = namedtuple("HamrResponse", ["ok", "message"])

        try:
            hamr.sync_app(self.name)
        except HamrError as e:
            return HamrResponse(ok=False, message=str(e))

        return HamrResponse(ok=True, message="")

    def is_homepage_enabled(self):
        return "<h2>Search Trains</h2>" in self.get("/").text

    def get_station_autocomplete(self, prefix):
        """Returns codes of all the stations matching the prefix.
        """
        results = self.get("/api/stations", params={"q": prefix}).json()
        return [row['code'] for row in results]

    def get_status(self):
        """Runs the tests for each task and returns the status for each task.
        """
        tasks = {}
        for task in TASKS:
            task_status = task.verify(self)
            tasks[task.name] = asdict(task_status)
            if task_status.status != "pass":
                break
        return dict(tasks=tasks, current_task=task.name)

@dataclass
class CheckStatus:
    title: str
    status: str = "pass"
    message: str = ""

    def fail(self, message):
        self.status = "fail"
        self.message = message
        return self

    def error(self, message):
        self.status = "error"
        self.message = message
        return self

CHECKS = {}
def register_check(check):
    CHECKS[check.__name__] = check
    return check

class CheckFailed(Exception):
    pass

class Check:
    def validate(self, site):
        status = CheckStatus(self.title)
        try:
            self.do_validate(site)
            return status
        except CheckFailed as e:
            return status.fail(str(e))
        except Exception as e:
            return status.error(str(e))

    def do_validate(self, site):
        raise NotImplementedError()

@register_check
class check_not_implemented(Check):
    def __init__(self):
        self.title = "Checks are not yet implemented for this task"

    def do_validate(self, site):
        raise CheckFailed("coming soon...")

@register_check
class check_flag(Check):
    def __init__(self, flag):
        self.flag = flag
        self.title = f"Checks flag: {flag}"

    def do_validate(self, site):
        flags = site.get("/api/flags").json()
        if not flags.get(self.flag):
            raise CheckFailed(f"Feature flag `{self.flag}` is not set to `True`.")

@register_check
class check_webpage_content(Check):
    def __init__(self, url, expected_text):
        self.url = url
        self.expected_text = expected_text
        self.title = f"Check webpage content: {url}"

    def do_validate(self, site):
        if not self.expected_text in site.get(self.url).text:
            message = f'Text "{self.expected_text}"\nis expected in the web page {site.base_url}{self.url},\nbut it is not found.'
            raise CheckFailed(message)

@register_check
class check_autocomplete(Check):
    def __init__(self, q, expected_stations):
        self.q = q
        self.expected_stations = expected_stations
        self.title = f"Check autocomplete for input: {q}"

    def do_validate(self, site):
        stations = site.get_station_autocomplete(self.q)
        if sorted(stations) != sorted(self.expected_stations):
            message = (
                f"For Input {self.q},\n"
                f"expected the output to include stations: {' '.join(self.expected_stations)},\n"
                f"but found: {' '.join(stations)}")
            raise CheckFailed(message)

@register_check
class check_search_trains(Check):
    def __init__(self,
            from_station,
            to_station,
            ticket_class=None,
            departure_time=[],
            arrival_time=[],
            expected_trains=[]):
        self.from_station = from_station
        self.to_station = to_station
        self.ticket_class = ticket_class
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.expected_trains = [str(n) for n in expected_trains]
        self.title = f"Search Trains: {from_station} -> {to_station}"

        if ticket_class:
            self.title += f" [{ticket_class}]"
        if departure_time:
            self.title += f" dt={departure_time!r}"
        if arrival_time:
            self.title += f" at={arrival_time!r}"

    def do_validate(self, site):
        params = {
            "from": self.from_station,
            "to": self.to_station,
            "class": self.ticket_class,
            "dt": self.departure_time,
            "at": self.arrival_time
        }
        trains = site.get("/api/search", params=params).json()

        numbers = [str(t['number']) for t in trains]

        if sorted(numbers) != sorted(self.expected_trains):
            message = (
                f"The result of search_trains({self.from_station!r}, {self.to_station!r})\n"
                f"is expected to include trains: {', '.join(self.expected_trains)}\n"
                f"but found: {', '.join(numbers)}")
            raise CheckFailed(message)

        expected_keys = [
            "number",
            "name",
            "from_station_code",
            "from_station_name",
            "to_station_code",
            "to_station_name",
            "departure",
            "arrival",
            "duration_h",
            "duration_m"
        ]
        for t in trains:
            missing_keys = set(t.keys()) - set(expected_keys)
            if missing_keys:
                message = (
                    "The search_trains function is expected to return list of dicts\n" +
                    "with the following fields:\n" +
                    str(expected_keys) + "\n,"
                    "but found: " + str(list(t.keys())))
                raise CheckFailed(message)

@register_check
class check_schedule(Check):
    def __init__(self, train, ensure_rows):
        self.train = train
        self.ensure_rows = ensure_rows
        self.title = f"Check schedule for train {train}"

    def extract_table(self, html):
        soup = BeautifulSoup(html, "lxml")
        table = soup.select("table")[0]
        return self.parse_table(table)

    def parse_table(self, table):
        return [self.parse_row(tr) for tr in table.select("tr")]

    def parse_row(self, tr):
        return [cell.text.strip() for cell in tr.select("th,td")]

    def do_validate(self, site):
        html = site.get(f"/trains/{self.train}").text
        schedule = self.extract_table(html)

        for row in self.ensure_rows:
            if row not in schedule:
                message = f"Missing following entry in the schedule of train {self.train}:\n {row}"
                raise CheckFailed(message)

@dataclass
class TaskStatus:
    status: str
    checks: List[CheckStatus]

class Task:
    def __init__(self, name, title, description, checks):
        self.name = name
        self.title = title
        self.description = description
        self.checks = checks

    def verify(self, site) -> TaskStatus:
        print(f"[{site.domain}] verifying task {self.name}...")

        results = [c.validate(site) for c in self.checks]
        print(results)
        if all(c.status == "pass" for c in results):
            status = "pass"
        else:
            status = "fail"
        return TaskStatus(status, checks=results)

    @classmethod
    def load_from_file(cls, filename) -> List[Task]:
        """Loads a list of tasks from a file.
        """
        data = yaml.safe_load_all(open(filename))
        return [cls.from_dict(d) for d in data]

    @classmethod
    def from_dict(cls, data) -> Task:
        """Loads a Task from dict.
        """
        name = data['name']
        title = data['title']
        description = data['description']
        checks = [cls.parse_check(c) for c in data['checks']]
        return Task(name, title, description, checks)

    @staticmethod
    def parse_check(check_data):
        if isinstance(check_data, str):
            return CHECKS[check_data]()
        elif isinstance(check_data, dict) and len(check_data) == 1:
            name, args = list(check_data.items())[0]
            cls = CHECKS[name]
            return cls(**args)
        else:
            raise ValueError(f"Invalid check: {check_data}")

TASKS = Task.load_from_file("tasks.yml")

def main():
    import sys, json
    name = sys.argv[1]
    site = Site(name)
    print(json.dumps(site.get_status(), indent=2))

if __name__ == "__main__":
    main()
