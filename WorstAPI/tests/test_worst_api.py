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

    @pytest.fixture(scope="class", params=[
        ("HR", "qwaszx12", "localhost", 1521, "xe")
    ])
    def setup_db_worker(self, request):
        (user, password, host, port, db) = request.param
        return DBWork(user, password, host, port, db)

    def test_req_public_key_success(self, setup_api_worker):
        api_worker = setup_api_worker
        resp = api_worker._request_pubkey()
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
        pub_key = api_worker._request_pubkey().text
        resp = api_worker._request_login(username, password, pub_key)
        resp_str = str(resp)
        private_key = resp.text
        assert ((self.SUCCESS_CODE in resp_str
                 and len(private_key) == self.DEVELOPER_KEY_LENGTH
                 and username == "developer"
                 or len(private_key) == self.PRIVATE_KEY_LENGTH)
                or (self.UNAUTHORIZED_CODE in resp_str and self.UNAUTHORIZED_TEXT in resp.text)), "Invalid args"

    @pytest.mark.parametrize("username, password, public_key", [
        ("admin", "admin", "some-key"),
        ("developer", "rer", "some_wrong.key")
    ])
    def test_login_invalid_key(self, username, password, public_key, setup_api_worker):
        api_worker = setup_api_worker
        resp = api_worker._request_login(username, password, public_key)
        resp_str = str(resp)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid args"

    @pytest.mark.parametrize("username,password", [
        ("admin", "admin"),
        ("developer", "developer"),
    ])
    @pytest.mark.xfail(reason="double login", strict=True)
    def test_login_use_public_key_once(self, username, password, setup_api_worker):
        api_worker = setup_api_worker
        pub_key = api_worker._request_pubkey().text
        private_key = api_worker._request_login(username, password, pub_key).text
        api_worker._request_logout(private_key)
        private_key = api_worker._request_login(username, password, pub_key).text

    @pytest.mark.parametrize("username,password", [
        ("admin", "admin"),
        ("developer", "developer"),
    ])
    def test_login_use_private_key_several_times(self, username, password, setup_api_worker):
        api_worker = setup_api_worker
        pub_key = api_worker._request_pubkey().text
        private_key = api_worker._request_login(username, password, pub_key).text
        resp = api_worker._request_all_employees(private_key)
        api_worker._request_logout(private_key)
        second_private_key = api_worker._request_login(username, password, pub_key).text
        resp = api_worker._request_all_employees(private_key)

    @pytest.mark.parametrize("username,password", [
        ("admin", "admin"),
        ("developer", "developer"),
    ])
    def test_get_all_employees_success(self, username, password, setup_api_worker):
        api_worker = setup_api_worker
        pub_key = api_worker._request_pubkey().text
        private_key = api_worker._request_login(username, password, pub_key).text
        resp = api_worker._request_all_employees(private_key)
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

    @pytest.mark.parametrize("incorrect_key", [
        ("admin", "admin"),
        ("developer", "developer"),
    ])
    def test_get_all_employees_bad_key(self, incorrect_key, setup_api_worker):
        api_worker = setup_api_worker
        resp = api_worker._request_all_employees(incorrect_key)
        resp_str = str(resp)
        assert self.INTERVAL_SERVER_ERROR_CODE in resp_str, "Invalid args"

    @pytest.mark.parametrize("username, password, name, surname, email, phone, job, salary, dep_id", [
        ("admin", "admin", "Luis", "Hardy", "someeee@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
    ])
    def test_create_employees_accepted(self, username, password, name, surname, email, phone, job, salary, dep_id,
                                       setup_api_worker, setup_db_worker):
        api_worker = setup_api_worker

        pub_key = api_worker._request_pubkey().text
        private_key = api_worker._request_login(username, password, pub_key).text
        resp = api_worker._request_create_employees(private_key, name, surname, email, phone, job, salary,
                                                    dep_id)
        resp_str = str(resp)
        print(resp_str)
        print(resp.text)
        print(resp.content)
        # json_cont = {
        #                  "first_name": name,
        #                  "last_name": surname,
        #                  "email": email,
        #                  "phone_number": phone,
        #                  "job_id": job,
        #                  "salary": salary,
        #                  "department_id": dep_id
        #              }
        # with setup_db_worker as db_worker:
        #     print(db_worker.select_row_from_table("employees", json_cont))
        #     assert self.ACCEPTED_CODE in resp_str and db_worker.select_row_from_table("employees", json_cont) != [], "Invalid args"
