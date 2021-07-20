import os, pymysql

connection = pymysql.connect(host=os.environ['RDS_HOSTNAME'], user=os.environ['RDS_USERNAME'], password=os.environ['RDS_PASSWORD'],
                             db='', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
connection.cursor().execute('create database autobankdb')