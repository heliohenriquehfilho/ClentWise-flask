from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from datetime import datetime
import pandas as pd
import json
from routes.obter_dados_tabela import obter_dados_tabela
from routes.load_supabase import load_supabase

financeiro_bp = Blueprint('financeiro', __name__, template_folder='templates')
supabase = load_supabase()

# suas traduções
translations = {
    "Português": { 
        "title": "Financeiro",
        "menu_register_expense": "Cadastrar Despesa",
        "menu_financial_insights": "Insights Financeiros",
        "register_expense": "Aba de Despesas",
        "select_expense": "Selecione a despesa",
        "water_supplier": "Fornecedor de Àgua",
        "electricity_supplier": "Fornecedor de Luz",
        "internet_supplier": "Fornecedor de Internet",
        "supplier": "Fornecedor",
        "bill": "Boleto",
        "salary_payment": "Pagamento de Funcionário",
        "expense_value": "Valor da conta",
        "payment_date": "Data do pagamento",
        "payment_method": "Forma de pagamento",
        "payment_method_options": ["Débito", "Débito Automático", "Dinheiro", "Pix", "Boleto"],
        "add_supplier": "Qual o fornecedor: ",
        "description": "Descrição: ",
        "register_expense_button": "Cadastrar despesa",
        "expense_registered": "Conta cadastrada!",
        "error_registering_expense": "Erro ao salvar a conta: {e}",
        "no_sales": "Não há vendas registradas.",
        "no_expenses": "Não há despesas registradas.",
        "no_investments": "Não há investimentos registrados.",
        "sales_total": "Total de vendas no mês de {month}: R$ {total:.2f}",
        "expenses_total": "Total de despesas no mês de {month}: R$ {total:.2f}",
        "investments_paid_total": "Total de investimentos pagos no mês de {month}: R$ {total:.2f}",
        "campaigns_paid_total": "Total de campanhas pagos no mês de {month}: R$ {total:.2f}",
        "monthly_balance": "Balanço do mês {month}: R$ {balance:.2f}",
        "enter_month": "Navegação Meses",
        "months": [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ],
        "year": "Qual Ano:",
        "sales": "Entradas: ",
        "expenses": "Saídas: ",
        "investment_payments": "Pagamentos de Investimentos:",
        "campaigns": "Campanhas: "
    },
    "English": {
        "title": "Financial",
        "menu_register_expense": "Register Expense",
        "menu_financial_insights": "Financial Insights",
        "register_expense": "Expense Tab",
        "select_expense": "Select Expense",
        "water_supplier": "Water Supplier",
        "electricity_supplier": "Electricity Supplier",
        "internet_supplier": "Internet Supplier",
        "supplier": "Supplier",
        "bill": "Bill",
        "salary_payment": "Employee Payment",
        "expense_value": "Bill Value",
        "payment_date": "Payment Date",
        "payment_method": "Payment Method",
        "payment_method_options": ["Debit", "Automatic Debit", "Cash", "Pix", "Bill"],
        "add_supplier": "Which supplier: ",
        "description": "Description: ",
        "register_expense_button": "Register expense",
        "expense_registered": "Expense registered!",
        "error_registering_expense": "Error registering expense: {e}",
        "no_sales": "No sales recorded.",
        "no_expenses": "No expenses recorded.",
        "no_investments": "No investments recorded.",
        "sales_total": "Total sales in {month}: R$ {total:.2f}",
        "expenses_total": "Total expenses in {month}: R$ {total:.2f}",
        "investments_paid_total": "Total investments paid in {month}: R$ {total:.2f}",
        "campaigns_paid_total": "Total campaigns paid in {month}: R$ {total:.2f}",
        "monthly_balance": "Balance for {month}: R$ {balance:.2f}",
        "enter_month": "Month Navigation",
        "months": [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ],
        "year": "Which Year:",
        "sales": "Sales: ",
        "expenses": "Expenses: ",
        "investment_payments": "Investment Payments:",
        "campaigns": "Campaigns: "
    }
}

def t(key):
    lang = session.get('language', 'Português')
    return translations[lang].get(key, key)

def preparar_dados_para_tabela(dados):
    """Prepara os dados para exibição na tabela, convertendo para lista de valores"""
    dados_formatados = []
    for item in dados:
        if isinstance(item, dict):
            dados_formatados.append(list(item.values()))
        elif hasattr(item, 'values') and callable(item.values):
            dados_formatados.append(list(item.values()))
        else:
            # Caso o item já seja uma lista/tupla ou outro iterável
            dados_formatados.append(list(item))
    return dados_formatados

