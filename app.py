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

# --- Rotas Principais ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    print("Dados recebidos:", data) # Ótimo para debug!

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


# Rota para a página de PERFIL
# Ela pode receber um ID (ex: /perfil/1)
@app.route('/perfil/')
@app.route('/perfil/<int:usuario_id>')
def perfil(usuario_id=None):
    # Esta página é dinâmica! Ela precisa buscar os dados do usuário.
    
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row # Isso permite acessar os dados por nome da coluna
    c = conn.cursor()
    
    usuario_data = None
    if usuario_id:
        # Busca o usuário específico
        c.execute('SELECT * FROM usuarios WHERE id = ?', (usuario_id,))
        usuario_data = c.fetchone()
    else:
        # Se nenhum ID for passado, busca o ÚLTIMO usuário cadastrado
        c.execute('SELECT * FROM usuarios ORDER BY id DESC LIMIT 1')
        usuario_data = c.fetchone()
    
    conn.close()
    
    # Se o banco estiver vazio ou o ID não for encontrado
    if usuario_data is None:
        # Você pode renderizar uma página de erro ou um perfil de "Usuário não encontrado"
        # Por enquanto, vamos redirecionar para o cadastro
        return redirect(url_for('cadastro'))

    # Transforma o dado do SQLite em um dicionário (fácil de usar no HTML)
    usuario = dict(usuario_data)
    
    # Adiciona a lógica de gamificação que será usada no template
    usuario["nivel"] = "Doador Iniciante" # Exemplo
    usuario["progressoPercentual"] = usuario["pontos"] * 10 # Exemplo
    
    usuario["selos"] = []
    if usuario["ja_doou"] == 'sim':
        usuario["selos"].append({"nome": "Primeira Doação!", "caminhoImagem": "assets/selo-primeira-doacao.png"})
    # Adicione mais lógica de selos aqui...

    # Passamos o dicionário 'usuario' para o template 'perfil.html'
    # Agora no HTML você pode usar {{ usuario.nome }}, {{ usuario.email }}, etc.
    return render_template('perfil.html', usuario=usuario)


# Rota para 'conscientizacao' (Seu código original, caso você queira usá-la)
@app.route('/conscientizacao_original') # Mudei o nome para não conflitar
def conscientizacao():
    nome = request.args.get('nome', 'Doador')
    # ... (seu código de busca de pontos) ...
    # Lembre-se de criar o 'conscientizacao.html' na pasta templates
    return render_template('conscientizacao.html', nome=nome, pontos=0)


# Alias público para a página de conscientização (rota amigável)
@app.route('/conscientizacao')
def conscientizacao_alias():
    return redirect(url_for('conscientizacao'))


# Rota para o dashboard do admin
@app.route('/dashboard_admin')
def dashboard_admin():
    return render_template('dashboard_admin.html')


if __name__ == '__main__':
    app.run(debug=True)