import os
from flask import Flask, render_template, request, redirect, url_for, flash
import database
from validators import validar_pessoa, UFS_VALIDAS

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave-em-producao")

# Inicializa a tabela na primeira execução (idempotente, seguro para deploy)
try:
    database.init_db()
except Exception as e:
    # Não derruba o app se o banco ainda não estiver pronto (ex: primeiro build no Render)
    print(f"[init_db] Aviso: não foi possível inicializar a tabela ainda: {e}")


@app.route("/")
def index():
    pessoas = database.listar_pessoas()
    return render_template("index.html", pessoas=pessoas)


@app.route("/nova", methods=["GET", "POST"])
def nova():
    if request.method == "POST":
        try:
            dados = validar_pessoa(
                request.form.get("nome", ""),
                request.form.get("cidade", ""),
                request.form.get("estado", ""),
            )
        except ValueError as e:
            flash(str(e), "error")
            return render_template(
                "form.html",
                pessoa=request.form,
                modo="nova",
                ufs=UFS_VALIDAS,
            )

        database.criar_pessoa(dados["nome"], dados["cidade"], dados["estado"])
        flash("Pessoa cadastrada com sucesso!", "success")
        return redirect(url_for("index"))

    return render_template("form.html", pessoa=None, modo="nova", ufs=UFS_VALIDAS)


@app.route("/editar/<int:pessoa_id>", methods=["GET", "POST"])
def editar(pessoa_id):
    pessoa = database.buscar_pessoa(pessoa_id)
    if not pessoa:
        flash("Pessoa não encontrada.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            dados = validar_pessoa(
                request.form.get("nome", ""),
                request.form.get("cidade", ""),
                request.form.get("estado", ""),
            )
        except ValueError as e:
            flash(str(e), "error")
            return render_template(
                "form.html",
                pessoa=request.form,
                modo="editar",
                ufs=UFS_VALIDAS,
            )

        database.atualizar_pessoa(
            pessoa_id, dados["nome"], dados["cidade"], dados["estado"]
        )
        flash("Pessoa atualizada com sucesso!", "success")
        return redirect(url_for("index"))

    return render_template("form.html", pessoa=pessoa, modo="editar", ufs=UFS_VALIDAS)


@app.route("/deletar/<int:pessoa_id>", methods=["POST"])
def deletar(pessoa_id):
    if database.deletar_pessoa(pessoa_id):
        flash("Pessoa removida.", "success")
    else:
        flash("Não foi possível remover.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)