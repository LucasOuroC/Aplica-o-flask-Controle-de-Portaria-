from flask import Flask, render_template, request, redirect, flash, session, jsonify, url_for
from functools import wraps
from datetime import datetime
import mysql.connector
from mysql.connector import Error


app = Flask(__name__)
app.secret_key = 'mercante'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            database='BDPROJECT',
            user='root',
            password='Lusc@031020'
        )
        if connection.is_connected():
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
        values = (dado['nome'], dado['data'], dado['horaE'], dado['veic'], dado['cor'], dado['placa'], dado['visit'],
                  dado['tipo_visitante'], dado['rg'], dado['empresa'], dado['horaS'], dado['setor'], dado['obs'])
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nome' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'error')
            return redirect(url_for('login', next=request.url))
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
            if usuario['nome'] == nome and usuario['senha'] == senha:
                session['nome'] = nome
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
        data = datetime.strptime(data, '%Y-%m-%d').strftime('%d-%m-%Y')
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
            'data': data,
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
        dados = carregar_dados()  # Recarregar os dados para atualizar a tabela

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
            values = (dados_atualizados['nome'], dados_atualizados['data'], dados_atualizados['horaE'],
                      dados_atualizados['veic'], dados_atualizados['cor'], dados_atualizados['placa'],
                      dados_atualizados['visit'], dados_atualizados['tipo_visitante'], dados_atualizados['rg'],
                      dados_atualizados['empresa'], dados_atualizados['horaS'], dados_atualizados['setor'],
                      dados_atualizados['obs'], dados_atualizados['cod'])
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'message': 'Dados atualizados com sucesso!'})

        return jsonify({'message': 'Erro: Não foi possível atualizar os dados.'}), 400

    return jsonify({'message': 'Método não permitido.'}), 405


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
