#
# dsn = cx_Oracle.makedsn("localhost", 1521, service_name="xe")
# conn = cx_Oracle.connect(user="HR", password="qwaszx12", dsn=dsn)
# print("Kek")
# print(conn.version)
# conn.close()
from datetime import datetime

import cx_Oracle


# import psycopg2


class DBWork(object):
    # def __init__(self, user, password, host, port, db):
    #     self._conn = psycopg2.connect(user=user, password=password, host=host, port=port, database=db)

    def __init__(self, user, password, host, port, db):
        dsn = cx_Oracle.makedsn(host, port, service_name=db)
        self._conn = cx_Oracle.connect(user=user, password=password, dsn=dsn)

    def __enter__(self):
        return self

    def close_conn(self):
        self._conn.close()

    def select_all_from_table(self, table_name):
        cur = self._conn.cursor()
        cur.execute("select * from %s" % table_name)
        res = self.get_result_from_cursor(cur)
        cur.close()
        return res

    def select_row_from_table(self, table_name, to_select_dict):
        cur = self._conn.cursor()
        select_query = "select * from %s where " % table_name
        counter = 0
        for i in to_select_dict:
            value = to_select_dict[i]
            select_query += "%s = %s" % (i, self._escape(value))
            if counter != len(to_select_dict) - 1:
                select_query += " and "
            counter += 1
        cur.execute(select_query)
        res = DBWork.get_result_from_cursor(cur)
        cur.close()
        return res

    def select_single_value_from_table(self, table_name, colon_name, to_select_dict):
        cur = self._conn.cursor()
        select_query = "select %s from %s where " % (colon_name, table_name)
        counter = 0
        for i in to_select_dict:
            value = to_select_dict[i]
            select_query += "%s = %s" % (i, self._escape(value))
            if counter != len(to_select_dict) - 1:
                select_query += " and "
            counter += 1
        cur.execute(select_query)
        print(cur.fetchall())
        res = cur.fetchall()[0][0]
        cur.close()
        return res

    def select_single_colon_from_table(self, table_name, single_colon_name):
        cur = self._conn.cursor()
        select_query = "select %s from %s" % (single_colon_name, table_name)
        cur.execute(select_query)
        res = DBWork.get_result_from_cursor(cur)
        cur.close()
        return res

    def delete_from_table(self, table_name, to_delete_dict):
        cur = self._conn.cursor()
        delete_query = "delete from %s where " % table_name
        counter = 0
        for i in to_delete_dict:
            value = to_delete_dict[i]
            delete_query += "%s = %s" % (i, self._escape(value))
            if counter != len(to_delete_dict) - 1:
                delete_query += " and "
            counter += 1
        cur.execute(delete_query)
        rowcount = cur.rowcount
        self._conn.commit()
        cur.close()
        return rowcount

    def delete_from_table_with_unique(self, table_name, to_delete_unique_colon, to_delete_unique_val, ):
        cur = self._conn.cursor()
        delete_query = "delete from %s where %s = '%s'" % (table_name, to_delete_unique_colon, to_delete_unique_val)
        cur.execute(delete_query)
        rowcount = cur.rowcount
        self._conn.commit()
        cur.close()
        return rowcount

    @staticmethod
    def _escape(data):
        if type(data) is str:
            return "'%s'" % data
        elif type(data) is datetime:
            return "'%s'" % data.isofomat()
        else:
            return "%d" % data

    def insert_into_table(self, table_name, to_insert_dict):
        cur = self._conn.cursor()
        insert_query = "insert into %s (%s) " % (table_name, ', '.join(to_insert_dict.keys()))
        cont = []
        for i in to_insert_dict:
            value = to_insert_dict[i]
            cont.append(self._escape(value))
        insert_query += "values(%s)" % ', '.join(cont)
        cur.execute(insert_query)
        rowcount = cur.rowcount
        self._conn.commit()
        cur.close()
        return rowcount

    @staticmethod
    def get_result_from_cursor(cur):
        all_rows_content = cur.fetchall()
        description = cur.description
        res = []
        for row in all_rows_content:
            table_str = dict()
            for i in range(len(description)):
                # print(description[i][0])
                # table_str.update({description[i].name: row[i]})
                table_str.update({description[i][0]: row[i]})
            res.append(table_str)
        return res


# with DBWork("hr", "qwaszx12", "localhost", 5432, "hr_db") as dbw:


# #with DBWork("HR", "qwaszx12", "localhost", 1521, "xe") as dbw:
#     d = dbw.select_all_from_table('employees')
#     #dbw.insert_into_table('countries', {'country_id': 'OO', 'country_name': 'YYYY', 'region_id': 1})
#     dbw.select_row_from_table('countries', {'country_id': 'OO', 'country_name': 'YYYY', 'region_id': 1})
#     dbw.delete_from_table('employees', {"first_name": "Luis",
#                                         "last_name": "Hardy",
#                                         "email": "someeee@mail.ru",
#                                         "phone_number": "7-999-777-66-77",
#                                         "job_id": "PU_MAN",
#                                         "salary": 3000,
#                                         "department_id": 30})
#     print(d)
#     f = dbw.select_all_from_table('employees')
#     print(f)

dbw = DBWork("HR", "qwaszx12", "localhost", 1521, "xe")
# #dbw.delete_from_table_with_unique("employees", "email", "some@mail.ru")
# dbw.delete_from_table_with_unique("job_history", "EMPLOYEE_ID", "431")
# dbw.delete_from_table_with_unique("employees", "EMPLOYEE_ID", "431")
# print(dbw.select_all_from_table('job_history'))
print(dbw.select_all_from_table('employees'))
