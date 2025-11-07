from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_mail import Mail, Message
from dotenv import load_dotenv
import sqlite3
import os
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Configurar logging para debugging
logging.basicConfig(level=logging.DEBUG)

# -----------------------------
# Carregar variáveis de ambiente (.env)
# -----------------------------
load_dotenv()

# -----------------------------
# Inicialização da Aplicação
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Configurações do Flask
# -----------------------------
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# -----------------------------
# Configuração de E-mail (via .env)
# -----------------------------
app.config['MAIL_SERVER'] = os.getenv('EMAIL_HOST')
app.config['MAIL_PORT'] = int(os.getenv('EMAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_HOST_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_HOST_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = (
    os.getenv('MAIL_DEFAULT_NAME', 'Suporte'),
    os.getenv('EMAIL_HOST_USER')
)

mail = Mail(app)

# -----------------------------
# Banco de Dados
# -----------------------------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            tipo_sanguineo TEXT,
            data_nascimento TEXT,
            genero TEXT,
            cep TEXT,
            endereco TEXT,
            ja_doou TEXT,
            primeira_vez TEXT,
            interesse TEXT,
            autoriza_msg INTEGER,
            autoriza_dados INTEGER,
            pontos INTEGER DEFAULT 0,
            senha TEXT
        )
    ''')

    c.execute("PRAGMA table_info(usuarios)")
    columns = [col[1] for col in c.fetchall()]
    if 'senha' not in columns:
        c.execute('ALTER TABLE usuarios ADD COLUMN senha TEXT')

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Função Genérica para Envio de E-mail
# -----------------------------
def enviar_email(para, assunto, mensagem):
    try:
        msg = Message(subject=assunto, recipients=[para], body=mensagem)
        mail.send(msg)
        return {'status': 'sucesso', 'mensagem': 'E-mail enviado com sucesso!'}
    except Exception as e:
        return {'status': 'erro', 'mensagem': str(e)}

# -----------------------------
# Rotas
# -----------------------------
@app.route('/')
def index():
    cookie_usuario_id = request.cookies.get('usuario_id')
    login_time = request.cookies.get('login_time')
    logged_in = False
    if cookie_usuario_id and login_time:
        try:
            login_time_dt = datetime.fromisoformat(login_time)
            if datetime.utcnow() - login_time_dt <= timedelta(days=4):
                logged_in = True
        except (ValueError, TypeError):
            pass
    return render_template('index.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')
        if not email or not senha:
            logging.error("Email ou senha não fornecidos")
            return render_template('login.html', error="Por favor, preencha todos os campos.", logged_in=False)
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario = c.fetchone()
        conn.close()
        if not usuario:
            logging.error(f"Usuário com email {email} não encontrado")
            return render_template('login.html', error="Email ou senha inválidos", logged_in=False)
        if check_password_hash(usuario['senha'], senha):
            response = make_response(redirect(url_for('perfil')))
            response.set_cookie('usuario_id', str(usuario['id']), max_age=3*24*60*60)
            response.set_cookie('login_time', datetime.utcnow().isoformat(), max_age=3*24*60*60)
            logging.debug(f"Login bem-sucedido para usuário ID: {usuario['id']}")
            return response
        else:
            logging.error(f"Senha inválida para email {email}")
            return render_template('login.html', error="Email ou senha inválidos", logged_in=False)
    return render_template('login.html', logged_in=False)

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('usuario_id')
    response.delete_cookie('login_time')
    logging.debug("Usuário deslogado, cookies removidos")
    return response

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', logged_in=False)

@app.route('/campanhas')
def campanhas():
    cookie_usuario_id = request.cookies.get('usuario_id')
    login_time = request.cookies.get('login_time')
    logged_in = False
    if cookie_usuario_id and login_time:
        try:
            login_time_dt = datetime.fromisoformat(login_time)
            if datetime.utcnow() - login_time_dt <= timedelta(days=4):
                logged_in = True
        except (ValueError, TypeError):
            pass
    return render_template('campanhas.html', logged_in=logged_in)

@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html', logged_in=False)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    logging.debug(f"Dados recebidos do formulário: {data}")
    senha_hash = generate_password_hash(data.get('senha'))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO usuarios (
            nome, email, telefone, tipo_sanguineo, data_nascimento, genero,
            cep, endereco, ja_doou, primeira_vez, interesse,
            autoriza_msg, autoriza_dados, pontos, senha
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
    ''', (
        data.get('nome'), data.get('email'), data.get('telefone'),
        data.get('tipo_sanguineo'), data.get('data_nascimento'),
        data.get('genero'), data.get('cep'), data.get('endereco'),
        data.get('ja_doou'), data.get('primeira_vez'), data.get('interesse'),
        1 if data.get('autoriza_msg') == 'sim' else 0,
        1 if data.get('autoriza_dados') == 'sim' else 0,
        senha_hash
    ))
    conn.commit()
    user_id = c.lastrowid
    conn.close()
    response = make_response(redirect(url_for('perfil')))
    response.set_cookie('usuario_id', str(user_id), max_age=3*24*60*60)
    response.set_cookie('login_time', datetime.utcnow().isoformat(), max_age=3*24*60*60)
    logging.debug(f"Usuário cadastrado com ID: {user_id}")
    return response

