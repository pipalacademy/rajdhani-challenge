import requests


HAMR_URL = "https://hamr.rajdhani.pipal.in"


class HamrError(Exception):
    pass


class Hamr:
    def __init__(self, server_url):
        self.server_url = server_url

    def create_app(self, app_name, git_url):
        url = f"{self.server_url}/apps/create"
        r = requests.post(url, data={"app_name": app_name, "git_url": git_url})

        if not r.ok:
            message = f"Create Request to Hamr API failed with status code {r.status_code}"
            try:
                data = r.json()
            except requests.exceptions.JSONDecodeError:
                pass
            else:
                error_status, error_msg = data["status"], data.get("message", "")
                message += f"\nstatus: {error_status}\nmessage: {error_msg}"

            raise HamrError(message)

        return True

    def sync_app(self, app_name):
        url = f"{self.server_url}/apps/{app_name}/deploy"
        r = requests.post(url)

        if not r.ok:
            message = f"Deploy Request to Hamr API failed with status code {r.status_code}"
            try:
                data = r.json()
            except requests.exceptions.JSONDecodeError:
                pass
            else:
                error_status, error_msg = data["status"], data.get("message", "")
                message += f"\nstatus: {error_status}\nmessage: {error_msg}"

            raise HamrError(message)

        return True


hamr = Hamr(HAMR_URL)
