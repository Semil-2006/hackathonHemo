from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from dotenv import load_dotenv
import secrets
import time
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

campanhas_db = [
    {"id": 1, "nome": "Urgência O- Hospital X", "tipo_sanguineo": "O-", "vagas": 50, "participantes": 12, "status": "Ativa"},
    {"id": 2, "nome": "Doação Geral de Verão", "tipo_sanguineo": "Todos", "vagas": 100, "participantes": 85, "status": "Ativa"},
    {"id": 3, "nome": "AB+ Maternidade Central", "tipo_sanguineo": "AB+", "vagas": 30, "participantes": 30, "status": "Encerrada"},
]
# Define o próximo ID, essencial para a função POST
proximo_id = 4

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# For AJAX/API calls we prefer JSON 401 responses instead of HTML redirects.
@login_manager.unauthorized_handler
def unauthorized_callback():
    try:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'unauthorized'}), 401
    except Exception:
        pass
    return redirect(url_for('login'))

# -----------------------------
# Configurações do Flask
# -----------------------------
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# If SECRET_KEY is not provided via environment (common in local/dev),
# generate a secure random key so Flask session machinery (and Flask-Login)
# can work. In production provide a fixed secret via the SECRET_KEY env var.
if not app.config.get('SECRET_KEY'):
    generated_secret = secrets.token_urlsafe(32)
    app.config['SECRET_KEY'] = generated_secret
    logging.warning('SECRET_KEY was not set in environment; generated a temporary key for session support (not for production).')

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
    if 'nivel' not in columns:
        # store donor level (e.g. 'Doador Iniciante', 'Doador Comprometido', 'Doador Heróico')
        c.execute("ALTER TABLE usuarios ADD COLUMN nivel TEXT DEFAULT 'Doador Iniciante'")

    conn.commit()
    conn.close()

    # Create a table to log email sends
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT,
            recipient_email TEXT,
            status TEXT,
            error TEXT,
            sent_at TEXT,
            admin_user_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Create campaigns table if missing
def init_campaigns_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS campanhas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo_sanguineo TEXT,
            vagas INTEGER DEFAULT 0,
            participantes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Ativa',
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_campaigns_table()


# Create participations table
def init_participations_table():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS participacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            campanha_id INTEGER NOT NULL,
            joined_at TEXT,
            UNIQUE(usuario_id, campanha_id)
        )
    ''')
    conn.commit()
    conn.close()

init_participations_table()

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


# --- Flask-Login user class and loader ---
class User(UserMixin):
    def __init__(self, id, email=None, nome=None):
        self.id = str(id)
        self.email = email
        self.nome = nome


@login_manager.user_loader
def load_user(user_id):
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE id = ?', (int(user_id),))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row['id'], row['email'], row['nome'])
    except Exception:
        return None
    return None

# -----------------------------
# Rotas
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')
        if not email or not senha:
            logging.error("Email ou senha não fornecidos")
            return render_template('login.html', error="Por favor, preencha todos os campos.")
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario = c.fetchone()
        conn.close()
        if not usuario:
            logging.error(f"Usuário com email {email} não encontrado")
            return render_template('login.html', error="Email ou senha inválidos")
        if check_password_hash(usuario['senha'], senha):
            user = User(usuario['id'], usuario['email'], usuario['nome'])
            login_user(user)
            logging.debug(f"Login bem-sucedido para usuário ID: {usuario['id']}")
            return redirect(url_for('perfil'))
        else:
            logging.error(f"Senha inválida para email {email}")
            return render_template('login.html', error="Email ou senha inválidos")
    return render_template('login.html', logged_in=False)

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/campanhas')
def campanhas():
    return render_template('campanhas.html')

@app.route('/campanhas_admin')
def campanhas_admin():
    return render_template('campanhas_admin.html')

@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')


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
    # Log the user in immediately after registration
    user = User(user_id, data.get('email'), data.get('nome'))
    login_user(user)
    logging.debug(f"Usuário cadastrado com ID: {user_id}")
    return redirect(url_for('perfil'))

@app.route('/perfil/<int:usuario_id>')
@app.route('/perfil/')
@login_required
def perfil(usuario_id=None):
    # Use the authenticated user by default. Only allow viewing own profile for now.
    try:
        if usuario_id is not None and int(usuario_id) != int(current_user.id):
            logging.warning(f"Usuário {current_user.id} tentou acessar perfil de {usuario_id}")
            return make_response('Forbidden', 403)
        usuario_id = usuario_id or int(current_user.id)
    except (ValueError, TypeError):
        logging.error("ID de usuário inválido")
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
    usuario_data = c.fetchone()
    # fetch participations for the user
    c.execute('''
        SELECT p.id as participacao_id, p.joined_at, c.*
        FROM participacoes p
        JOIN campanhas c ON p.campanha_id = c.id
        WHERE p.usuario_id = ?
        ORDER BY p.joined_at DESC
    ''', (usuario_id,))
    participations_rows = c.fetchall()
    conn.close()
    if usuario_data is None:
        logging.error(f"Nenhum usuário encontrado para ID: {usuario_id}")
        return render_template('perfil.html', error="Usuário não encontrado. Por favor, faça login ou cadastre-se novamente.")
    usuario = dict(usuario_data)
    usuario['participacoes'] = [dict(r) for r in participations_rows] if participations_rows else []
    # Compute participation-based stats
    participation_count = len(usuario['participacoes']) if usuario.get('participacoes') else 0

    # Determine current level (prefer stored level if present)
    def compute_level_from_count(n):
        if n >= 6:
            return 'Doador Heróico'
        if n >= 3:
            return 'Doador Comprometido'
        if n >= 1:
            return 'Doador Iniciante'
        return 'Não classificado'

    stored_level = usuario.get('nivel')
    if stored_level and stored_level.strip() and stored_level != 'None':
        usuario['nivel'] = stored_level
    else:
        usuario['nivel'] = compute_level_from_count(participation_count)

    # Next level thresholds and names
    if participation_count >= 6:
        next_threshold = 6
        next_level_name = 'Nível Máximo'
    elif participation_count >= 3:
        next_threshold = 6
        next_level_name = 'Doador Heróico'
    elif participation_count >= 1:
        next_threshold = 3
        next_level_name = 'Doador Comprometido'
    else:
        next_threshold = 1
        next_level_name = 'Doador Iniciante'

    # Progress towards next threshold
    progresso_percentual = int(min(100, (participation_count / next_threshold) * 100)) if next_threshold else 0
    participations_to_next = max(0, next_threshold - participation_count)

    usuario['participation_count'] = participation_count
    usuario['next_threshold'] = next_threshold
    usuario['next_level_name'] = next_level_name
    usuario['participations_to_next'] = participations_to_next
    usuario['progress_text'] = f"{participation_count}/{next_threshold}"
    usuario["progressoPercentual"] = progresso_percentual

    # Build earned badges (selos) based on participation_count and other flags
    selos = []
    # First donation badge (if flagged in DB)
    if usuario.get("ja_doou") == 'sim' or usuario.get('primeira_vez'):
        selos.append({
            'nome': 'Primeira Doação',
            'caminhoImagem': 'assets/selo-primeira-doacao.png'
        })

    # Participation-based badges
    # 1 participation -> Iniciante badge
    if participation_count >= 1:
        selos.append({ 'nome': 'Iniciante', 'caminhoImagem': 'assets/emblemas/1.png' })
    # 3 participations -> Comprometido
    if participation_count >= 3:
        selos.append({ 'nome': 'Comprometido', 'caminhoImagem': 'assets/emblemas/2.png' })
    # 6 participations -> Heróico
    if participation_count >= 6:
        selos.append({ 'nome': 'Heróico', 'caminhoImagem': 'assets/emblemas/3.png' })

    # attach to usuario for template consumption
    usuario['selos'] = selos
    usuario["selos"] = []
    if usuario.get("ja_doou") == 'sim':
        usuario["selos"].append({
            "nome": "Primeira Doação!",
            "caminhoImagem": "assets/selo-primeira-doacao.png"
        })
    logging.debug(f"Dados do usuário: {usuario}")
    return render_template('perfil.html', usuario=usuario, logged_in=True)


# Rota para atualizar os dados do perfil (edição pelo usuário)
@app.route('/perfil/<int:usuario_id>/update', methods=['POST'])
@login_required
def update_perfil(usuario_id):
    # Recebe os dados do formulário e atualiza o usuário no banco
    data = request.form.to_dict()
    logging.debug(f"Atualizando usuário {usuario_id} com: {data}")

    # Segurança: somente o dono do perfil pode atualizar
    try:
        if int(current_user.id) != int(usuario_id):
            logging.warning(f"Tentativa de atualização não autorizada: user {current_user.id} tentou atualizar {usuario_id}")
            return make_response('Forbidden', 403)
    except (ValueError, TypeError):
        logging.error("ID de usuário inválido no current_user")
        return make_response('Forbidden', 403)

    # Campos esperados (ajuste conforme necessário)
    nome = data.get('nome')
    email = data.get('email')
    telefone = data.get('telefone')
    tipo_sanguineo = data.get('tipo_sanguineo')
    data_nascimento = data.get('data_nascimento')
    genero = data.get('genero')
    cep = data.get('cep')
    endereco = data.get('endereco')
    ja_doou = data.get('ja_doou')
    primeira_vez = data.get('primeira_vez')
    interesse = data.get('interesse')
    autoriza_msg = 1 if data.get('autoriza_msg') in ('on', '1', 'true', 'True') else 0
    autoriza_dados = 1 if data.get('autoriza_dados') in ('on', '1', 'true', 'True') else 0

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE usuarios SET
            nome = ?, email = ?, telefone = ?, tipo_sanguineo = ?,
            data_nascimento = ?, genero = ?, cep = ?, endereco = ?,
            ja_doou = ?, primeira_vez = ?, interesse = ?,
            autoriza_msg = ?, autoriza_dados = ?
        WHERE id = ?
    ''', (nome, email, telefone, tipo_sanguineo,
          data_nascimento, genero, cep, endereco,
          ja_doou, primeira_vez, interesse,
          autoriza_msg, autoriza_dados, usuario_id))
    conn.commit()
    conn.close()

    logging.debug(f"Usuário {usuario_id} atualizado com sucesso")
    return redirect(url_for('perfil', usuario_id=usuario_id))