@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    cookie_usuario_id = request.cookies.get('usuario_id')
    if not cookie_usuario_id:
        logging.debug("Nenhum cookie de usuário encontrado, redirecionando para login")
        return redirect(url_for('login'))
    
    data = request.form.to_dict()
    user_id = int(cookie_usuario_id)
    
    required_fields = ['nome', 'email', 'telefone', 'tipo_sanguineo', 'data_nascimento', 'genero', 'cep', 'endereco', 'ja_doou', 'interesse']
    for field in required_fields:
        if not data.get(field):
            logging.error(f"Campo obrigatório ausente: {field}")
            return render_template('perfil.html', error="Por favor, preencha todos os campos obrigatórios.", logged_in=True)
    
    senha = data.get('senha')
    senha_hash = generate_password_hash(senha) if senha else None
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if senha:
        c.execute('''
            UPDATE usuarios SET
                nome = ?, email = ?, telefone = ?, tipo_sanguineo = ?, data_nascimento = ?,
                genero = ?, cep = ?, endereco = ?, ja_doou = ?, primeira_vez = ?,
                interesse = ?, autoriza_msg = ?, autoriza_dados = ?, senha = ?
            WHERE id = ?
        ''', (
            data.get('nome'), data.get('email'), data.get('telefone'),
            data.get('tipo_sanguineo'), data.get('data_nascimento'), data.get('genero'),
            data.get('cep'), data.get('endereco'), data.get('ja_doou'), data.get('primeira_vez'),
            data.get('interesse'), 1 if data.get('autoriza_msg') == 'sim' else 0,
            1 if data.get('autoriza_dados') == 'sim' else 0, senha_hash, user_id
        ))
    else:
        c.execute('''
            UPDATE usuarios SET
                nome = ?, email = ?, telefone = ?, tipo_sanguineo = ?, data_nascimento = ?,
                genero = ?, cep = ?, endereco = ?, ja_doou = ?, primeira_vez = ?,
                interesse = ?, autoriza_msg = ?, autoriza_dados = ?
            WHERE id = ?
        ''', (
            data.get('nome'), data.get('email'), data.get('telefone'),
            data.get('tipo_sanguineo'), data.get('data_nascimento'), data.get('genero'),
            data.get('cep'), data.get('endereco'), data.get('ja_doou'), data.get('primeira_vez'),
            data.get('interesse'), 1 if data.get('autoriza_msg') == 'sim' else 0,
            1 if data.get('autoriza_dados') == 'sim' else 0, user_id
        ))
    
    conn.commit()
    conn.close()
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE id = ?', (user_id,))
    usuario_data = c.fetchone()
    conn.close()
    
    if usuario_data is None:
        logging.error(f"Nenhum usuário encontrado para ID: {user_id}")
        return render_template('perfil.html', error="Usuário não encontrado.", logged_in=False)
    
    usuario = dict(usuario_data)
    usuario["nivel"] = "Doador Iniciante"
    usuario["progressoPercentual"] = usuario["pontos"] * 10
    usuario["selos"] = []
    if usuario["ja_doou"] == 'sim':
        usuario["selos"].append({
            "nome": "Primeira Doação!",
            "caminhoImagem": "assets/selo-primeira-doacao.png"
        })
    
    logging.debug(f"Perfil atualizado para usuário ID: {user_id}")
    return render_template('perfil.html', usuario=usuario, success="Perfil atualizado com sucesso!", logged_in=True)

