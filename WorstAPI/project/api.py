import requests


class APIWork(object):
    LOGIN = "v1/login"
    PUBKEY = "v1/pubkey"
    GET_ALL_EMPLOYEES = "v1/get_all_employees"
    CREATE_NEW_EMPLOYEES = "v1/create_new_employees"
    DELETE_EMPLOYEES = "v1/delete_employees"
    UPDATE_EMPLOYEES = "v1/update_employees"
    EMPLOYEE_HISTORY = "v1/get_employee_history"
    LOGOUT = "v1/logout"
    EMPLOYEES_JSON_FIELD = "employees"
    PUBLIC_KEY_FIELD = "key"
    PASSWORD_FIELD = "password"
    USERNAME_FIELD = "username"
    ID_FIELD = "id"
    DEP_ID_FIELD = "dep_id"
    SALARY_FIELD = "salary"
    JOB_FIELD = "job"
    PHONE_FIELD = "phone"
    EMAIL_FIELD = "email"
    SURNAME_FIELD = "surname"
    NAME_FIELD = "name"
    EMPLOYEES_FIELD = "employees"
    KEY_FIELD = "key"
    BASE_URL_PATTERN = "http://%s:%d/%s/"

    def __init__(self, host, port, prefix):
        self._host = host
        self._port = port
        self._prefix = prefix
        self._base_url = self.BASE_URL_PATTERN % (self._host, self._port, self._prefix)

    def request_pubkey(self):
        return requests.get(self._base_url + self.PUBKEY)

    def request_login(self, username, password, pub_key):
        req_params = {self.USERNAME_FIELD: username, self.PASSWORD_FIELD: password, self.PUBLIC_KEY_FIELD: pub_key}
        return requests.get(self._base_url + self.LOGIN, params=req_params)

    def request_all_employees(self, key):
        json_cont = {self.KEY_FIELD: key}
        return requests.post(self._base_url + self.GET_ALL_EMPLOYEES,
                             json=json_cont)

    def request_create_employees(self, key, emp):
        json_cont = {self.KEY_FIELD: key,
                     self.EMPLOYEES_FIELD: [{
                         self.NAME_FIELD: emp.name,
                         self.SURNAME_FIELD: emp.surname,
                         self.EMAIL_FIELD: emp.email,
                         self.PHONE_FIELD: emp.phone,
                         self.JOB_FIELD: emp.job,
                         self.SALARY_FIELD: emp.salary,
                         self.DEP_ID_FIELD: emp.dep_id,
                     }]}
        return requests.post(self._base_url + self.CREATE_NEW_EMPLOYEES,
                             json=json_cont)

    def request_delete_employees(self, key, user_id):
        json_cont = {self.KEY_FIELD: key,
                     self.ID_FIELD: user_id
                     }
        return requests.post(self._base_url + self.DELETE_EMPLOYEES,
                             json=json_cont)

    def request_update_employees(self, key, emp, emp_id):
        json_cont = {self.KEY_FIELD: key,
                     self.EMPLOYEES_FIELD: [{
                         self.NAME_FIELD: emp.name,
                         self.SURNAME_FIELD: emp.surname,
                         self.EMAIL_FIELD: emp.email,
                         self.PHONE_FIELD: emp.phone,
                         self.JOB_FIELD: emp.job,
                         self.SALARY_FIELD: emp.salary,
                         self.DEP_ID_FIELD: emp.dep_id,
                         self.ID_FIELD: emp_id
                     }]}
        return requests.post(self._base_url + self.UPDATE_EMPLOYEES,
                             json=json_cont)

    def request_get_employees_history(self, key):
        json_cont = {self.KEY_FIELD: key}
        return requests.post(self._base_url + self.EMPLOYEE_HISTORY,
                             json=json_cont)

    def request_logout(self, key):
        json_cont = {self.KEY_FIELD: key}
        return requests.post(self._base_url + self.LOGOUT,
                             json=json_cont)
