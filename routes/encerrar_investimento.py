from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.obter_dados_tabela import obter_dados_tabela
from routes.load_supabase import load_supabase
import pandas as pd

supabase = load_supabase()
encerrar_investmento_bp = Blueprint('encerrar_investmento', __name__)

@encerrar_investmento_bp.route('/encerrar_investmento', methods=['GET', 'POST'])
def encerrar_investimento():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redireciona para login se o usuário não estiver autenticado.

    if request.method == "POST":
        investimento_id = request.form.get('investimento_id')

        if not investimento_id:
            return "ID do investimento não fornecido.", 400  # Retorna erro se o ID for inválido.

        # Atualiza o status do investimento para encerrado
        supabase.table("investimento").update({"encerrado": True}).eq("investimento__c", investimento_id).execute()
        investimentos = obter_dados_tabela("investimento", user_id)
        investimentos_df = pd.DataFrame(investimentos)
        investimentos_ativos = investimentos_df[investimentos_df['encerrado'] == False]
        investimento_encerrado = investimentos_df[investimentos_df['encerrado'] == True]

        return render_template(
            'investments.html', 
            investimentos_df=investimentos_ativos.to_dict('records'),
            investimento_encerrado=investimento_encerrado.to_dict('records'))

    investimentos = obter_dados_tabela("investimento", user_id)
    investimentos_df = pd.DataFrame(investimentos)
    investimentos_ativos = investimentos_df[investimentos_df['encerrado'] == False]
    investimento_encerrado = investimentos_df[investimentos_df['encerrado'] == True]

    return render_template(
        'investments.html', 
        investimentos_df=investimentos_ativos.to_dict('records'),
        investimento_encerrado=investimento_encerrado.to_dict('records'))