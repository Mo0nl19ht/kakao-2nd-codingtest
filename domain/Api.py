import requests, json


class Api:
    def __init__(self, x_auth, problem):
        self.host = "https://68ecj67379.execute-api.ap-northeast-2.amazonaws.com/api"
        self.x_auth = x_auth
        self.problem = problem
        self.header = {}
        self._start(x_auth, problem)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def _start(self, x_auth, problem):
        response = requests.post(
            self.host + "/start",
            headers={"X-Auth-Token": x_auth, "Content-Type": "application/json"},
            json={"problem": problem},
        ).json()
        self.header = {
            "Authorization": response["auth_key"],
            "Content-Type": "application/json",
        }
        return response["auth_key"]

    def _request(self, path, method, data={}):
        url = self.host + path
        if method == "get":
            return requests.get(url, headers=self.header)
        elif method == "post":
            return requests.post(url, headers=self.header, json=data)
        elif method == "put":
            return requests.put(url, headers=self.header, json=data)

    def new_requests(self):
        return self._request("/new_requests", "get").json()["reservations_info"]

    def reply(self, replies):
        # accepted, refused
        replies = {"replies": replies}
        return self._request("/reply", "put", replies).json()["day"]

    def simulate(self, room_assign):
        room_assign = {"room_assign": room_assign}
        return self._request("/simulate", "put", room_assign).json()["fail_count"]

    def score(self):
        return self._request("/score", "get").json()