@app.route('/api/dashboard_data')
def api_dashboard_data():
    """Retorna dados agregados a partir da tabela usuarios para alimentar o dashboard.
    A saída é uma lista de objetos: { city, potential, engage, distance }
    - city: string (extraído heurísticamente do campo 'endereco' ou 'cep')
    - potential: número de usuários na cidade (estimativa de doadores)
    - engage: proporção (0..1) de usuários com autoriza_msg=1
    - distance: valor numeric usado para simular logística (determinístico por cidade)
    """
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT endereco, cep, autoriza_msg FROM usuarios')
        rows = c.fetchall()
        conn.close()

        # Agrupar por cidade extraída do endereco (heurística: token final após vírgula)
        agg = {}
        for r in rows:
            endereco = r['endereco'] or ''
            cep = r['cep'] or ''
            # heurística simples para cidade
            city = None
            if ',' in endereco:
                city = endereco.split(',')[-1].strip()
            elif endereco.strip():
                city = endereco.strip()
            elif cep:
                city = f'CEP {cep}'
            else:
                city = 'Desconhecido'

            if city not in agg:
                agg[city] = { 'count': 0, 'consent': 0 }
            agg[city]['count'] += 1
            try:
                if int(r['autoriza_msg']) == 1:
                    agg[city]['consent'] += 1
            except Exception:
                pass

        results = []
        for city, v in agg.items():
            count = v['count']
            consent = v['consent']
            # deterministic pseudo-distance: sum of char codes mod 30 + 1
            s = sum(ord(ch) for ch in city)
            distance = (s % 30) + 1
            engage = (consent / count) if count else 0
            results.append({ 'city': city, 'potential': count, 'engage': round(engage, 2), 'distance': distance })


        # sort descending by potential
        results.sort(key=lambda x: x['potential'], reverse=True)
        return jsonify({ 'data': results })
    except Exception as e:
        logging.exception('Erro ao gerar dados do dashboard')
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Campaigns CRUD API
# -----------------------------
@app.route('/api/campaigns', methods=['GET'])
def api_get_campaigns():
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM campanhas ORDER BY created_at DESC')
        rows = c.fetchall()
        conn.close()
        campanhas = [dict(r) for r in rows]
        return jsonify({'campaigns': campanhas})
    except Exception as e:
        logging.exception('Erro ao buscar campanhas')
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns', methods=['POST'])
def api_create_campaign():
    try:
        data = request.get_json() or request.form.to_dict()
        nome = data.get('nome')
        tipo = data.get('tipo_sanguineo')
        vagas = int(data.get('vagas') or 0)
        status = data.get('status') or 'Ativa'
        created_at = datetime.utcnow().isoformat()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO campanhas (nome, tipo_sanguineo, vagas, status, created_at) VALUES (?, ?, ?, ?, ?)',
                  (nome, tipo, vagas, status, created_at))
        conn.commit()
        campaign_id = c.lastrowid
        conn.close()
        return jsonify({'id': campaign_id, 'message': 'Campanha criada'}), 201
    except Exception as e:
        logging.exception('Erro ao criar campanha')
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
def api_update_campaign(campaign_id):
    try:
        data = request.get_json() or request.form.to_dict()
        nome = data.get('nome')
        tipo = data.get('tipo_sanguineo')
        vagas = data.get('vagas')
        status = data.get('status')
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Build update dynamically
        updates = []
        params = []
        if nome is not None:
            updates.append('nome = ?'); params.append(nome)
        if tipo is not None:
            updates.append('tipo_sanguineo = ?'); params.append(tipo)
        if vagas is not None:
            updates.append('vagas = ?'); params.append(int(vagas))
        if status is not None:
            updates.append('status = ?'); params.append(status)
        if updates:
            params.append(campaign_id)
            sql = 'UPDATE campanhas SET ' + ', '.join(updates) + ' WHERE id = ?'
            c.execute(sql, tuple(params))
            conn.commit()
        conn.close()
        return jsonify({'message': 'Campanha atualizada'})
    except Exception as e:
        logging.exception('Erro ao atualizar campanha')
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
def api_delete_campaign(campaign_id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM campanhas WHERE id = ?', (campaign_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Campanha removida'})
    except Exception as e:
        logging.exception('Erro ao remover campanha')
        return jsonify({'error': str(e)}), 500

