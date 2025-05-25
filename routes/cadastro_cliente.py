from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.load_supabase import load_supabase
import pandas as pd

supabase = load_supabase()
cadastro_cliente_bp = Blueprint('cadastro_cliente', __name__)

@cadastro_cliente_bp.route("/cadastro_cliente", methods=["GET", "POST"])
def cadastro_cliente():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        opcao_cadastro = request.form.get("opcao_cadastro")

        if opcao_cadastro == "manual":
            cliente = {
                "nome": request.form.get("nome"),
                "contato": request.form.get("contato"),
                "endereco": request.form.get("endereco"),
                "email": request.form.get("email"),
                "user_id": session['user_id']
            }

            if all(cliente.values()):
                try:
                    resposta = supabase.table("clientes") \
                    .select("id") \
                    .filter("nome", "eq", cliente["nome"]) \
                    .filter("contato", "eq", cliente["contato"]) \
                    .filter("endereco", "eq", cliente["endereco"]) \
                    .filter("email", "eq", cliente["email"]) \
                    .filter("user_id", "eq", cliente["user_id"]) \
                    .execute()

                    if resposta.data:
                        flash("Cliente Já cadastrado!", "danger")

                    else:
                        supabase.table("clientes").insert(cliente).execute()
                        flash("Cliente cadastrado com sucesso!", "success")

                except Exception as e:
                    flash(f"Erro ao cadastrar cliente: {e}", "danger")
                    
            else:
                flash("Por favor, preencha todos os campos.", "danger")

        elif opcao_cadastro == "csv":
            file = request.files.get("csv_file")
            if file and file.filename.endswith(".csv"):
                try:
                    data = pd.read_csv(file)
                    for _, row in data.iterrows():
                        cliente = {
                            "nome": row.get("nome"),
                            "contato": row.get("contato"),
                            "endereco": row.get("endereco", ""),
                            "email": row.get("email"),
                            "user_id": session['user_id']
                        }

                        if all(
                            [
                                cliente["nome"],
                                cliente["contato"],
                                cliente["email"],
                            ]):

                            resposta = supabase.table("clientes")\
                            .select("id") \
                            .filter("nome", "eq", cliente["nome"]) \
                            .filter("contato", "eq", cliente["contato"]) \
                            .filter("email", "eq", cliente["email"]) \
                            .filter("user_id", "eq", cliente["user_id"]) \
                            .execute()

                            if not resposta.data:
                                supabase.table("clientes").insert(cliente).execute()
                    flash("Importação concluída!", 'success')

                except Exception as e:
                    flash(f"Erro ao processar o CSV: {e}", "danger")
                
            else:
                flash("Por favor, envie um arquivo CSV válido.", "danger")

    return render_template("clientes.html")
