import pytest

from project.api import APIWork
from .employee_db_data_class import EmployeeDBData
from ..utils.db_work import DBWork


@pytest.fixture(scope="class", params=[
    ("localhost", 8081, "worst-api")
])
def setup_api_worker(request):
    (host, port, prefix) = request.param
    return APIWork(host, port, prefix)


@pytest.fixture(scope="class", params=[
    ("HR", "qwaszx12", "localhost", 1521, "xe")
])
def setup_db_worker(request):
    (user, password, host, port, db) = request.param
    db_worker = DBWork(user, password, host, port, db)
    yield db_worker
    db_worker.close_conn()


@pytest.fixture(scope="function")
def valid_private_key(user_pwd_args, setup_api_worker):
    return get_key(user_pwd_args, setup_api_worker)


@pytest.fixture(scope="function", params=[
    ("admin", "admin"),
    ("developer", "developer")
])
def user_pwd_args(request):
    return request.param


@pytest.fixture(scope="function", params=[
    ("user", "user"),
    ("developer", "developer")
])
def user_dev_key(request, setup_api_worker):
    return get_key(request.param, setup_api_worker)


@pytest.fixture(scope="function", params=[
    ("user", "user")
])
def user_key(request, setup_api_worker):
    return get_key(request.param, setup_api_worker)


def get_key(fixt, setup_api_worker):
    (username, password) = fixt
    api_worker = setup_api_worker

    pub_key = api_worker.request_pubkey().text
    private_key = api_worker.request_login(username, password, pub_key).text
    return private_key


@pytest.fixture(scope="function")
def del_emp_after_test(setup_db_worker):
    emp_to_del = []

    def save(emp):
        emp_to_del.append(emp)

    yield save
    db_worker = setup_db_worker
    for em in emp_to_del:
        db_worker.delete_from_table(EmployeeDBData.EMPLOYEE_TABLE_NAME, em.get_employee_json_without_id())


@pytest.fixture(scope="function")
def create_and_del_employee(setup_db_worker):
    emps_to_del = []
    db_worker = setup_db_worker

    def create_empl(emp):
        empl_id = db_worker.select_sequence_element("employees_seq")
        db_worker.insert_into_table(EmployeeDBData.EMPLOYEE_TABLE_NAME, emp.get_employee_json_with_id(empl_id))
        emps_to_del.append(empl_id)
        return empl_id

    yield create_empl
    for emp_id in emps_to_del:
        db_worker.delete_from_table_with_unique(EmployeeDBData.JOB_HISTORY_TABLE_NAME,
                                                EmployeeDBData.EMPLOYEE_ID_COLON_NAME, emp_id)
        db_worker.delete_from_table_with_unique(EmployeeDBData.EMPLOYEE_TABLE_NAME,
                                                EmployeeDBData.EMPLOYEE_ID_COLON_NAME, emp_id)