# Rota para renderizar a página
@app.route('/admin/campanhas')
def admin_campanhas():
    return render_template('admin_campanhas.html') # Assumindo que sua página está em 'admin_campanhas.html'

# --- Endpoints da API para o JS ---

# 1. Listar Campanhas (GET /api/campanhas)
# @app.route('/api/campanhas', methods=['GET'])
# def listar_campanhas():
#     return jsonify(campanhas_db)
@app.route('/api/campanhas', methods=['GET'])
def listar_campanhas():
    # Calcula as estatísticas dinamicamente
    total_participantes = sum(c.get('participantes', 0) for c in campanhas_db)
    total_vagas = sum(c.get('vagas', 0) for c in campanhas_db)
    
    # Retorna o formato esperado: { "campanhas": [...] }
    return jsonify({
        "campanhas": campanhas_db,
        "estatisticas": {
            "totalCampanhas": len(campanhas_db),
            "totalParticipantes": total_participantes,
            "vagasDisponiveis": total_vagas - total_participantes
        }
    })

# 2. Criar Nova Campanha (POST /api/campanhas)
@app.route('/api/campanhas', methods=['POST'])
def criar_campanha():
    global proximo_id
    dados = request.get_json()
    
    nova_campanha = {
        "id": proximo_id,
        "nome": dados.get('nome'),
        "tipo_sanguineo": dados.get('tipo_sanguineo'),
        "vagas": 50, # Valor padrão, pode ser ajustado na edição
        "participantes": 0,
        "status": "Ativa"
    }
    campanhas_db.append(nova_campanha)
    proximo_id += 1
    
    return jsonify({"mensagem": "Campanha criada com sucesso!", "campanha": nova_campanha}), 201

