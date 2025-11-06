from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
import sqlite3
import os

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
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE usuarios (
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
                pontos INTEGER DEFAULT 0
            )
        ''')
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
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/campanhas')
def campanhas():
    return render_template('campanhas.html')

@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')

# -----------------------------
# Cadastro de Usuário
# -----------------------------
@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO usuarios (
            nome, email, telefone, tipo_sanguineo, data_nascimento, genero,
            cep, endereco, ja_doou, primeira_vez, interesse,
            autoriza_msg, autoriza_dados, pontos
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (
        data.get('nome'), data.get('email'), data.get('telefone'),
        data.get('tipo_sanguineo'), data.get('data_nascimento'),
        data.get('genero'), data.get('cep'), data.get('endereco'),
        data.get('ja_doou'), data.get('primeira_vez'), data.get('interesse'),
        1 if data.get('autoriza_msg') == 'on' else 0,
        1 if data.get('autoriza_dados') == 'on' else 0
    ))
    conn.commit()
    user_id = c.lastrowid
    conn.close()

    return redirect(url_for('perfil', usuario_id=user_id))

# -----------------------------
# Perfil de Usuário
# -----------------------------
@app.route('/perfil/')
@app.route('/perfil/<int:usuario_id>')
def perfil(usuario_id=None):
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if usuario_id:
        c.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
    else:
        c.execute('SELECT * FROM usuarios ORDER BY id DESC LIMIT 1')

    usuario_data = c.fetchone()
    conn.close()

    if usuario_data is None:
        return redirect(url_for('cadastro'))

    usuario = dict(usuario_data)
    usuario["nivel"] = "Doador Iniciante"
    usuario["progressoPercentual"] = usuario["pontos"] * 10
    usuario["selos"] = []

    if usuario["ja_doou"] == 'sim':
        usuario["selos"].append({
            "nome": "Primeira Doação!",
            "caminhoImagem": "assets/selo-primeira-doacao.png"
        })

    return render_template('perfil.html', usuario=usuario)

# -----------------------------
# API de Campanhas
# -----------------------------
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

# -----------------------------
# Recuperação de Senha (Form + E-mail)
# -----------------------------
@app.route('/recuperar', methods=['GET'])
def recuperar():
    return render_template('recuperar_senha.html')

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
        return render_template('recuperar_senha.html', sucesso=True)
    else:
        return render_template('recuperar_senha.html', erro=resultado['mensagem'])

@app.route('/enviar_email', methods=['POST'])
def enviar_email_api():
    dados = request.get_json()
    resultado = enviar_email(dados['para'], dados['assunto'], dados['mensagem'])
    status = 200 if resultado['status'] == 'sucesso' else 500
    return jsonify(resultado), status

# -----------------------------
# Página de Conscientização
# -----------------------------
@app.route('/conscientizacao')
def conscientizacao():
    nome = request.args.get('nome', 'Doador')
    return render_template('conscientizacao.html', nome=nome, pontos=0)

# -----------------------------
# Execução da Aplicação
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
