import cx_Oracle

dsn = cx_Oracle.makedsn("localhost", 1521, service_name="xe")
conn = cx_Oracle.connect(user="HR", password="qwaszx12", dsn=dsn)
print("Kek")
print(conn.version)
conn.close()