# 3. Atualizar Campanha (PUT /api/campanhas/<id>)
@app.route('/api/campanhas/<int:campanha_id>', methods=['PUT'])
def atualizar_campanha(campanha_id):
    dados = request.get_json()
    
    for campanha in campanhas_db:
        if campanha['id'] == campanha_id:
            campanha['nome'] = dados.get('nome', campanha['nome'])
            campanha['tipo_sanguineo'] = dados.get('tipo_sanguineo', campanha['tipo_sanguineo'])
            campanha['vagas'] = dados.get('vagas', campanha['vagas'])
            campanha['status'] = dados.get('status', campanha['status'])
            return jsonify({"mensagem": f"Campanha {campanha_id} atualizada com sucesso!"}), 200
            
    return jsonify({"erro": "Campanha não encontrada"}), 404

# 4. Remover Campanha (DELETE /api/campanhas/<id>)
@app.route('/api/campanhas/<int:campanha_id>', methods=['DELETE'])
def remover_campanha(campanha_id):
    global campanhas_db
    tamanho_original = len(campanhas_db)
    # Filtra a lista, mantendo apenas as campanhas cujo ID é diferente do ID a ser removido
    campanhas_db = [c for c in campanhas_db if c['id'] != campanha_id]
    
    if len(campanhas_db) < tamanho_original:
        return jsonify({"mensagem": f"Campanha {campanha_id} removida com sucesso!"}), 200
    else:
        return jsonify({"erro": "Campanha não encontrada"}), 404

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
@app.route('/enviar_email.html')
def enviar_email_page():
    """ Rota GET para CARREGAR a página 'enviar_email.html' """
    try:
        return render_template('enviar_email.html')
    except Exception as e:
        print(f"Erro ao renderizar enviar_email.html: {e}")
        return "Erro interno - template não encontrado", 500


@app.route('/recuperar', methods=['GET'])
def recuperar():
    return render_template('recuperar_senha.html')


@app.route('/api/me')
def api_me():
    """Return minimal info about the current authenticated user as JSON.
    Returns 401 if not logged in.
    """
    if not getattr(current_user, 'is_authenticated', False):
        return jsonify({'error': 'unauthorized'}), 401
    try:
        return jsonify({'id': int(current_user.id), 'email': getattr(current_user, 'email', None), 'nome': getattr(current_user, 'nome', None)})
    except Exception:
        return jsonify({'error': 'could not read user'}), 500

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

@app.route('/conscientizacao')
def conscientizacao():
    nome = request.args.get('nome', 'Doador')
    return render_template('conscientizacao.html', nome=nome, pontos=0)



