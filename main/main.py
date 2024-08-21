from flask import Flask, render_template, request, redirect, flash, session, jsonify,url_for, make_response
from functools import wraps
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.before_request
def ensure_session_access():
    session.modified = True

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.private = True
    return response

app.config['SESSION_REFRESH_EACH_REQUEST'] = False

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False #Alternar para true em Prod
)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host= os.getenv("DB_HOST"),
            port= os.getenv("DB_PORT"),
            database= os.getenv("DB_NAME"),
            user= os.getenv("DB_USER"),
            password= os.getenv("DB_PASSWORD")
        )
        if connection.is_connected():
            print("Conexão ao MySQL estabelecida com sucesso!")
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def carregar_usuario():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        connection.close()
        print(f"Usuários carregados: {usuarios}")  
        return usuarios
    return []

def carregar_dados():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM dados ORDER BY data DESC")
        dados = cursor.fetchall()
        cursor.close()
        connection.close()
        for d in dados:
            d['cod'] = int(d['cod'])
        return dados
    return []

def salvar_dados(dado):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        query = """INSERT INTO dados (nome, data, horaE, veic, cor, placa, visit, tipo_visitante, rg, empresa, horaS, setor, obs)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (
            dado['nome'],
            dado['data'],           
            dado['horaE'],          
            dado['veic'],
            dado['cor'],
            dado['placa'],
            dado['visit'],
            dado['tipo_visitante'],
            dado['rg'],
            dado['empresa'],
            dado['horaS'],          
            dado['setor'],
            dado['obs']
        )

        print("Consulta SQL:", query)
        print("Valores:", values)

        try:
            cursor.execute(query, values)
            connection.commit()
        except Error as e:
            print(f"Erro ao executar a consulta: {e}")
        finally:
            cursor.close()
            connection.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nome' not in session:
            print("Usuário não está na sessão, redirecionando para login.")
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login', next=request.url))
        print("Usuário está na sessão.")
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('nome', None)
    return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        nome = request.form.get('nome')
        senha = request.form.get('senha')

        usuarios = carregar_usuario()

        for usuario in usuarios:
            print(f"Verificando usuário: {usuario}")  
            if usuario['nome'].strip().lower() == nome.strip().lower() and usuario['senha'] == senha:
                session['nome'] = nome
                #print(f"sessao criada {nome}")
                return redirect('/home')

        else:
            flash("Credenciais incorretas!! Verifique novamente")
            return redirect('/')
    return redirect('/')

@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    if 'nome' not in session:
        return redirect('/')

    nome = session['nome']
    dados = carregar_dados()

    if request.method == 'POST':
        data = request.form.get('data')  
        try:
            data_formatada = datetime.strptime(data, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            flash('Formato de data inválido.')
            return redirect('/home')

        horaE = request.form.get('horaE')
        veic = request.form.get('veic')
        cor = request.form.get('cor')
        plac = request.form.get('placa')
        visit = request.form.get('visit')
        tipo_visitante = request.form.get('check')
        rg = request.form.get('Rg')
        empre = request.form.get('empresa')
        horaS = request.form.get('horaS')
        setor = request.form.get('setor')
        obs = request.form.get('obs')

        if rg == '':
            rg = None

        codigo = int(max([d['cod'] for d in dados], default=0)) + 1
        newD = {
            'cod': codigo,
            'nome': nome,
            'data': data_formatada,  
            'horaE': horaE,
            'veic': veic,
            'cor': cor,
            'placa': plac,
            'visit': visit,
            'tipo_visitante': tipo_visitante,
            'rg': rg,
            'empresa': empre,
            'horaS': horaS,
            'setor': setor,
            'obs': obs,
        }

        salvar_dados(newD)
        dados = carregar_dados()  

    return render_template('home.html', dados=dados)



@app.route('/relatorio')
@login_required
def relatorio():
    dados = carregar_dados()
    return render_template('relatorio.html', dados=dados)

@app.route('/atualizar_dados', methods=['POST'])
@login_required
def atualizar_dados():
    if request.method == 'POST':
        dados_atualizados = request.get_json()

        if not dados_atualizados:
            return jsonify({'message': 'Nenhum dado enviado.'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = """UPDATE dados SET nome = %s, data = %s, horaE = %s, veic = %s, cor = %s, placa = %s, visit = %s,
                       tipo_visitante = %s, rg = %s, empresa = %s, horaS = %s, setor = %s, obs = %s
                       WHERE cod = %s"""
            values = (
                dados_atualizados.get('nome'),
                dados_atualizados.get('data'),
                dados_atualizados.get('horaE'),
                dados_atualizados.get('veic'),
                dados_atualizados.get('cor', None),  # Aqui usamos get com um valor padrão None
                dados_atualizados.get('placa'),
                dados_atualizados.get('visit'),
                dados_atualizados.get('tipo_visitante'),
                dados_atualizados.get('rg'),
                dados_atualizados.get('empresa'),
                dados_atualizados.get('horaS'),
                dados_atualizados.get('setor'),
                dados_atualizados.get('obs'),
                dados_atualizados.get('cod')
            )
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'message': 'Dados atualizados com sucesso!'})

        return jsonify({'message': 'Erro: Não foi possível atualizar os dados.'}), 400

    return jsonify({'message': 'Método não permitido.'}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
