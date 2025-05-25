from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.load_supabase import load_supabase
import re

supabase = load_supabase()
register_bp = Blueprint('register', __name__)

def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(\.[a-zA-Z]{2,})*$'
    return re.match(email_regex, email) is not None

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if not is_valid_email(email):
            flash("Email inválido. Certifique-se de incluir um domínio válido", "error")

        else:
            try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                if response.user:
                    flash("Usuário registrado com sucesso! Confirme o email recebido.", "success")
                    return redirect(url_for('login.login'))
                else:
                    flash("Erro ao registrar usuário.", "error")
            
            except Exception as e:
                flash(f"Erro ao registrar usuário: {e}", "error")

    return render_template('login.html')