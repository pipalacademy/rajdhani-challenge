import requests


HAMR_URL = "https://hamr.rajdhani.pipal.in"


class HamrError(Exception):
    pass


class Hamr:
    def __init__(self, server_url):
        self.server_url = server_url

    def sync_app(self, app_name):
        url = f"{self.server_url}/apps/{app_name}/deploy"
        r = requests.post(url)

        if not r.ok:
            message = f"Request to Hamr API failed with status code {r.status_code}"
            try:
                data = r.json()
            except requests.exceptions.JSONDecodeError:
                pass
            else:
                message += f"\nstatus: {data['status']}\nmessage: {data['message']}"

            raise HamrError(message)

        return True


hamr = Hamr(HAMR_URL)
