from . import db
from datetime import datetime, timezone

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    dinheiro = db.Column(db.Integer, nullable=False)
    cliques = db.Column(db.Integer, default=0)
    ultima_atualizacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    limite_off = db.Column(db.Integer, nullable=False)

class Itens(db.Model):
    id_item = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(200), unique=True, nullable=False)
    preco = db.Column(db.Float, nullable=False)

class Inventario(db.Model):
    id_inventario =  db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('itens.id_item'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)