from datetime import date


class Employee(object):
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
            "first_name": self.name,
            "last_name": self.surname,
            "email": self.email,
            "phone_number": self.phone,
            "job_id": self.job,
            "salary": self.salary,
            "department_id": self.dep_id
        }

    def get_employee_json_with_id(self, emp_id):
        return {
            "employee_id": emp_id,
            "first_name": self.name,
            "last_name": self.surname,
            "email": self.email,
            "phone_number": self.phone,
            "hire_date": date.today(),
            "job_id": self.job,
            "salary": self.salary,
            "department_id": self.dep_id
        }

    def get_employee_data_array(self):
        return [self.name, self.surname, self.email, self.phone, self.job, self.salary, self.dep_id]
