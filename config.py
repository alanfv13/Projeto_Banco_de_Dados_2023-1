from flask_mysqldb import MySQL
import os
import mysql.connector


cnx = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'avaliaunb'
)

cursor = cnx.cursor()
