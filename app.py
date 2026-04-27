from flask import Flask, render_template, request, redirect, url_for, session
from adticket.config import Config
from adticket.extensions import db, migrate
from adticket.models import Evento, Usuario, Produto
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)


@app.route("/")
def escolha_usuario():
    return render_template("auth/escolha.html")


@app.route("/login/admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email, tipo="admin").first()

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            session["tipo"] = usuario.tipo
            return redirect(url_for("dashboard"))

        return "Login inválido"

    return render_template("auth/login_admin.html")


@app.route("/login/operador", methods=["GET", "POST"])
def login_operador():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email, tipo="operador").first()

        if usuario and check_password_hash(usuario.senha, senha):
            session["usuario_id"] = usuario.id
            session["tipo"] = usuario.tipo
            return redirect(url_for("dashboard"))

        return "Login inválido"

    return render_template("auth/login_operador.html")


@app.route("/dashboard")
def dashboard():
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    return render_template("dashboard/index.html")


@app.route("/eventos")
def lista_eventos():
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    eventos = Evento.query.all()
    return render_template("eventos/lista.html", eventos=eventos)


@app.route("/eventos/novo", methods=["GET", "POST"])
def novo_evento():
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    if session.get("tipo") != "admin":
        return "Acesso negado"

    if request.method == "POST":
        data_inicio_str = request.form.get("data_inicio")
        data_fim_str = request.form.get("data_fim")

        data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date() if data_inicio_str else None
        data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date() if data_fim_str else None

        try:
            meta_financeira = float(request.form.get("meta", 0))
        except:
            meta_financeira = 0

        evento = Evento(
            nome=request.form.get("nome"),
            descricao=request.form.get("descricao"),
            data_inicio=data_inicio,
            data_fim=data_fim,
            departamento=request.form.get("departamento"),
            meta_financeira=meta_financeira,
            status="ativo"
        )

        db.session.add(evento)
        db.session.commit()

        return redirect(url_for("lista_eventos"))

    return render_template("eventos/cadastro_ev.html")


@app.route("/produtos")
def lista_produtos():
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    produtos = Produto.query.all()
    return render_template("produtos/lista_p.html", produtos=produtos)


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    if session.get("tipo") != "admin":
        return "Acesso negado"

    if request.method == "POST":
        produto = Produto(
            nome=request.form.get("nome"),
            descricao=request.form.get("descricao"),
            preco=float(request.form.get("preco")),
            possui_tamanhos=True if request.form.get("tamanhos") == "on" else False,
            controla_estoque=True if request.form.get("estoque") == "on" else False
        )

        db.session.add(produto)
        db.session.commit()

        return redirect(url_for("lista_p_produtos"))

    return render_template("produtos/cadastro_p.html")


@app.route("/produtos/<int:id>")
def detalhe_produto(id):
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    produto = Produto.query.get_or_404(id)
    return render_template("produtos/detalhe.html", produto=produto)


@app.route("/produtos/<int:id>/editar", methods=["GET", "POST"])
def editar_produto(id):
    if "usuario_id" not in session:
        return redirect(url_for("escolha_usuario"))

    if session.get("tipo") != "admin":
        return "Acesso negado"

    produto = Produto.query.get_or_404(id)

    if request.method == "POST":
        produto.nome = request.form.get("nome")
        produto.descricao = request.form.get("descricao")
        produto.preco = float(request.form.get("preco"))
        produto.possui_tamanhos = True if request.form.get("tamanhos") == "on" else False
        produto.controla_estoque = True if request.form.get("estoque") == "on" else False

        db.session.commit()
        return redirect(url_for("lista_p_produtos"))

    return render_template("produtos/editar.html", produto=produto)


@app.route("/usuarios/admin/novo", methods=["GET", "POST"])
def novo_admin():
    if "usuario_id" not in session or session.get("tipo") != "admin":
        return "Acesso negado"

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = generate_password_hash(request.form.get("senha"))

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            return "Email já cadastrado"

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo="admin"
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("usuarios/cadastro_admin.html")


@app.route("/usuarios/novo", methods=["GET", "POST"])
def novo_usuario():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = generate_password_hash(request.form.get("senha"))

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            return "Email já cadastrado"

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo="operador"
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for("login_operador"))

    return render_template("usuarios/cadastro_operador.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("escolha_usuario"))


if __name__ == "__main__":
    app.run(debug=True)