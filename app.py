from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

# --- Configuração do Banco de Dados (Seu código original) ---
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
        # If SMTP not configured, write to an outbox folder for local testing
        mail_server = app.config.get('MAIL_SERVER')
        mail_user = app.config.get('MAIL_USERNAME')
        if not mail_server or not mail_user:
            try:
                os.makedirs('outbox', exist_ok=True)
                safe_email = (para or 'no-reply').replace('@', '_at_').replace('/', '_')
                filename = f"outbox/{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}_{safe_email}.eml"
                with open(filename, 'w', encoding='utf-8') as fh:
                    fh.write(f"To: {para}\nSubject: {assunto}\n\n{mensagem}")
                logging.info(f"E-mail gravado em outbox (SMTP não configurado): {filename}")
                return {'status': 'sucesso', 'mensagem': f'E-mail gravado em outbox: {filename}'}
            except Exception:
                logging.exception('Falha ao gravar e-mail em outbox')
                # continue to attempt real send if possible

        # Compose and send real email
        msg = Message(subject=assunto, recipients=[para], body=mensagem, sender=app.config.get('MAIL_DEFAULT_SENDER'))
        mail.send(msg)
        logging.info(f"E-mail enviado para {para} assunto='{assunto}'")
        return {'status': 'sucesso', 'mensagem': 'E-mail enviado com sucesso!'}
    except Exception as e:
        logging.exception(f'Erro ao enviar email para {para}')
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


# Inject a safe `usuario` object into all templates so templates referencing
# `usuario` don't raise UndefinedError when routes don't pass it explicitly.
@app.context_processor
def inject_usuario():
    try:
        if getattr(current_user, 'is_authenticated', False):
            uid = int(current_user.id)
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM usuarios WHERE id = ?', (uid,))
            row = c.fetchone()
            if not row:
                conn.close()
                return {'usuario': {}}

            usuario = dict(row)
            # participations
            c.execute('''
                SELECT p.id as participacao_id, p.joined_at, c.*
                FROM participacoes p
                JOIN campanhas c ON p.campanha_id = c.id
                WHERE p.usuario_id = ?
                ORDER BY p.joined_at DESC
            ''', (uid,))
            parts = c.fetchall()
            conn.close()
            usuario['participacoes'] = [dict(r) for r in parts] if parts else []
            participation_count = len(usuario['participacoes'])

            # compute level
            if participation_count >= 6:
                nivel = 'Doador Heróico'
            elif participation_count >= 3:
                nivel = 'Doador Comprometido'
            elif participation_count >= 1:
                nivel = 'Doador Iniciante'
            else:
                nivel = usuario.get('nivel') or 'Não classificado'

            usuario['nivel'] = usuario.get('nivel') or nivel

            # thresholds
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

            progresso = int(min(100, (participation_count / next_threshold) * 100)) if next_threshold else 0
            usuario['participation_count'] = participation_count
            usuario['next_threshold'] = next_threshold
            usuario['next_level_name'] = next_level_name
            usuario['participations_to_next'] = max(0, next_threshold - participation_count)
            usuario['progress_text'] = f"{participation_count}/{next_threshold}"
            usuario['progressoPercentual'] = progresso

            # selos
            selos = []
            if usuario.get('ja_doou') == 'sim' or usuario.get('primeira_vez'):
                selos.append({ 'nome': 'Primeira Doação', 'caminhoImagem': 'assets/selo-primeira-doacao.png' })
            if participation_count >= 1:
                selos.append({ 'nome': 'Iniciante', 'caminhoImagem': 'assets/emblemas/1.png' })
            if participation_count >= 3:
                selos.append({ 'nome': 'Comprometido', 'caminhoImagem': 'assets/emblemas/2.png' })
            if participation_count >= 6:
                selos.append({ 'nome': 'Heróico', 'caminhoImagem': 'assets/emblemas/3.png' })
            usuario['selos'] = selos

            # build full set of available emblems (all_selos) and mark unlocked
            unlocked_names = set(s['nome'] for s in usuario['selos'])
            all_selos = [
                { 'nome': 'Primeira Doação', 'caminhoImagem': 'assets/selo-primeira-doacao.png' },
                { 'nome': 'Iniciante', 'caminhoImagem': 'assets/emblemas/1.png' },
                { 'nome': 'Comprometido', 'caminhoImagem': 'assets/emblemas/2.png' },
                { 'nome': 'Heróico', 'caminhoImagem': 'assets/emblemas/3.png' },
                # additional emblems (locked by default unless added above)
                { 'nome': 'Salvador de Vidas', 'caminhoImagem': 'assets/emblemas/4.png' },
                { 'nome': 'Tipo O Universal', 'caminhoImagem': 'assets/emblemas/5.png' },
                { 'nome': 'Fidelidade', 'caminhoImagem': 'assets/emblemas/6.png' },
            ]
            for s in all_selos:
                s['unlocked'] = (s['nome'] in unlocked_names)

            return {'usuario': usuario, 'all_selos': all_selos}
    except Exception:
        pass

    # default anonymous usuario to avoid template errors
    default = {
        'nivel': 'Doador Iniciante',
        'progressoPercentual': 0,
        'next_level_name': None,
        'progress_text': '0/1',
        'participations_to_next': 1,
        'selos': [],
        'participacoes': [],
        'participation_count': 0
    }
    # also include all_selos for anonymous users (all locked)
    all_selos = [
        { 'nome': 'Primeira Doação', 'caminhoImagem': 'assets/selo-primeira-doacao.png', 'unlocked': False },
        { 'nome': 'Iniciante', 'caminhoImagem': 'assets/emblemas/1.png', 'unlocked': False },
        { 'nome': 'Comprometido', 'caminhoImagem': 'assets/emblemas/2.png', 'unlocked': False },
        { 'nome': 'Heróico', 'caminhoImagem': 'assets/emblemas/3.png', 'unlocked': False },
        { 'nome': 'Salvador de Vidas', 'caminhoImagem': 'assets/emblemas/4.png', 'unlocked': False },
        { 'nome': 'Tipo O Universal', 'caminhoImagem': 'assets/emblemas/5.png', 'unlocked': False },
        { 'nome': 'Fidelidade', 'caminhoImagem': 'assets/emblemas/6.png', 'unlocked': False },
    ]
    return {'usuario': default, 'all_selos': all_selos}

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
            user = User(usuario['id'], usuario['email'], usuario['nome'])
            login_user(user)
            logging.debug(f"Login bem-sucedido para usuário ID: {usuario['id']}")
            return redirect(url_for('perfil'))
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
    try:
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Buscar somente campanhas com status "Ativa"
        c.execute("SELECT * FROM campanhas WHERE status = 'Ativa' ORDER BY created_at DESC")
        campanhas_ativas = c.fetchall()
        conn.close()
        return render_template('campanhas.html', campanhas=campanhas_ativas)
    except Exception as e:
        logging.exception("Erro ao carregar campanhas")
        return render_template('campanhas.html', campanhas=[], erro=str(e))

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

