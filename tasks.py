import requests
import inspect
from collections import namedtuple

from hamr import HamrError, hamr

DOMAIN = "rajdhani.pipal.in"

class Site:
    def __init__(self, name):
        self.name = name
        self.domain = f"{name}.{DOMAIN}"
        self.base_url = f"https://{self.domain}"

    def get(self, path, **kwargs):
        url = self.base_url.rstrip("/") + path
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
        results = self.get("/api/stations", params={"prefix": prefix}).json()
        return [row['code'] for row in results]

    def get_status(self):
        """Runs the tests for each task and returns the status for each task.
        """
        status = {}
        for task in TASKS.values():
            is_done = self.verify_task(task)
            status[task.name] = is_done
            if not is_done:
                break

        return dict(status=status, current_task=task.name)

    def verify_task(self, task):
        print(f"[{self.domain}] verifying task {task.name}...")
        try:
            task(self)
            return True
        except AssertionError:
            return False

TASKS = {}

def task(name):
    def decorator(f):
        TASKS[name] = Task(name, f)
        return f
    return decorator

class Task:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        doc = inspect.getdoc(func)
        self.title, self.description = doc.split("\n", 1)
        self.description = self.description.strip()

    def __call__(self, site):
        return self.func(site)

@task("homepage")
def task_homepage(site):
    """Enable the homepage.

    Set `enable_homepage = True` in the `rajdhani/config.py`.
    """
    assert site.is_homepage_enabled()

@task("autocomplete")
def task_autocomplete(site):
    """Implement the autocomplete on the home page.

    The autocomplete on the home page to select the from and to stations is
    a dummy implementation. Replace that with a correct implementation.
    """
    assert "TK" in site.get_station_autocomplete("tk")
    assert "TK" in site.get_station_autocomplete("Tumakuru")
    assert "TK" in site.get_station_autocomplete("tk")

    assert "MAQ" in site.get_station_autocomplete("Mangalu")
    assert "MAJN" in site.get_station_autocomplete("Mangalu")

def main():
    import sys
    name = sys.argv[1]
    site = Site(name)
    print(site.get_status())

if __name__ == "__main__":
    main()