@financeiro_bp.route('/financeiro', methods=['GET', 'POST'])
def financeiro():
    user_id = session.get('user_id')
    if not user_id:
        flash("Por favor faça login primeiro.", "warning")
        return redirect(url_for('auth.login'))

    # qual "aba" está aberta? parâmetro ?aba=register ou ?aba=insights
    aba = request.args.get('aba', 'register')

    # --------- ABA "Cadastrar Despesa" ---------
    if aba == 'register' and request.method == 'POST':
        contas = {
            "tipo": request.form['tipo'],
            "descricao": request.form['descricao'],
            "fornecedor": request.form['fornecedor'],
            "valor": float(request.form['valor']),
            "data_despesa": request.form['data'],
            "pagamento": request.form['pagamento'],
            "user_id": user_id
        }
        try:
            supabase.table("despesas").insert(contas).execute()
            flash(t("expense_registered"), "success")
        except Exception as e:
            flash(t("error_registering_expense").format(e=e), "danger")
        return redirect(url_for('financeiro.financeiro', aba='register'))

    # --------- ABA "Financial Insights" ---------
    # busca todos os dados
    vendas = obter_dados_tabela("vendas", user_id)
    despesas = obter_dados_tabela("despesas", user_id)
    investimentos = obter_dados_tabela("investimento", user_id)
    campanhas = obter_dados_tabela("campanha", user_id)

    # mês / ano selecionados
    mes_atual = datetime.today().month
    meses = t("months")
    menu_mes = request.args.get('mes', meses[mes_atual-1])
    ano = int(request.args.get('ano', datetime.today().year))
    mapa_meses = {m:i+1 for i,m in enumerate(meses)}
    mes_num = mapa_meses.get(menu_mes, mes_atual)

    # calcula somatórios e lista de pagamentos
    total_vendas = sum(v["valor"] for v in vendas
                   if "data_venda" in v and
                      datetime.strptime(v["data_venda"], "%Y-%m-%d").month == mes_num
                   and datetime.strptime(v["data_venda"], "%Y-%m-%d").year == ano)

    total_desp = sum(d["valor"] for d in despesas
                   if "data_despesa" in d and
                      datetime.strptime(d["data_despesa"], "%Y-%m-%d").month == mes_num
                   and datetime.strptime(d["data_despesa"], "%Y-%m-%d").year == ano)

    total_camp = sum(c["valor"] for c in campanhas
                   if "data_inicio" in c and
                      datetime.strptime(c["data_inicio"], "%Y-%m-%d").month == mes_num
                   and datetime.strptime(c["data_inicio"], "%Y-%m-%d").year == ano)

    pagamentos_investimentos = []
    total_inv = 0
    for inv in investimentos:
        hist = inv.get("historico_pagamentos", [])
        if isinstance(hist, str):
            hist = json.loads(hist)
        for p in hist:
            dt = datetime.strptime(p["data"], "%Y-%m-%d")
            if dt.month == mes_num and dt.year == ano:
                total_inv += p["valor"]
                pagamentos_investimentos.append({
                    "nome": inv["nome"],
                    "data": p["data"],
                    "valor": p["valor"]
                })

    balanco = total_vendas - (total_desp + total_inv + total_camp)

    # Prepara os dados para as tabelas
    vendas_tabela = preparar_dados_para_tabela(
        [v for v in vendas 
         if "data_venda" in v and 
            datetime.strptime(v["data_venda"], "%Y-%m-%d").month == mes_num and
            datetime.strptime(v["data_venda"], "%Y-%m-%d").year == ano]
    )
    
    despesas_tabela = preparar_dados_para_tabela(
        [d for d in despesas 
         if "data_despesa" in d and 
            datetime.strptime(d["data_despesa"], "%Y-%m-%d").month == mes_num and
            datetime.strptime(d["data_despesa"], "%Y-%m-%d").year == ano]
    )
    
    campanhas_tabela = preparar_dados_para_tabela(
        [c for c in campanhas 
         if "data_inicio" in c and 
            datetime.strptime(c["data_inicio"], "%Y-%m-%d").month == mes_num and
            datetime.strptime(c["data_inicio"], "%Y-%m-%d").year == ano]
    )
    
    investimentos_tabela = preparar_dados_para_tabela(pagamentos_investimentos)

    return render_template(
        'financeiro.html',
        t=t,
        aba=aba,
        # para despesa
        payment_methods=translations[session.get('language','Português')]["payment_method_options"],
        # para insights
        meses=meses,
        menu_mes=menu_mes,
        ano=ano,
        total_vendas=total_vendas,
        total_desp=total_desp,
        total_camp=total_camp,
        total_inv=total_inv,
        balanco=balanco,
        # Dados para as tabelas (já formatados)
        vendas_tabela=vendas_tabela,
        despesas_tabela=despesas_tabela,
        campanhas_tabela=campanhas_tabela,
        investimentos_tabela=investimentos_tabela,
        # Dados originais (para outros usos)
        vendas=vendas,
        despesas=despesas,
        campanhas=campanhas,
        pagamentos_investimentos=pagamentos_investimentos
    )