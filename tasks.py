from __future__ import annotations
from cmath import exp
import requests
import yaml
from dataclasses import dataclass, asdict
from collections import namedtuple
from typing import List

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
        raise CheckFailed()

@register_check
class check_flag(Check):
    def __init__(self, flag):
        self.title = f"Checks flag: {flag}"

    def do_validate(self, site):
        pass

@register_check
class check_webpage_content(Check):
    def __init__(self, url, expected_text):
        self.url = url
        self.expected_text = expected_text
        self.title = f"Check webpage content: {url}"

    def do_validate(self, site):
        if not self.expected_text in site.get(self.url).text:
            message = "Text `{expected_text}` is expected in web page /, but it is not found."
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
