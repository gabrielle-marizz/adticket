from adticket.extensions import db
from datetime import datetime

# =====================
# USUÁRIOS
# =====================
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    senha = db.Column(db.String, nullable=False)
    tipo = db.Column(db.String, nullable=False)  # define se é admin ou operador

    # lista de pedidos registrados por esse usuário
    pedidos = db.relationship("Pedido", backref="usuario", lazy=True)


# =====================
# EVENTOS
# =====================
class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descricao = db.Column(db.Text)
    data_inicio = db.Column(db.Date)
    data_fim = db.Column(db.Date)

    # meta financeira que o evento deseja alcançar
    meta_financeira = db.Column(db.Float, nullable=False)

    # departamento responsável pelo evento (ex: UFADEC)
    departamento = db.Column(db.String, nullable=False)

    # indica se o evento ainda está ativo ou já foi encerrado
    status = db.Column(db.String, nullable=False)

    # caminho da imagem do cartaz do evento
    imagem = db.Column(db.String)

    # produtos disponíveis nesse evento
    produtos = db.relationship("EventoProduto", backref="evento", lazy=True)

    # pedidos feitos dentro desse evento
    pedidos = db.relationship("Pedido", backref="evento", lazy=True)

    # relatórios gerados para esse evento
    relatorios = db.relationship("Relatorio", backref="evento", lazy=True)


# =====================
# PRODUTOS
# =====================
class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    descricao = db.Column(db.Text)

    # valor base do produto
    preco = db.Column(db.Float, nullable=False)

    # define se o produto usa tamanhos (ex: camisas)
    possui_tamanhos = db.Column(db.Boolean, nullable=False)

    # define se o produto possui controle de estoque
    controla_estoque = db.Column(db.Boolean, nullable=False)

    # relação com eventos onde o produto está disponível
    eventos = db.relationship("EventoProduto", backref="produto", lazy=True)


# =====================
# RELAÇÃO EVENTO-PRODUTO
# =====================
class EventoProduto(db.Model):
    __tablename__ = "evento_produto"

    id = db.Column(db.Integer, primary_key=True)

    # ligação com o evento
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False)

    # ligação com o produto
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)

    # quantidade disponível (usado apenas quando há controle de estoque)
    estoque = db.Column(db.Integer)


# =====================
# TAMANHOS
# =====================
class Tamanho(db.Model):
    __tablename__ = "tamanhos"

    id = db.Column(db.Integer, primary_key=True)

    # exemplos: PP, P, M, G, GG, XG, XGG, UNICO
    nome = db.Column(db.String, nullable=False)


# =====================
# PEDIDOS
# =====================
class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)

    # evento ao qual o pedido pertence
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False)

    # dados do cliente
    nome_cliente = db.Column(db.String, nullable=False)
    telefone = db.Column(db.String, nullable=False)

    # forma de pagamento escolhida
    forma_pagamento = db.Column(db.String)

    # detalhe do pagamento em caso de cartão
    tipo_pagamento_cartao = db.Column(db.String)

    # situação atual do pedido (reservado, confirmado ou cancelado)
    status_pagamento = db.Column(db.String, nullable=False)

    # define se o pedido é de um cliente comum ou do departamento
    tipo_pedido = db.Column(db.String, nullable=False)

    # usuário que registrou o pedido
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # valor total do pedido
    valor_total = db.Column(db.Float)

    # data limite para pagamento em caso de reserva
    data_validade_reserva = db.Column(db.DateTime)

    # data em que o pedido foi criado
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)

    # lista de itens que fazem parte desse pedido
    itens = db.relationship("ItemPedido", backref="pedido", lazy=True)

    # histórico de alterações desse pedido
    historico = db.relationship("HistoricoPedido", backref="pedido", lazy=True)


# =====================
# ITENS DO PEDIDO
# =====================
class ItemPedido(db.Model):
    __tablename__ = "itens_pedido"

    id = db.Column(db.Integer, primary_key=True)

    # referência ao pedido
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)

    # produto comprado
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)

    # tamanho escolhido
    tamanho_id = db.Column(db.Integer, db.ForeignKey("tamanhos.id"), nullable=False)

    # quantidade comprada
    quantidade = db.Column(db.Integer, nullable=False)

    # preço no momento da venda
    preco_unitario = db.Column(db.Float, nullable=False)

    produto = db.relationship("Produto")
    tamanho = db.relationship("Tamanho")


# =====================
# HISTÓRICO DE PEDIDOS
# =====================
class HistoricoPedido(db.Model):
    __tablename__ = "historico_pedido"

    id = db.Column(db.Integer, primary_key=True)

    # pedido relacionado à ação
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)

    # usuário que realizou a ação
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # tipo da ação realizada (criação, confirmação, cancelamento, etc.)
    acao = db.Column(db.String, nullable=False)

    # data e hora da ação
    data = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario")


# =====================
# RELATÓRIOS
# =====================
class Relatorio(db.Model):
    __tablename__ = "relatorios"

    id = db.Column(db.Integer, primary_key=True)

    # evento ao qual o relatório pertence
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False)

    # usuário que gerou o relatório
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # título do relatório
    titulo = db.Column(db.String, nullable=False)

    # descrição ou observações do relatório
    descricao = db.Column(db.Text)

    # caminho do arquivo PDF gerado
    caminho_pdf = db.Column(db.String)

    # data em que o relatório foi criado
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario")