from app import app
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from app.controllers.estudante import cadastrar_estudante, verificar_credenciais, login_required
from mysql.connector import Error
import MySQLdb


mysql = MySQL(app)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'avaliaunb',
    'port': 3306
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        try:
            matricula = request.form.get('matricula')
            nome = request.form.get('nome')
            email = request.form.get('email')
            curso = request.form.get('curso')
            senha = request.form.get('senha')
            administrador = False
            imagem = request.files.get('imagem')

            if not nome.strip():
                raise ValueError('Nome não fornecido')
            if not email.strip():
                raise ValueError('Email não fornecido')
            if not curso.strip():
                raise ValueError('Curso não fornecido')
            if not senha.strip():
                raise ValueError('Senha não fornecida')
            if matricula is None:
                raise ValueError('Matrícula não fornecida')
            if imagem and imagem.filename == '':
                raise ValueError('Nenhum arquivo selecionado')
            cadastrar_estudante(matricula, nome, email, curso, senha, administrador, imagem)
            return 'Estudante cadastrado com sucesso!', 200
        except KeyError:
            return f'Erro ao cadastrar o estudante: Campos obrigatórios não fornecidos. Dados recebidos: {str(request.form)}', 400

        except ValueError as e:
            return f'Erro ao cadastrar o estudante: {str(e)}. Dados recebidos: {str(request.form)}', 400

        except Exception as e:
            return f'Erro ao cadastrar o estudante: {str(e)}. Dados recebidos: {str(request.form)}', 500
    return render_template('cadastro.html')


def obter_matricula_por_email(email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Executa a consulta SQL para obter a matrícula do usuário pelo email
        query = "SELECT matricula FROM Estudantes WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        conn.close()
            # Retorna a matrícula se encontrada, caso contrário retorna None
        if result:
            return result[0]
        else:
            return None
    except Error as error:
        print(f"Erro ao conectar ao MySQL: {error}")
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')

        if verificar_credenciais(email, senha):
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais incorretas. Tente novamente.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Lógica para fazer o logout do usuário
    session.clear()  # Limpa a sessão
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Acesso permitido apenas para usuários logados
    return render_template('dashboard.html')


@app.route('/excluir_conta')
@login_required
def excluir_conta():
    try:
        # Obtém o ID do usuário da sessão
        user_id = session['user_id']

        # Conecta ao banco de dados
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Executa a consulta SQL para excluir a conta do usuário
        query = "DELETE FROM Estudantes WHERE id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()

        # Fecha a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Limpa a sessão e redireciona para a página de login
        session.clear()
        flash('Sua conta foi excluída com sucesso.', 'success')
        return redirect(url_for('login'))

    except Error as error:
        flash('Erro ao excluir a conta. Por favor, tente novamente.', 'error')
        return redirect(url_for('dashboard'))
    
def obter_dados_estudante(email):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Executa a consulta SQL para obter a matrícula do usuário pelo email
        query = "SELECT matricula FROM Estudantes WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        # Fecha a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Retorna a matrícula se encontrada, caso contrário retorna None
        if result:
            return result[0]
        else:
            return None
    except Error as error:
        print(f"Erro ao conectar ao MySQL: {error}")
        return None



def modificar_dados_estudante(matricula, nome, email, curso):
    try:
        connection = mysql.connector.connect(**db_config)
        query = "UPDATE Estudantes SET nome = %s, email = %s, curso = %s WHERE matricula = %s"
        values = (nome, email, curso, matricula)
        cursor = connection.cursor()
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return False

@app.route('/editar_conta', methods=['GET', 'POST'])
@login_required
def editar_conta():
    matricula = session['user_matricula']
    estudante = obter_dados_estudante(matricula)

    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        curso = request.form.get('curso')

        if modificar_dados_estudante(matricula, nome, email, curso):
            flash('Dados da conta modificados com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Erro ao modificar os dados da conta.', 'error')

    return render_template('editar_conta.html', estudante=estudante)
