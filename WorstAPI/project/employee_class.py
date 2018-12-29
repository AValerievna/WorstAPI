from datetime import date


class Employee(object):
    HIRE_DATE_FIELD = "hire_date"
    EMPLOYEE_ID_FIELD = "employee_id"
    DEPARTMENT_ID_FIELD = "department_id"
    SALARY_FIELD = "salary"
    JOB_ID_FIELD = "job_id"
    PHONE_NUMBER_FIELD = "phone_number"
    EMAIL_FIELD = "email"
    LAST_NAME_FIELD = "last_name"
    FIRST_NAME_FIELD = "first_name"

    def __init__(self, name, surname, email, phone, job, salary, dep_id):
        self.name = name
        self.surname = surname
        self.email = email
        self.phone = phone
        self.job = job
        self.salary = salary
        self.dep_id = dep_id

    def get_employee_json_without_id(self):
        return {
            self.FIRST_NAME_FIELD: self.name,
            self.LAST_NAME_FIELD: self.surname,
            self.EMAIL_FIELD: self.email,
            self.PHONE_NUMBER_FIELD: self.phone,
            self.JOB_ID_FIELD: self.job,
            self.SALARY_FIELD: self.salary,
            self.DEPARTMENT_ID_FIELD: self.dep_id
        }

    def get_employee_json_with_id(self, emp_id):
        return {
            self.EMPLOYEE_ID_FIELD: emp_id,
            self.FIRST_NAME_FIELD: self.name,
            self.LAST_NAME_FIELD: self.surname,
            self.EMAIL_FIELD: self.email,
            self.PHONE_NUMBER_FIELD: self.phone,
            self.HIRE_DATE_FIELD: date.today(),
            self.JOB_ID_FIELD: self.job,
            self.SALARY_FIELD: self.salary,
            self.DEPARTMENT_ID_FIELD: self.dep_id
        }

    def get_employee_data_array(self):
        return [self.name, self.surname, self.email, self.phone, self.job, self.salary, self.dep_id]
