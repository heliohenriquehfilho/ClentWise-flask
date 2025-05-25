from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.load_supabase import load_supabase

supabase = load_supabase()
editar_cliente_bp = Blueprint('editar_cliente', __name__)

@editar_cliente_bp.route("/editar_cliente", methods=["GET", "POST"])
def editar_cliente():
    try:
        client_id = request.form.get("client_id")
        nome = request.form.get("nome")
        contato = request.form.get("contato")
        email = request.form.get("email")
        ativo = request.form.get("ativo") == "on"  # Checkbox retorna "on" se marcado
        genero = request.form.get("genero")

        # Atualizando cliente no Supabase
        cliente_atualizado = {
            "nome": nome,
            "contato": contato,
            "email": email,
            "ativo": ativo,
            "genero": genero,
        }

        supabase.table("clientes").update(cliente_atualizado).eq("client__c", client_id).execute()
        flash("Cliente atualizado com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao atualizar cliente: {e}", "danger")

    return render_template("editar_clientes.html")