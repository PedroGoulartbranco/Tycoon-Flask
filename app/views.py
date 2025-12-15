from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash 
from .models import Usuario
from . import db

views_bp = Blueprint("views", __name__)

@views_bp.route("/login", methods=['GET', 'POST'])
def login():
    erro = None
    
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        usuario_ja_existe = Usuario.query.filter_by(nome=nome).first()
        if not usuario_ja_existe:
            erro = "Nome de usuario errado"
        elif not check_password_hash(usuario_ja_existe.senha, senha):
            erro =  "Senha incorreta"
        else:
            session["usuario_id"] = usuario_ja_existe.id
            return redirect(url_for("views.jogo"))
    
    return render_template("login.html", erro=erro)

@views_bp.route("/", methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']

        usuario_ja_existe = Usuario.query.filter_by(nome=nome).first()
        if usuario_ja_existe:
            return 'Usuario já existe!'

        senha_segura = generate_password_hash(senha)

        novo_usuario = Usuario (
            nome= nome,
            senha= senha_segura,
            dinheiro = 0
        )

        db.session.add(novo_usuario)
        db.session.commit()

        session["usuario_id"] = novo_usuario.id

        return redirect(url_for('views.jogo'))

    return render_template("cadastro.html")

@views_bp.route("/menu", methods=['GET'])
def jogo():
    if "usuario_id" not in session:
        return redirect(url_for("views.cadastro"))
    
    usuario_atual = Usuario.query.get(session["usuario_id"])
    return render_template("jogo.html", nome=usuario_atual.nome, dinheiro=usuario_atual.dinheiro)