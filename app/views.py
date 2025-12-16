from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from .models import Usuario, Itens, Inventario
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
            dinheiro = 0,
            cliques = 0
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
    return render_template("jogo.html", nome=usuario_atual.nome, dinheiro=usuario_atual.dinheiro, cliques=usuario_atual.cliques)

@views_bp.route("/clique", methods=['POST'])
def clique():
    if "usuario_id" not in session:
        return redirect(url_for("views.cadastro"))
    
    usuario_atual = Usuario.query.get(session["usuario_id"])
    usuario_atual.dinheiro += 1
    usuario_atual.cliques += 1

    db.session.commit()

    return jsonify({'dinheiro': usuario_atual.dinheiro, 'cliques': usuario_atual.cliques})

@views_bp.route("/top10", methods=['GET'])
def top10():
    lista_usuarios = Usuario.query.order_by(Usuario.dinheiro.desc()).limit(10).all()

    ranking = []

    for usuario in lista_usuarios:
        ranking.append({
            "nome": usuario.nome,
            "dinheiro": usuario.dinheiro
        })

    return jsonify(ranking)

@views_bp.route("/comprar/<int:id_item>", methods=['POST'])
def comprar_item(id_item):
    usuario = Usuario.query.filter_by(id=session['usuario_id']).first()
    item = Itens.query.get(id_item)

    if usuario.dinheiro < item.preco:
        return jsonify({"sucesso": False, "erro": "Dinheiro insuficiente"})
    
    usuario.dinheiro -= item.preco

    item_comprado = Inventario (
        usuario_id = usuario.id,
        item_id = id_item,
        quantidade = 1
    )

    db.session.add(item_comprado)
    db.session.commit()
    return jsonify({"sucesso": True, "novo_dinheiro": usuario.dinheiro,"mensagem": f"Você comprou {item.nome}!"})