import pytest

from api.api import APIWork
from api.db_work import DBWork


class TestWorstApi(object):
    SUCCESS_CODE = "200"
    ACCEPTED_CODE = "202"
    INTERVAL_SERVER_ERROR_CODE = "500"
    UNAUTHORIZED_CODE = "401"
    UNAUTHORIZED_TEXT = "Unauthorized"

    PUBLIC_KEY_LENGTH = 36
    PRIVATE_KEY_LENGTH = 64
    DEVELOPER_KEY_LENGTH = 76

    @pytest.fixture(scope="class", params=[
        ("localhost", 8081, "worst-api")
    ])
    def setup_api_worker(self, request):
        (host, port, prefix) = request.param
        return APIWork(host, port, prefix)

    @pytest.fixture(scope="function", params=[
        ("HR", "qwaszx12", "localhost", 1521, "xe")
    ])
    def setup_db_worker(self, request):
        (user, password, host, port, db) = request.param
        db_worker = DBWork(user, password, host, port, db)
        yield db_worker
        db_worker.close_conn()

    @pytest.fixture(scope="function", params=[
        ("admin", "admin"),
        ("developer", "developer")
    ])
    def user_pwd_args(self, request):
        return request.param

    @pytest.fixture(scope="function", params=[
        "key",
        "very-bad-key"
    ])
    def invalid_key_args(self, request):
        return request.param

    @pytest.fixture(scope="function", params=[
        ("Mau", "Hardy", "maum@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)
    ])
    def user_obj_args(self, request, setup_db_worker):
        (name, surname, email, phone, job, salary, dep_id) = request.param
        db_worker = setup_db_worker
        yield request.param
        json_cont = {
            "first_name": name,
            "last_name": surname,
            "email": email,
            "phone_number": phone,
            "job_id": job,
            "salary": salary,
            "department_id": dep_id
        }
        db_worker.delete_from_table("employees", json_cont)

    def test_req_public_key_success(self, setup_api_worker):
        print(setup_api_worker)
        api_worker = setup_api_worker
        resp = api_worker.request_pubkey()
        print(resp.text)
        assert self.SUCCESS_CODE in str(resp) and len(resp.text) == self.PUBLIC_KEY_LENGTH

    @pytest.mark.parametrize("username,password", [
        ("admin", "admin"),
        ("developer", "developer"),
        ("user", "user"),
        ("admin.", "content"),
        ("user", "pasw_content"),
        ("developer ", "some.content"),
        ("some_name", "some_passw")
    ])
    def test_login_success(self, username, password, setup_api_worker):
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        resp = api_worker.request_login(username, password, pub_key)
        resp_str = str(resp)
        private_key = resp.text
        assert ((self.SUCCESS_CODE in resp_str
                 and len(private_key) == self.DEVELOPER_KEY_LENGTH
                 and username == "developer"
                 or len(private_key) == self.PRIVATE_KEY_LENGTH)
                or (self.UNAUTHORIZED_CODE in resp_str and self.UNAUTHORIZED_TEXT in resp.text)), "Invalid login method"

    def test_login_invalid_key(self, invalid_key_args, user_pwd_args, setup_api_worker):
        invalid_key = invalid_key_args
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        resp = api_worker.request_login(username, password, invalid_key)
        resp_str = str(resp)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid login method"

    @pytest.mark.xfail(reason="double login", strict=True)
    def test_login_use_public_key_once(self, user_pwd_args, setup_api_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        api_worker.request_logout(private_key)
        private_key = api_worker.request_login(username, password, pub_key).text

    def test_login_use_private_key_several_times(self, user_pwd_args, setup_api_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        resp = api_worker.request_all_employees(private_key)
        api_worker.request_logout(private_key)
        second_private_key = api_worker.request_login(username, password, pub_key).text
        resp = api_worker.request_all_employees(private_key)

    def test_get_all_employees_success(self, user_pwd_args, setup_api_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        resp = api_worker.request_all_employees(private_key)
        resp_str = str(resp.json)
        resp_json_arr = resp.json()
        for json_obj in resp_json_arr:
            assert self.SUCCESS_CODE in resp_str \
                   and "surname" in json_obj \
                   and "phone" in json_obj \
                   and "job_id" in json_obj \
                   and "name" in json_obj \
                   and "hire_date" in json_obj \
                   and "salary" in json_obj \
                   and "email" in json_obj, "Invalid get_all_employees"

    def test_get_all_employees_invalid_key(self, invalid_key_args, setup_api_worker):
        invalid_key = invalid_key_args
        api_worker = setup_api_worker
        resp = api_worker.request_all_employees(invalid_key)
        resp_str = str(resp)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid get_all_employees"

    def test_create_employees_accepted(self, user_obj_args, user_pwd_args, setup_api_worker, setup_db_worker):
        (name, surname, email, phone, job, salary, dep_id) = user_obj_args
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        resp = api_worker.request_create_employees(private_key, name, surname, email, phone, job, salary,
                                                   dep_id)
        resp_str = str(resp)
        json_cont = {
            "first_name": name,
            "last_name": surname,
            "email": email,
            "phone_number": phone,
            "job_id": job,
            "salary": salary,
            "department_id": dep_id
        }
        db_worker = setup_db_worker
        selected_value = db_worker.select_row_from_table("employees", json_cont)
        assert self.ACCEPTED_CODE in resp_str and selected_value != [] and len(selected_value) == 1, "Invalid create " \
                                                                                                     "new employees"

    def test_create_employees_invalid_key(self, invalid_key_args, user_obj_args, user_pwd_args, setup_api_worker,
                                          setup_db_worker):
        (name, surname, email, phone, job, salary, dep_id) = user_obj_args
        invalid_key = invalid_key_args
        api_worker = setup_api_worker
        resp = api_worker.request_create_employees(invalid_key, name, surname, email, phone, job, salary,
                                                   dep_id)
        resp_str = str(resp)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid create new employees"

    @pytest.mark.parametrize("sec_name, sec_surname, sec_phone, sec_job, sec_salary, sec_dep_id", [
        ("Mau", "Hardy", "7-999-777-66-77", "PU_MAN", 3000, 30)
    ])
    def test_create_employees_existing_email(self, sec_name, sec_surname, sec_phone, sec_job, sec_salary, sec_dep_id,
                                             user_obj_args, user_pwd_args, setup_api_worker, setup_db_worker):
        (name, surname, email, phone, job, salary, dep_id) = user_obj_args
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        resp = api_worker.request_create_employees(private_key, name, surname, email, phone, job, salary,
                                                   dep_id)
        resp = api_worker.request_create_employees(private_key, sec_name, sec_surname, email, sec_phone, sec_job,
                                                   sec_salary,
                                                   sec_dep_id)
        resp_str = str(resp)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid create new employees"

    @pytest.mark.parametrize("name, surname, email, phone, job, salary, dep_id", [
        ("Mau", "Hardy", "some.mail", "7-999-777-66-77", "PU_MAN", 3000, "some"),
        ("Mau", "Hardy", "3mail", "7-999-777-66-77", "some", 3000, 30),
        (9, "Hardy", "2mail", "7-999-777-66-77", "PU_MAN", 3000, 30),
        ("Mau", "Lol", "1mail", "7-999-777-66-77", "PU_MAN", 3000, 30),
        ("Mau", "Hardy", 4, "7-999-777-66-77", "PU_MAN", 3000, 30),
        ("Mau", "Hardy", "11mail", 1, "PU_MAN", 3000, 30),
        ("Mau", "Hardy", "22mail", "7-999-777-66-77", "PU_MAN", "some_salary", 30),
    ])
    def test_create_employees_existing_email(self, name, surname, email, phone, job, salary, dep_id,
                                             user_pwd_args, setup_api_worker, setup_db_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker
        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        resp = api_worker.request_create_employees(private_key, name, surname, email, phone, job, salary,
                                                   dep_id)
        resp_str = str(resp)
        print(resp_str)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid create new employees"
