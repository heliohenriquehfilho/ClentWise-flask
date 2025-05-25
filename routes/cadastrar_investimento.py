from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from flask import jsonify
from routes.obter_dados_tabela import obter_dados_tabela
from routes.load_supabase import load_supabase
import pandas as pd

supabase = load_supabase()
cadastrar_investmento_bp = Blueprint('cadastrar_investmento', __name__)

@cadastrar_investmento_bp.route('/cadastrar_investmento', methods=['GET', 'POST'])
def cadastrar_investimento():
    user_id = session.get('user_id')

    if request.method == "POST":
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        valor = float(request.form.get("valor"))
        tipo = request.form.get("pagamento")
        duracao = int(request.form.get("duracao"))

        valor_total = duracao * valor

        investimento = {
            "user_id": user_id,
            "nome": nome,
            "descricao": descricao,
            "valor": valor,
            "tipo_pagamento": tipo,
            "duracao": duracao,
            "valor_total": valor_total,
            "status": True,
            "pagamentos": 0,
            "encerrado": False,
            "historico_pagamentos": []
        }

        try:
            supabase.table("investimento").insert(investimento).execute()
            flash("Venda cadastrada com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao cadastrar venda: {e}", "fail")

        investimentos = obter_dados_tabela("investimento", user_id)
        investimentos_df = pd.DataFrame(investimentos)
        investimentos_ativos = investimentos_df[investimentos_df['encerrado'] == False]
        investimento_encerrado = investimentos_df[investimentos_df['encerrado'] == True]

        return render_template(
            'investments.html', 
            investimentos_df=investimentos_ativos.to_dict('records'),
            investimento_encerrado=investimento_encerrado.to_dict('records'), 
            investimento=investimento)