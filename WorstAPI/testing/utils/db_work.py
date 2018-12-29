
from datetime import date

import cx_Oracle


class DBWork(object):
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

    def select_row_with_unique_value(self, table_name, unique_value_name, unique_value_value):
        cur = self._conn.cursor()
        select_query = "select * from %s where %s = %s" % (table_name, unique_value_name,
                                                           self._escape(unique_value_value))
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

    def select_sequence_element(self, seq_name):
        cur = self._conn.cursor()
        select_query = "select %s.nextval from dual" % seq_name
        cur.execute(select_query)
        res = cur.fetchall()[0][0]
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
        elif type(data) is date:
            return "DATE '%s'" % data.isoformat()
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
                table_str.update({description[i][0]: row[i]})
            res.append(table_str)
        return res


