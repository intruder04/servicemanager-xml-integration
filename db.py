import pymysql
import pymysql.cursors
from config_file import *

def makeQuery(type,query):
    try:
        # Connect to the database
        connection = pymysql.connect(host=mysql_ip,port=mysql_port,user=mysql_user,password=mysql_password,db=mysql_dbname,charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        if (type=='insert' or type=='update'):
            with connection.cursor() as cursor:
                sql = query
                cursor.execute(sql)
            connection.commit()
        if (type=='select'):
            with connection.cursor() as cursor:
                sql = query
                cursor.execute(sql)
                result = cursor.fetchone()
                return result
                # print(result)
    finally:
        connection.close()

