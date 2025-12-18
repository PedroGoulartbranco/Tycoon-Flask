from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash 
from .models import Usuario, Itens, Inventario
from . import db
from datetime import datetime, timezone
from math import floor

views_bp = Blueprint("views", __name__)
lista_preco_multiplicadores = [100, 200, 400, 600, 1000, 1300, 1900, 2300, 3000, 3500]
lista_preco_clique_automaticos_1 = [150, 300, 400, 520, 600, 780, 1000, 1200, 1500, 2000]
lista_tempo_off = [3600, 7200, 10800, 14400, 18000, 21600, 25200, 28800, 32400, 36000]

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
            cliques = 0,
            limite_off = 0
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

    valor_por_clique = 1

    aumentar_clique = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=1).first()
    if aumentar_clique:
        valor_por_clique = aumentar_clique.quantidade

    horario_atual = datetime.now(timezone.utc)
    segundos_passados = (horario_atual - usuario_atual.ultima_atualizacao.replace(tzinfo=timezone.utc)).total_seconds()
    quantidade_de_cliques_automaticos = 0

    clique_automatico_1 = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=2).first()
    if clique_automatico_1:
        quantidade_de_cliques_automaticos = clique_automatico_1.quantidade
    else:
        quantidade_de_cliques_automaticos = 0
    dinheiro_ganho_passivo = segundos_passados * quantidade_de_cliques_automaticos
    dinheiro_ganho_passivo = floor(dinheiro_ganho_passivo)

    usuario_atual.dinheiro += int(valor_por_clique + dinheiro_ganho_passivo)
    usuario_atual.cliques += 1
    usuario_atual.ultima_atualizacao = horario_atual

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

    if item.id_item == 1: #Caso for um multiplicador
        jogador_tem_ou_nao_tem_multiplicador =  Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=1).first()
        if jogador_tem_ou_nao_tem_multiplicador:
            if jogador_tem_ou_nao_tem_multiplicador.quantidade >= 10:
                return jsonify({"sucesso": False, "erro": "Limite Máximo Já Atingindo"})
            if usuario.dinheiro < lista_preco_multiplicadores[jogador_tem_ou_nao_tem_multiplicador.quantidade - 1]:
                return jsonify({"sucesso": False, "erro": "Dinheiro insuficiente"})
            usuario.dinheiro -= lista_preco_multiplicadores[jogador_tem_ou_nao_tem_multiplicador.quantidade - 1]
            jogador_tem_ou_nao_tem_multiplicador.quantidade += 1
        else:
            if usuario.dinheiro < lista_preco_multiplicadores[0]:
                return jsonify({"sucesso": False, "erro": "Dinheiro insuficiente"})
            item_comprado = Inventario (
            usuario_id = usuario.id,
            item_id = id_item,
            quantidade = 1
        )
            usuario.dinheiro -= lista_preco_multiplicadores[0]
            db.session.add(item_comprado)
    else:
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

@views_bp.route("/ver_multiplicador", methods=['GET'])
def ver_multiplicador():
    aumentar_clique = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=1).first()
    if aumentar_clique:
        return jsonify({"multiplicador": aumentar_clique.quantidade, "preco": lista_preco_multiplicadores[aumentar_clique.quantidade - 1]})
    return jsonify({"multiplicador": 0, "preco": lista_preco_multiplicadores[0]})

@views_bp.route("/comprar_clique_automatico", methods=['POST'])
def comprar_clique_automatico():
    item = Itens.query.get(2)
    usuario = Usuario.query.filter_by(id=session['usuario_id']).first()

    clique_automatico_no_inventario = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=2).first()
    if clique_automatico_no_inventario:
        if clique_automatico_no_inventario.quantidade >= 10:
            return jsonify({"sucesso": False, "erro": "Limite Máximo"})
        if usuario.dinheiro < lista_preco_clique_automaticos_1[clique_automatico_no_inventario.quantidade - 1]:
            return jsonify({"sucesso": False, "erro": "Dinheiro insuficiente"})
        usuario.dinheiro -= lista_preco_clique_automaticos_1[clique_automatico_no_inventario.quantidade - 1]
        clique_automatico_no_inventario.quantidade += 1
    else:
        if usuario.dinheiro < lista_preco_clique_automaticos_1[0]:
            return jsonify({"sucesso": False, "erro": "Dinheiro insuficiente"})
        usuario.dinheiro -= lista_preco_clique_automaticos_1[0]
        automatico_comprado = Inventario (
            usuario_id = usuario.id,
            item_id = 2,
            quantidade = 1
        )
        db.session.add(automatico_comprado)
    db.session.commit()
    return jsonify({"sucesso": True, "novo_dinheiro": usuario.dinheiro,"mensagem": f"Você comprou {item.nome}!"})

@views_bp.route("/ver_automaticos_1", methods=['GET'])
def ver_automaticos_1():
    numero_de_automaticos = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=2).first()
    if numero_de_automaticos:
        return jsonify({"numero_automatico": numero_de_automaticos.quantidade, "preco": lista_preco_clique_automaticos_1[numero_de_automaticos.quantidade - 1]})
    return jsonify({"numero_automatico": 0, "preco": lista_preco_clique_automaticos_1[0]})

@views_bp.route("/atualizar_dinheiro", methods=['GET'])
def atualizar_dinheiro():
    usuario_atual = Usuario.query.get(session["usuario_id"])

    horario_atual = datetime.now(timezone.utc)
    segundos_passados = (horario_atual - usuario_atual.ultima_atualizacao.replace(tzinfo=timezone.utc)).total_seconds()
    quantidade_de_cliques_automaticos = 0

    clique_automatico_1 = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=2).first()
    limite_off_usuario = Inventario.query.filter_by(usuario_id=session["usuario_id"], item_id=2).first()
    if clique_automatico_1:
        quantidade_de_cliques_automaticos = clique_automatico_1.quantidade
    else:
        quantidade_de_cliques_automaticos = 0
    if segundos_passados > lista_tempo_off[usuario_atual.limite_off]: #Limita o tempo fora
        segundos_passados = lista_tempo_off[usuario_atual.limite_off]

    dinheiro_ganho_passivo = segundos_passados * quantidade_de_cliques_automaticos
    dinheiro_ganho_passivo = floor(dinheiro_ganho_passivo)

    usuario_atual.dinheiro += dinheiro_ganho_passivo
    usuario_atual.ultima_atualizacao = horario_atual

    db.session.commit()

    return jsonify({"dinheiro": usuario_atual.dinheiro, "tempo_off": floor(segundos_passados / 3600), "limite_off": limite_off_usuario.quantidade, "dinheiro_off": dinheiro_ganho_passivo})
