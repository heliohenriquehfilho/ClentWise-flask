from routes.atualizar_investimento import atualizar_investmentos_bp
from routes.cadastrar_investimento import cadastrar_investmento_bp
from routes.encerrar_investimento import encerrar_investmento_bp
from routes.deletar_investimento import deletar_investimento_bp
from routes.cadastro_cliente import cadastro_cliente_bp
from routes.edit_cliente import editar_cliente_bp
from flask import Flask, render_template, session
from routes.investments import investments_bp
from routes.dashboard import dashboard_bp
from routes.finances import finances_bp
from routes.clientes import clientes_bp
from routes.register import register_bp
from routes.vendas import vendas_bp
from routes.logout import logout_bp
from routes.login import login_bp
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Registrar Blueprints com prefixos opcionais
app.register_blueprint(login_bp, url_prefix='/login')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(register_bp, url_prefix='/register')
app.register_blueprint(logout_bp, url_prefix='/logout')
app.register_blueprint(cadastro_cliente_bp, url_prefix="/cadastro_cliente")
app.register_blueprint(vendas_bp, url_prefix="/sales")
app.register_blueprint(clientes_bp, url_prefix="/clientes")
app.register_blueprint(editar_cliente_bp, url_prefix="/editar_cliente")
app.register_blueprint(investments_bp, url_prefix="/investments")
app.register_blueprint(atualizar_investmentos_bp, url_prefix="/atualizar_investmentos")
app.register_blueprint(encerrar_investmento_bp, url_prefix="/encerrar_investmento")
app.register_blueprint(deletar_investimento_bp, url_prefix="/deletar_investimento")
app.register_blueprint(cadastrar_investmento_bp, url_prefix="/cadastrar_investimento")
app.register_blueprint(finances_bp, url_prefix="/finances")
 
@app.route('/')
def index():
    if 'user_id' in session:
        return render_template('dashboard.html', user_id=session.get('user_id'))
    return render_template('login.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)