from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.form.to_dict()
    print("Dados recebidos:", data)

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
    conn.close()

    return redirect(url_for('conscientizacao', nome=nome))


@app.route('/conscientizacao')
def conscientizacao():
    nome = request.args.get('nome', 'Doador')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT pontos FROM usuarios WHERE nome = ?', (nome,))
    row = c.fetchone()
    pontos = row[0] if row else 0
    conn.close()

    return render_template('conscientizacao.html', nome=nome, pontos=pontos)


if __name__ == '__main__':
    app.run(debug=True)
