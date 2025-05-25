from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.obter_dados_tabela import obter_dados_tabela
from routes.load_supabase import load_supabase
import pandas as pd
import json

supabase = load_supabase()
investments_bp = Blueprint('investments', __name__)

@investments_bp.route('/investments', methods=['GET', 'POST'])
def investments():
    user_id = session['user_id']

    # Obtém os investimentos do banco de dados
    investimentos = obter_dados_tabela("investimento", user_id)
    investimentos_df = pd.DataFrame(investimentos)
    investimentos_ativos = investimentos_df[investimentos_df['encerrado'] == False]
    investimento_encerrado = investimentos_df[investimentos_df['encerrado'] == True]

    investimento_selecionado = request.args.get('investimento_selecionado')

    if investimento_selecionado:
        # Use .iterrows() para iterar pelas linhas do DataFrame
        investimento_series = investimentos_df[investimentos_df['investimento__c'] == investimento_selecionado]

        if not investimento_series.empty:
            investimento = investimento_series.iloc[0].to_dict()
            historico_pagamentos = investimento.get("historico_pagamentos", [])
            if isinstance(historico_pagamentos, str):
                historico_pagamentos = json.loads(historico_pagamentos)
            pagamentos = pd.DataFrame(historico_pagamentos)
            pagamentos_vazios = pagamentos.empty  # Verifica se o DataFrame de pagamentos está vazio

            investimentos = obter_dados_tabela("investimento", user_id)
            investimentos_df = pd.DataFrame(investimentos)
            investimentos_ativos = investimentos_df[investimentos_df['encerrado'] == False]
            investimento_encerrado = investimentos_df[investimentos_df['encerrado'] == True]

            return render_template(
                'investments.html',
                investimentos_df=investimentos_ativos.to_dict('records'),
                investimento_encerrado=investimento_encerrado.to_dict('records'),
                investimento=investimento,
                pagamentos=pagamentos,
                pagamentos_vazios=pagamentos_vazios,
            )
        
        if investimento is not None:
            historico_pagamentos = investimento.get("historico_pagamentos", [])
            if isinstance(historico_pagamentos, str):
                historico_pagamentos = json.loads(historico_pagamentos)
            pagamentos = pd.DataFrame(historico_pagamentos)
            pagamentos_vazios = pagamentos.empty  # Verifica se o DataFrame de pagamentos está vazio

            investimentos = obter_dados_tabela("investimento", user_id)
            investimentos_df = pd.DataFrame(investimentos)
            investimentos_ativos = investimentos_df[investimentos_df['encerrado'] == False]
            investimento_encerrado = investimentos_df[investimentos_df['encerrado'] == True]

            return render_template(
                'investments.html', 
                investimentos_df=investimentos_ativos.to_dict('records'),
                investimento_encerrado=investimento_encerrado.to_dict('records'), 
                investimento=investimento, 
                pagamentos=pagamentos, 
                pagamentos_vazios=pagamentos_vazios)

    return render_template(
        'investments.html', 
        investimentos_df=investimentos_ativos.to_dict('records'),
        investimento_encerrado=investimento_encerrado.to_dict('records'))