@app.route('/perfil/')
@app.route('/perfil/<int:usuario_id>')
def perfil(usuario_id=None):
    cookie_usuario_id = request.cookies.get('usuario_id')
    login_time = request.cookies.get('login_time')
    if not cookie_usuario_id or not login_time:
        logging.debug("Nenhum cookie encontrado ou login_time ausente, redirecionando para login")
        return redirect(url_for('login'))
    try:
        login_time_dt = datetime.fromisoformat(login_time)
        if datetime.utcnow() - login_time_dt > timedelta(days=4):
            logging.debug("Cookie expirado, redirecionando para login")
            return redirect(url_for('login'))
        usuario_id = usuario_id or int(cookie_usuario_id)
    except (ValueError, TypeError):
        logging.error("Erro ao processar cookie de login_time ou usuario_id inválido")
        return redirect(url_for('login'))
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
    usuario_data = c.fetchone()
    conn.close()
    if usuario_data is None:
        logging.error(f"Nenhum usuário encontrado para ID: {usuario_id}")
        return render_template('perfil.html', error="Usuário não encontrado. Por favor, faça login ou cadastre-se novamente.", logged_in=False)
    usuario = dict(usuario_data)
    usuario["nivel"] = "Doador Iniciante"
    usuario["progressoPercentual"] = usuario["pontos"] * 10
    usuario["selos"] = []
    if usuario["ja_doou"] == 'sim':
        usuario["selos"].append({
            "nome": "Primeira Doação!",
            "caminhoImagem": "assets/selo-primeira-doacao.png"
        })
    logging.debug(f"Dados do usuário: {usuario}")
    response = make_response(render_template('perfil.html', usuario=usuario, logged_in=True))
    try:
        if (datetime.utcnow() - login_time_dt) < timedelta(days=3):
            response.set_cookie('login_time', datetime.utcnow().isoformat(), max_age=3*24*60*60)
    except UnboundLocalError:
        logging.error("login_time_dt não definido, não renovando cookie")
    return response

@app.route('/api/campanhas')
def api_campanhas():
    campanhas = [
        {"id": 1, "nome": "Urgência O-", "tipo_sanguineo": "O-", "participantes": 15, "vagas": 20},
        {"id": 2, "nome": "Campanha Pediátrica", "tipo_sanguineo": "Todos", "participantes": 45, "vagas": 100},
        {"id": 3, "nome": "Ajude o Sr. João", "tipo_sanguineo": "B+", "participantes": 5, "vagas": 10},
        {"id": 4, "nome": "Estoque Crítico A-", "tipo_sanguineo": "A-", "participantes": 8, "vagas": 15},
    ]
    total_participantes = sum(c['participantes'] for c in campanhas)
    total_vagas = sum(c['vagas'] for c in campanhas)
    return jsonify({
        "campanhas": campanhas,
        "estatisticas": {
            "totalCampanhas": len(campanhas),
            "totalParticipantes": total_participantes,
            "vagasDisponiveis": total_vagas - total_participantes
        }
    })

@app.route('/recuperar', methods=['GET'])
def recuperar():
    return render_template('recuperar_senha.html', logged_in=False)

@app.route('/email-submit', methods=['POST'])
def email_submit():
    email = request.form['email']
    corpo = f"""
    Olá,
    Recebemos uma solicitação para redefinir sua senha.
    Clique no link abaixo para continuar:
    http://seusite.com/redefinir_senha?email={email}
    Se você não fez esta solicitação, ignore este e-mail.
    """
    resultado = enviar_email(email, 'Recuperação de Senha', corpo)
    if resultado['status'] == 'sucesso':
        return render_template('recuperar_senha.html', sucesso=True, logged_in=False)
    else:
        return render_template('recuperar_senha.html', erro=resultado['mensagem'], logged_in=False)

@app.route('/enviar_email', methods=['POST'])
def enviar_email_api():
    dados = request.get_json()
    resultado = enviar_email(dados['para'], dados['assunto'], dados['mensagem'])
    status = 200 if resultado['status'] == 'sucesso' else 500
    return jsonify(resultado), status

@app.route('/conscientizacao')
def conscientizacao():
    cookie_usuario_id = request.cookies.get('usuario_id')
    login_time = request.cookies.get('login_time')
    logged_in = False
    if cookie_usuario_id and login_time:
        try:
            login_time_dt = datetime.fromisoformat(login_time)
            if datetime.utcnow() - login_time_dt <= timedelta(days=4):
                logged_in = True
        except (ValueError, TypeError):
            pass
    nome = request.args.get('nome', 'Doador')
    return render_template('conscientizacao.html', nome=nome, pontos=0, logged_in=logged_in)

if __name__ == '__main__':
    app.run(debug=True)