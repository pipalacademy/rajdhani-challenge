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
    def assert_autocomplete(q, expected_stations):
        assert sorted(site.get_station_autocomplete(q)) == sorted(expected_stations)

    assert_autocomplete("sbc", ["SBC"])
    assert_autocomplete("bangal", ["SBC", "BNCE", "BNC", "BJY"])
    assert_autocomplete("guntur", ["GNT", "NGNT"])
    assert_autocomplete("cst", ["CSTM"])
    assert_autocomplete("chennai", ["MS", "MSC", "MAS", "MPKT", "MPK", "MSF", "MSB"])

@task("search-trains")
def task_search_trains():
    """Find the trains on search.

    The `search_trains` functions in the db module is called
    to find the matching trains from source station to destination
    when the user searches for trains. Currently, that function
    returns a placeholder result. Replace that with the correct
    implementation.

    File: `rajdhani/db.py`<br>
    Function: `search_trains`
    """
    assert False, "Not yet implemented"

@task("search-trains-with-date")
def task_search_trains_with_date():
    """Support date and ticket class in train search.

    Enable date and class fields in the search form by setting
    `flag_date_class_in_search` in `config.py` to `True`.

    Update the `search_trains` function to consider the week of
    the day from the date and the ticket class to only include the
    trains that run that the specified week day.

    File: `rajdhani/db.py` <br>
    Function: `search_trains`
    """
    assert False, "Not yet implemented"

@task("search-filters")
def task_search_filters():
    """Implement search filters.

    Enable the filters on arrival time and departure time by setting
    the flag `flag_search_filters` to `True` in the `config.py`.

    Consider the arrival time and departure time filters when searching
    for trains.

    File: `rajdhani/db.py` <br>
    Function: `search_trains`
    """
    assert False, "Not yet implemented"

@task("train-schedule")
def task_train_schedule():
    """Show schedule of a train.

    Enable link to show the schedule of each train in the search results
    by setting the flag `flag_show_schedule_link` in the config to `True`.

    Implement the `get_train_schedule` function that takes the
    train number as argument and returns the schedule.

    File: `rajdhani/db.py` <br>
    Function: `get_train_schedule`
    """
    assert False, "Not yet implemented"

@task("seat-availability")
def task_seat_availability():
    """Show availability of seats for each train.

    Enable showing the number of seats available in each ticket class
    for each train in the search results by setting the flag
    `flag_seat_availability` in the config to `True`.

    Implement the function `get_seat_availability` that takes the
    train number as argument and returns the seat avaiblity for
    each ticket class.

    File: `rajdhani/db.py` <br>
    Function: `get_seat_availability`
    """
    assert False, "Not yet implemented"

@task("book-ticket")
def task_book_ticket():
    """Implement booking a ticket.

    Enable ticket booking by setting the flag
    `flag_ticket_booking` in the config to `True`.

    Implement the function `book_ticket` that takes train
    and passenger details and books a ticket by adding an entry
    in the database table.

    After booking a ticket, the number of available seats for that
    train in the booked ticket class should be reduced by one.

    File: `rajdhani/db.py` <br>
    Function: `book_ticket`
    """
    assert False, "Not yet implemented"

@task("email-conformation")
def task_email_confirmation():
    """Send an email to confirm the successful booking.

    Send an email to the passenger confirming the reservation.

    File: `rajdhani/booking.py` <br>
    Function: `send_email_confirmation`
    """
    assert False, "Not yet implemented"

@task("login-with-magic-link")
def task_login_with_magic_link():
    """Enable login with a magic link.

    Details coming soon..
    """
    assert False, "Not yet implemented"

@task("my-trips")
def task_my_trips():
    """Show my trips page for logged in users.

    Details coming soon..
    """
    assert False, "Not yet implemented"

def main():
    import sys
    name = sys.argv[1]
    site = Site(name)
    print(site.get_status())

if __name__ == "__main__":
    main()
