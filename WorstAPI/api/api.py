import requests


class APIWork(object):

    def __init__(self, host, port, prefix):
        self._host = host
        self._port = port
        self._prefix = prefix
        self._base_url = "http://%s:%d/%s/" % (self._host, self._port, self._prefix)

    def request_pubkey(self):
        return requests.get(self._base_url + "v1/pubkey")

    def request_login(self, username, password, public_key):
        req_params = {"username": username, "password": password, "key": public_key}
        return requests.get(self._base_url + "v1/login", params=req_params)

    def request_all_employees(self, key):
        json_cont = {"key": key}
        return requests.post(self._base_url + "v1/get_all_employees",
                             json=json_cont)

    def request_create_employees(self, key, name, surname, email, phone, job, salary, dep_id):
        json_cont = {"key": key,
                     "employees": [{
                         "name": name,
                         "surname": surname,
                         "email": email,
                         "phone": phone,
                         "job": job,
                         "salary": salary,
                         "dep_id": dep_id
                     }]}
        return requests.post(self._base_url + "v1/create_new_employees",
                             json=json_cont)

    def request_delete_employees(self, key, user_id):
        json_cont = {"key": key,
                     "id": user_id
                     }
        return requests.post(self._base_url + "v1/delete_employees",
                             json=json_cont)

    def request_update_employees(self, key, name, surname, email, phone, job, salary, dep_id, id):
        json_cont = {"key": key,
                     "employees": [{
                         "name": name,
                         "surname": surname,
                         "email": email,
                         "phone": phone,
                         "job": job,
                         "salary": salary,
                         "dep_id": dep_id,
                         "id": id
                     }]}
        return requests.post(self._base_url + "v1/update_employees",
                             json=json_cont)

    def request_get_employees_history(self, key):
        json_cont = {"key": key}
        return requests.post(self._base_url + "v1/get_employee_history",
                             json=json_cont)

    def request_logout(self, key):
        json_cont = {"key": key}
        return requests.post(self._base_url + "v1/logout",
                             json=json_cont)


apW = APIWork("localhost", 8081, "worst-api")
public_key = apW.request_pubkey().text
#
# private_key = apW._request_login("admin", "mau", public_key).text
# print(private_key)
private_key = apW.request_login("admin", "admin", public_key).text
# print(private_key)
# all_resp = apW._request_all_employees(private_key).text

# create_resp = apW.request_create_employees(private_key, "Mau", "Hardy", "ma@mail.ru", "7-999-777-66-77", "PU_MAN",
#                                           3000, 30)
# create_resp = apW.request_create_employees(private_key, "Tom", "Hardy", "ema@mail.ru", "7-999-777-66-77", "PU_MAN",
#                                            3000, 30)
# create_resp = apW.request_update_employees(private_key, "R", "F", "cusww@mail.ru", "444", "ST_CLERK",
#                                             1000, 10, 500)
# create_resp = apW.request_update_employees(private_key, "Tom", "Hardy", "ema@mail.ru", "7-999-777-66-77", "PU_MAN",
#                                            3000, 215)


# create_resp = apW._request_get_employees_history(private_key)

#print(create_resp.content)
