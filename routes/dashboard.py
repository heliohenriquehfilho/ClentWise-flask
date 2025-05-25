from flask import Flask, Blueprint, session, redirect, url_for, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login.login'))
    return render_template('dashboard.html', user_id=session['user_id'])
