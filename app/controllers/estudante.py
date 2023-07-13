from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from functools import wraps

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'avaliaunb',
    'port': 3306
}

def obter_ultima_matricula():
    try:
        connection = mysql.connector.connect(**db_config)
        query = "SELECT MAX(matricula) FROM Estudantes"
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result[0] is not None else 0
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")

def cadastrar_estudante(matricula, nome, email, curso, senha, admin, imagem ):
    try:
        connection = mysql.connector.connect(**db_config)
        query = "INSERT INTO Estudantes (matricula, nome, email, curso, senha, admin, imagem) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        imagem_bytes = imagem.read() if imagem else None
        values = (matricula, nome, email, curso, senha, admin, imagem_bytes)
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        print("Estudante cadastrado com sucesso!")
        print(f"Matrícula do estudante: {matricula}")
        return render_template('login.html') 
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")

def verificar_credenciais(email, senha):
    try:
        # Conecta ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Executa a consulta SQL para obter as informações do estudante
        query = "SELECT admin FROM estudantes WHERE email = %s AND senha = %s"
        cursor.execute(query, (email, senha))
        result = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Verifica se as credenciais estão corretas e retorna True ou False
        if result and result[0] == 1:
            return True  # Estudante é um administrador
        else:
            return False  # Estudante não é um administrador

    except mysql.connector.Error as error:
        print("Erro ao conectar ao banco de dados:", error)
        return False
    
# Decorator para verificar se o usuário está logado
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
    return decorated_function

def verificar_credenciais(email, senha):
    try:
        # Conecta ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Executa a consulta SQL para obter as informações do estudante
        query = "SELECT * FROM Estudantes WHERE email = %s AND senha = %s"
        cursor.execute(query, (email, senha))
        result = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Verifica se as credenciais estão corretas e retorna True ou False
        if result:
            # Credenciais corretas, armazena as informações do usuário na sessão
            session['logged_in'] = True
            session['user_id'] = result[0]
            session['user_email'] = result[2]
            return True
        else:
            # Credenciais incorretas
            return False

    except mysql.connector.Error as error:
        print("Erro ao conectar ao banco de dados:", error)
        return False

