import pytest
from hamcrest import assert_that, all_of, has_key, equal_to, has_length, is_not, empty

from project.employee_class import Employee
from project.http_response_data_class import HttpResponseData
from .employee_db_data_class import EmployeeDBData


class TestWorstApi(object):

    def test_req_public_key_success(self, setup_api_worker):
        api_worker = setup_api_worker

        resp = api_worker.request_pubkey()
        assert_that(resp.status_code, equal_to(HttpResponseData.SUCCESS_CODE))
        assert_that(resp.text, has_length(EmployeeDBData.PUBLIC_KEY_LENGTH))

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
        private_key = resp.text

        if username == EmployeeDBData.DEVELOPER_NAME:
            assert_that(resp.status_code, equal_to(HttpResponseData.SUCCESS_CODE), "Invalid login method")
            assert_that(private_key, has_length(EmployeeDBData.DEVELOPER_KEY_LENGTH), "Invalid login method")
        elif resp.status_code == HttpResponseData.SUCCESS_CODE:
            assert_that(private_key, has_length(EmployeeDBData.PRIVATE_KEY_LENGTH), "Invalid login method")
        else:
            assert_that(resp.status_code, equal_to(HttpResponseData.UNAUTHORIZED_CODE), "Invalid login method")
            assert_that(private_key, equal_to(HttpResponseData.UNAUTHORIZED_TEXT), "Invalid login method")

    @pytest.mark.parametrize("invalid_key", [
        "key",
        "very-bad-key"
    ])
    def test_login_invalid_key(self, invalid_key, user_pwd_args, setup_api_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker

        resp = api_worker.request_login(username, password, invalid_key)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE),
                    "Invalid login method with invalid key")

    def test_login_use_public_key_once(self, user_pwd_args, setup_api_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker

        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        api_worker.request_logout(private_key)
        resp = api_worker.request_login(username, password, pub_key)
        assert_that(resp.status_code, is_not(HttpResponseData.SUCCESS_CODE),
                    "Invalid login method with double used public key")

    def test_login_use_private_key_several_times(self, user_pwd_args, setup_api_worker):
        (username, password) = user_pwd_args
        api_worker = setup_api_worker

        pub_key = api_worker.request_pubkey().text
        private_key = api_worker.request_login(username, password, pub_key).text
        api_worker.request_all_employees(private_key)
        api_worker.request_logout(private_key)
        api_worker.request_login(username, password, pub_key).text
        api_worker.request_all_employees(private_key)

    def test_get_all_employees_success(self, valid_private_key, setup_api_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker

        resp = api_worker.request_all_employees(private_key)
        resp_json_arr = resp.json()

        for json_obj in resp_json_arr:
            assert_that(json_obj, all_of(has_key(EmployeeDBData.NAME_KEY), has_key(EmployeeDBData.SURNAME_KEY),
                                         has_key(EmployeeDBData.EMAIL_KEY), has_key(EmployeeDBData.PHONE_KEY),
                                         has_key(EmployeeDBData.HIRE_DATE_KEY), has_key(EmployeeDBData.SALARY_KEY),
                                         has_key(EmployeeDBData.JOB_ID_KEY)), "Invalid get all employees")
            assert_that(resp.status_code, equal_to(HttpResponseData.SUCCESS_CODE), "Invalid get all employees")

    @pytest.mark.parametrize("invalid_key", [
        "key",
        "very-bad-key"
    ])
    def test_get_all_employees_invalid_key(self, invalid_key, setup_api_worker):
        api_worker = setup_api_worker

        resp = api_worker.request_all_employees(invalid_key)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE),
                    "Invalid get_all_employees")

    @pytest.mark.parametrize("emp", [
        Employee("Mau", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)
    ])
    def test_create_employees_accepted(self, emp, del_emp_after_test, valid_private_key, setup_api_worker,
                                       setup_db_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker

        resp = api_worker.request_create_employees(private_key, emp)
        db_worker = setup_db_worker
        selected_value = db_worker.select_row_from_table(EmployeeDBData.EMPLOYEE_TABLE_NAME,
                                                         emp.get_employee_json_without_id())
        assert_that(resp.status_code, equal_to(HttpResponseData.ACCEPTED_CODE), "Invalid create new employees")
        assert_that(selected_value, is_not(empty()), "Invalid create new employees")
        assert_that(selected_value, has_length(1), "Invalid create new employees")
        del_emp_after_test(emp)

    @pytest.mark.parametrize("emp,invalid_key", [
        (Employee("Mau", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30), "some_key")
    ])
    def test_create_employees_invalid_key(self, emp, invalid_key, del_emp_after_test, setup_api_worker):
        api_worker = setup_api_worker

        resp = api_worker.request_create_employees(invalid_key, emp)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE),
                    "Invalid create new employees")
        del_emp_after_test(emp)

    @pytest.mark.parametrize("emp,sec_emp", [
        (Employee("Mau", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "some", "7-999-777-66-77", "PU_MAN", 3000, 30))
    ])
    def test_create_employees_existing_email(self, emp, sec_emp,
                                             del_emp_after_test, valid_private_key, setup_api_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker

        sec_emp.email = emp.email
        api_worker.request_create_employees(private_key, emp)
        resp = api_worker.request_create_employees(private_key, sec_emp)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE),
                    "Invalid create new employees")
        del_emp_after_test(emp)

    @pytest.mark.parametrize("emp", [
        Employee("Mau", "Hardy", "some.mail", "7-999-777-66-77", "PU_MAN", 3000, "some"),
        Employee("Mau", "Hardy", "3mail", "7-999-777-66-77", "some", 3000, 30),
        Employee(9, "Hardy", "2mail", "7-999-777-66-77", "PU_MAN", 3000, 30),
        Employee("Mau", 10, "1mail", "7-999-777-66-77", "PU_MAN", 3000, 30),
        Employee("Mau", "Hardy", 4, "7-999-777-66-77", "PU_MAN", 3000, 30),
        Employee("Mau", "Hardy", "11mail", "some_phone", "PU_MAN", 3000, 30),
        Employee("Mau", "Hardy", "22mail", "7-999-777-66-77", "PU_MAN", "some_salary", 30),
    ])
    def test_create_employees_invalid_args(self, emp, del_emp_after_test, valid_private_key, setup_api_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker

        resp = api_worker.request_create_employees(private_key, emp)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE),
                    "Invalid create new employees with invalid args")
        del_emp_after_test(emp)

    @pytest.mark.parametrize("emp,invalid_key", [
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30), "some...key")
    ])
    def test_delete_employees_invalid_key(self, emp, create_and_del_employee, invalid_key, valid_private_key,
                                          setup_api_worker):
        valid_private_key
        api_worker = setup_api_worker
        emp_id = create_and_del_employee(emp)

        resp = api_worker.request_delete_employees(invalid_key, emp_id)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE), "Invalid delete employees")

    @pytest.mark.parametrize("emp", [
        Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)
    ])
    def test_delete_employees_employee_not_exists(self, emp, create_and_del_employee, valid_private_key,
                                                  setup_api_worker,
                                                  setup_db_worker):
        valid_private_key
        private_key = valid_private_key
        api_worker = setup_api_worker
        emp_id = create_and_del_employee(emp)

        db_worker = setup_db_worker
        db_worker.delete_from_table_with_unique(EmployeeDBData.EMPLOYEE_TABLE_NAME,
                                                EmployeeDBData.EMPLOYEE_ID_COLON_NAME, emp_id)
        resp = api_worker.request_delete_employees(private_key, emp_id)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE), "Invalid delete employees")

    @pytest.mark.parametrize("emp", [
        Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)
    ])
    def test_delete_employees_develop_user_key(self, emp, create_and_del_employee, user_dev_key, setup_api_worker,
                                               valid_private_key):
        valid_private_key
        private_key = user_dev_key
        emp_id = create_and_del_employee(emp)
        api_worker = setup_api_worker

        resp = api_worker.request_delete_employees(private_key, emp_id)
        assert_that(resp.status_code, equal_to(HttpResponseData.UNAUTHORIZED_CODE), "Invalid delete employees")

    @pytest.mark.parametrize("emp,sec_emp,invalid_key", [
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Hell", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30), "some_key"),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Motor", "ma88@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30), "some_key"),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "targ@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30), "some_key"),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8888@mail.ru", "7-999-333-00-00", "PU_MAN", 3000, 30), "some_key"),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888@mail.ru", "7-999-777-66-77", "FI_MGR", 3000, 30), "some_key"),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888888@mail.ru", "7-999-777-66-77", "PU_MAN", 5000, 30), "some_key"),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 10), "some_key")
    ])
    def test_update_employees_invalid_key(self, emp, sec_emp, create_and_del_employee, invalid_key,
                                          valid_private_key, setup_api_worker):
        valid_private_key
        api_worker = setup_api_worker
        emp_id = create_and_del_employee(emp)

        resp = api_worker.request_update_employees(invalid_key, sec_emp, emp_id)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE), "Invalid update employees")

    @pytest.mark.parametrize("emp,sec_emp", [
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Hell", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Motor", "ma88@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "targ@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8888@mail.ru", "7-999-333-00-00", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888@mail.ru", "7-999-777-66-77", "FI_MGR", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888888@mail.ru", "7-999-777-66-77", "PU_MAN", 5000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 10))
    ])
    def test_update_employees_employee_not_exists(self, emp, sec_emp, create_and_del_employee,
                                                  valid_private_key, setup_api_worker,
                                                  setup_db_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker
        emp_id = create_and_del_employee(emp)

        db_worker = setup_db_worker
        db_worker.delete_from_table_with_unique(EmployeeDBData.EMPLOYEE_TABLE_NAME,
                                                EmployeeDBData.EMPLOYEE_ID_COLON_NAME, emp_id)
        resp = api_worker.request_update_employees(private_key, sec_emp, emp_id)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE), "Invalid update employees")

    @pytest.mark.parametrize("emp,sec_emp", [
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Hell", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Motor", "ma88@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "targ@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8888@mail.ru", "7-999-333-00-00", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888@mail.ru", "7-999-777-66-77", "FI_MGR", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888888@mail.ru", "7-999-777-66-77", "PU_MAN", 5000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 10))
    ])
    def test_update_employees_success(self, emp, sec_emp, create_and_del_employee, valid_private_key,
                                      setup_api_worker, setup_db_worker):
        private_key = valid_private_key
        emp_id = create_and_del_employee(emp)
        api_worker = setup_api_worker

        resp = api_worker.request_update_employees(private_key, sec_emp, emp_id)
        db_worker = setup_db_worker
        selected_value = db_worker.select_row_from_table(EmployeeDBData.EMPLOYEE_TABLE_NAME,
                                                         sec_emp.get_employee_json_without_id())
        assert_that(resp.status_code, equal_to(HttpResponseData.ACCEPTED_CODE), "Invalid update new employees")
        assert_that(selected_value, is_not(empty()), "Invalid update new employees")
        assert_that(selected_value, has_length(1), "Invalid update new employees")

    @pytest.mark.parametrize("emp,sec_emp", [
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Hell", "Hardy", "ma888@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Motor", "ma88@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "targ@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8888@mail.ru", "7-999-333-00-00", "PU_MAN", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888@mail.ru", "7-999-777-66-77", "FI_MGR", 3000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma88888888@mail.ru", "7-999-777-66-77", "PU_MAN", 5000, 30)),
        (Employee("Mau", "Hardy", "ma808@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 30),
         Employee("Mau", "Hardy", "ma8@mail.ru", "7-999-777-66-77", "PU_MAN", 3000, 10))
    ])
    def test_update_employees_develop_user_key(self, emp, sec_emp, create_and_del_employee, user_key, setup_api_worker):
        private_key = user_key
        emp_id = create_and_del_employee(emp)
        api_worker = setup_api_worker

        resp = api_worker.request_update_employees(private_key, sec_emp, emp_id)
        assert_that(resp.status_code, equal_to(HttpResponseData.UNAUTHORIZED_CODE), "Invalid update employees")

    def test_get_employee_history_success(self, valid_private_key, setup_api_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker

        resp = api_worker.request_get_employees_history(private_key)
        resp_json_arr = resp.json()
        for json_obj in resp_json_arr:
            assert_that(json_obj, all_of(has_key(EmployeeDBData.DATE_KEY), has_key(EmployeeDBData.DEP_ID_KEY),
                                         has_key(EmployeeDBData.JOB_ID_KEY), has_key(EmployeeDBData.ID_KEY),
                                         has_key(EmployeeDBData.START_DATE_KEY)))
            assert_that(resp.status_code, equal_to(HttpResponseData.SUCCESS_CODE), "Invalid get employee history")

    def test_get_employee_history_user_key(self, user_key, setup_api_worker):
        private_key = user_key
        api_worker = setup_api_worker

        resp = api_worker.request_get_employees_history(private_key)
        assert_that(resp.status_code, equal_to(HttpResponseData.UNAUTHORIZED_CODE), "Invalid get employee history")

    def test_logout_success(self, valid_private_key, setup_api_worker):
        private_key = valid_private_key
        api_worker = setup_api_worker

        resp = api_worker.request_logout(private_key)
        assert_that(resp.status_code, equal_to(HttpResponseData.SUCCESS_CODE), "Invalid logout method")

    @pytest.mark.parametrize("invalid_key", [
        "key",
        "very-bad-key"
    ])
    def test_logout_invalid_key(self, valid_private_key, invalid_key, setup_api_worker):
        valid_private_key
        api_worker = setup_api_worker

        resp = api_worker.request_logout(invalid_key)
        assert_that(resp.status_code, equal_to(HttpResponseData.INTERVAL_SERVER_ERROR_CODE), "Invalid logout method")