@app.route('/campanhas_admin')
def campanhas_admin():
    return render_template('campanhas_admin.html')

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
    # Log the user in immediately after registration
    user = User(user_id, data.get('email'), data.get('nome'))
    login_user(user)
    logging.debug(f"Usuário cadastrado com ID: {user_id}")
    return redirect(url_for('perfil'))

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
        return render_template('perfil.html', error="Usuário não encontrado. Por favor, faça login ou cadastre-se novamente.", logged_in=False)
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
    autoriza_msg = 1 if data.get('autoriza_msg') == 'on' else 0
    autoriza_dados = 1 if data.get('autoriza_dados') == 'on' else 0

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO usuarios (
            nome, email, telefone, tipo_sanguineo, data_nascimento, genero,
            cep, endereco, ja_doou, primeira_vez, interesse,
            autoriza_msg, autoriza_dados, pontos
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (nome, email, telefone, tipo_sanguineo, data_nascimento, genero,
          cep, endereco, ja_doou, primeira_vez, interesse,
          autoriza_msg, autoriza_dados))
    conn.commit()
    
    # Pega o ID do usuário que acabamos de inserir
    user_id = c.lastrowid
    
    conn.close()
    
    # --- MUDANÇA AQUI ---
    # Em vez de redirecionar para 'conscientizacao',
    # vamos para a página de perfil do usuário que acabamos de criar.
    return redirect(url_for('perfil', usuario_id=user_id))


# ---
# NOVAS ROTAS (Adicionadas para suas páginas)
# ---

# Rota para a página de LOGIN
@app.route('/login')
def login():
    # Simplesmente renderiza o template de login
    return render_template('login.html')

# Rota para a página de CADASTRO
@app.route('/cadastro')
def cadastro():
    # Simplesmente renderiza o template de cadastro
    return render_template('cadastro.html')

# Rota para a página de campanhas
@app.route('/campanhas')
def campanhas(): # <-- MUDANÇA 1: O nome da função estava 'cadastro' e causou o erro
    # Simplesmente renderiza o template de campanhas
    return render_template('campanhas.html')

# ---
# MUDANÇA 2: Adicionando a rota da API que estava faltando.
# O script 'list_campanhas.js' precisa desta rota para funcionar.
# ---
@app.route('/api/campanhas')
def api_campanhas():
    """Fornece os dados das campanhas em JSON."""
    # No futuro, você pode buscar isso do banco de dados.
    # Por enquanto, são dados de exemplo.
    
    # Exemplo de dados (você pode adicionar/remover campanhas aqui)
    lista_campanhas = [
        {"id": 1, "nome": "Urgência O- para Hospital de Base", "tipo_sanguineo": "O-", "participantes": 15, "vagas": 20},
        {"id": 2, "nome": "Campanha Pediátrica (Todos os tipos)", "tipo_sanguineo": "Todos", "participantes": 45, "vagas": 100},
        {"id": 3, "nome": "Ajude o Sr. João (B+)", "tipo_sanguineo": "B+", "participantes": 5, "vagas": 10},
        {"id": 4, "nome": "Estoque Crítico A-", "tipo_sanguineo": "A-", "participantes": 8, "vagas": 15},
    ]
    
    # Calcula as estatísticas totais
    total_campanhas = len(lista_campanhas)
    total_participantes = sum(c['participantes'] for c in lista_campanhas)
    total_vagas = sum(c['vagas'] for c in lista_campanhas)
    vagas_disponiveis = total_vagas - total_participantes

    return jsonify({
        "campanhas": lista_campanhas,
        "estatisticas": {
            "totalCampanhas": total_campanhas,
            "totalParticipantes": total_participantes,
            "vagasDisponiveis": vagas_disponiveis
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
    return render_template('recuperar_senha.html', logged_in=False)


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


# Alias público para a página de conscientização (rota amigável)
@app.route('/conscientizacao')
def conscientizacao_alias():
    return redirect(url_for('conscientizacao'))


# Rota para o dashboard do admin
@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')

# Rota para página de enviar mensagem ao público-alvo (admin)
@app.route('/admin_nova_campanha')
def admin_nova_campanha():
    return render_template('admin_nova_campanha.html')

if __name__ == '__main__':
    app.run(debug=True)