# Endpoint para envio segmentado de campanhas (email)
@app.route('/api/admin/send_campaign', methods=['POST'])
@login_required
def api_admin_send_campaign():
    """Recebe um JSON com: { canal_disparo, remetente, conteudo, segmentacao }
    segmentacao pode conter: tipo_sanguineo: [..], genero, min_age, max_age, cidade: [..], classificacao, interesse
    Retorna JSON com { sent: N, failed: [ {email, error} ] }
    """
    try:
        payload = request.get_json() or {}
        canal = payload.get('canal_disparo', 'email')
        remetente = payload.get('remetente')
        conteudo = payload.get('conteudo', '')
        segmentacao = payload.get('segmentacao', {}) or {}

        tipos = segmentacao.get('tipo_sanguineo') or []
        genero = segmentacao.get('genero') or None
        cidade_list = segmentacao.get('cidade') or []
        interesse = segmentacao.get('interesse') or None
        classificacao = segmentacao.get('classificacao') or None
        min_age = segmentacao.get('min_age')
        max_age = segmentacao.get('max_age')

        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Build dynamic query
        query = "SELECT id, nome, email, tipo_sanguineo, genero, data_nascimento, endereco, ja_doou FROM usuarios WHERE email IS NOT NULL AND email != ''"
        params = []
        if tipos:
            placeholders = ','.join('?' for _ in tipos)
            query += f" AND tipo_sanguineo IN ({placeholders})"
            params.extend(tipos)
        if genero:
            query += " AND genero = ?"
            params.append(genero)
        if cidade_list:
            # match any cidade in endereco (simple LIKE)
            city_clauses = []
            for city in cidade_list:
                city_clauses.append("endereco LIKE ?")
                params.append(f"%{city}%")
            query += " AND (" + " OR ".join(city_clauses) + ")"
        if interesse and interesse != 'todos':
            query += " AND interesse = ?"
            params.append(interesse)
        if classificacao and classificacao != 'todos':
            query += " AND primeira_vez = ?"
            params.append('sim' if classificacao == 'primeira_vez' else classificacao)

        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        # Filter by age if requested
        recipients = []
        now = datetime.utcnow().date()
        for r in rows:
            dob = r['data_nascimento']
            age = None
            if dob:
                try:
                    # Try ISO format first
                    if '-' in dob:
                        dob_dt = datetime.fromisoformat(dob).date()
                    elif '/' in dob:
                        # try DD/MM/YYYY
                        parts = dob.split('/')
                        if len(parts) == 3:
                            day, month, year = parts
                            dob_dt = datetime(int(year), int(month), int(day)).date()
                        else:
                            dob_dt = None
                    else:
                        dob_dt = None
                    if dob_dt:
                        age = (now - dob_dt).days // 365
                except Exception:
                    age = None

            if min_age is not None or max_age is not None:
                try:
                    if age is None:
                        # if we can't compute age, skip this recipient when age filter is requested
                        continue
                    if min_age is not None and age < int(min_age):
                        continue
                    if max_age is not None and age > int(max_age):
                        continue
                except Exception:
                    continue

            recipients.append({'id': r['id'], 'nome': r['nome'], 'email': r['email']})

        sent = 0
        failed = []

        # Simple sending loop (synchronous). For many recipients, consider background job / queue.
        subject = f"{remetente or 'Hemocentro'} - Comunicado"
        for rec in recipients:
            try:
                # Customize content with name if desired
                body = conteudo.replace('[nome_doador]', rec.get('nome') or '')
                resultado = enviar_email(rec['email'], subject, body)
                if resultado.get('status') == 'sucesso':
                    sent += 1
                else:
                    failed.append({'email': rec['email'], 'error': resultado.get('mensagem')})
            except Exception as e:
                failed.append({'email': rec['email'], 'error': str(e)})

        return jsonify({'sent': sent, 'failed': failed, 'recipients_count': len(recipients)})
    except Exception as e:
        logging.exception('Erro ao enviar campanha')
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Participation endpoints
# -----------------------------
@app.route('/api/campaigns/<int:campaign_id>/participate', methods=['POST'])
@login_required
def api_participate_campaign(campaign_id):
    user_id = int(current_user.id)
    logging.debug(f"API participate called by user {user_id} for campaign {campaign_id}")
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        # Check campaign exists
        c.execute('SELECT id FROM campanhas WHERE id = ?', (campaign_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Campanha não encontrada'}), 404

        joined_at = datetime.utcnow().isoformat()
        try:
            # ensure user is not already subscribed (clear error message)
            c.execute('SELECT 1 FROM participacoes WHERE usuario_id = ? AND campanha_id = ?', (user_id, campaign_id))
            if c.fetchone():
                conn.close()
                return jsonify({'error': 'Você já está inscrito nesta campanha'}), 409

            c.execute('INSERT INTO participacoes (usuario_id, campanha_id, joined_at) VALUES (?, ?, ?)',
                      (user_id, campaign_id, joined_at))
            # increment participantes counter in campanhas table
            c.execute('UPDATE campanhas SET participantes = COALESCE(participantes,0) + 1 WHERE id = ?', (campaign_id,))
            # Recompute user's donor level based on total participations and persist
            c.execute('SELECT COUNT(*) FROM participacoes WHERE usuario_id = ?', (user_id,))
            cnt = c.fetchone()[0] or 0
            if cnt >= 6:
                new_level = 'Doador Heróico'
            elif cnt >= 3:
                new_level = 'Doador Comprometido'
            elif cnt >= 1:
                new_level = 'Doador Iniciante'
            else:
                new_level = None
            if new_level:
                c.execute("UPDATE usuarios SET nivel = ? WHERE id = ?", (new_level, user_id))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Inscrição realizada com sucesso'}), 201
        except sqlite3.IntegrityError:
            # fallback: unique constraint violated
            conn.close()
            return jsonify({'error': 'Você já está inscrito nesta campanha'}), 409
    except Exception as e:
        logging.exception('Erro ao inscrever usuário na campanha')
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns/<int:campaign_id>/participate', methods=['DELETE'])
@login_required
def api_unparticipate_campaign(campaign_id):
    user_id = int(current_user.id)
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM participacoes WHERE usuario_id = ? AND campanha_id = ?', (user_id, campaign_id))
        if c.rowcount > 0:
            # decrement participantes (avoid negative values)
            c.execute('UPDATE campanhas SET participantes = CASE WHEN COALESCE(participantes,0) > 0 THEN participantes - 1 ELSE 0 END WHERE id = ?', (campaign_id,))
            conn.commit()
            # Recompute user's donor level after removal
            c.execute('SELECT COUNT(*) FROM participacoes WHERE usuario_id = ?', (user_id,))
            cnt = c.fetchone()[0] or 0
            if cnt >= 6:
                new_level = 'Doador Heróico'
            elif cnt >= 3:
                new_level = 'Doador Comprometido'
            elif cnt >= 1:
                new_level = 'Doador Iniciante'
            else:
                new_level = 'Não classificado'
            c.execute('UPDATE usuarios SET nivel = ? WHERE id = ?', (new_level, user_id))
            conn.commit()
            conn.close()
            return jsonify({'message': 'Removido da campanha'}), 200
        else:
            conn.close()
            return jsonify({'error': 'Inscrição não encontrada'}), 404
    except Exception as e:
        logging.exception('Erro ao remover inscrição')
        return jsonify({'error': str(e)}), 500


@app.route('/api/my_participations', methods=['GET'])
@login_required
def api_my_participations():
    user_id = int(current_user.id)
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('''
            SELECT p.id as participacao_id, p.joined_at, c.*
            FROM participacoes p
            JOIN campanhas c ON p.campanha_id = c.id
            WHERE p.usuario_id = ?
            ORDER BY p.joined_at DESC
        ''', (user_id,))
        rows = c.fetchall()
        conn.close()
        participations = [dict(r) for r in rows]
        return jsonify({'participations': participations})
    except Exception as e:
        logging.exception('Erro ao buscar participações do usuário')
        return jsonify({'error': str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)

