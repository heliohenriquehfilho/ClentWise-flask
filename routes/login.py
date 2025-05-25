from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.load_supabase import load_supabase

supabase = load_supabase()
login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = supabase.auth.sign_in_with_password({
                'email': email,
                'password': password})
            if response.user:
                session['user_id'] = response.user.id
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for('dashboard.dashboard'))
        
        except Exception as e:
            flash(f"Erro ao autenticar: {e}", "error")
        
    return render_template('login.html')