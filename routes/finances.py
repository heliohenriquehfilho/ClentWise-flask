from flask import Blueprint, request, session, flash, redirect, url_for, render_template


"""
def calcular_valor_total(preco, desconto, quantidade):
    return round((preco - (preco * (desconto / 100))) * quantidade, 2)
"""

finances_bp = Blueprint('finances', __name__)

@finances_bp.route('/finances', methods=['GET', 'POST'])
def finances():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))
    return render_template('finances.html')