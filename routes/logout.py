from flask import Blueprint, request, session, flash, redirect, url_for, render_template


logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for('index'))