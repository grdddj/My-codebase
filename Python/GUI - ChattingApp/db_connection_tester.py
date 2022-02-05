import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host="89.221.219.124", database="chat", user="user", password="password"
    )
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL database... MySQL Server version on ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("Your connected to - ", record)
except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    # closing database connection.
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
