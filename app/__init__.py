from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)
bootstrap = Bootstrap(app)
mysql = MySQL(app)
app.secret_key = 'batatadoce'

from app.controllers.perfils import app



