import requests


class APIWork:

    def __init__(self, host, port, prefix):
        self._host = host
        self._port = port
        self._prefix = prefix

    def get_response(self, request, req_params):
        return requests.get(("http://%s:%d/%s/%s" % (self._host, self._port, self._prefix, request)), params=req_params)

    def request_pubkey(self):
        return requests.get("http://%s:%d/%s/v1/pubkey" % (self._host, self._port, self._prefix))

    def request_login(self, username, password, public_key):
        req_params = {"username": username, "password": password, "key": public_key}
        return requests.get("http://%s:%d/%s/v1/login" % (self._host, self._port, self._prefix), params=req_params)

    def request_all_employees(self, key):
        json_cont = {"key": key}
        return requests.post("http://%s:%d/%s/v1/get_all_employees" % (self._host, self._port, self._prefix), json_cont)


apW = APIWork("localhost", 8081, "worst-api")
public_key = apW.request_pubkey().text
private_key = apW.request_login("admin", "admin", public_key).text
print(private_key)
print(apW.request_all_employees(private_key))
