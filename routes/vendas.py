from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.load_supabase import load_supabase
from routes.obter_dados_tabela import obter_dados_tabela
import pandas as pd

supabase = load_supabase()
vendas_bp = Blueprint('vendas', __name__)

vendas = []

def formatar_produtos(produtos_json):
    if produtos_json is None:
        return ""  # Retorna uma string vazia caso o valor seja None

    produtos_formatados = []
    for produto in produtos_json:
        if all(key in produto for key in ['nome', 'quantidade', 'desconto', 'preco']):
            produtos_formatados.append(f"{produto['nome']} - Quantidade: {produto['quantidade']} - Desconto: {produto['desconto']}% - Preço: R${produto['preco']}")
    
    return ", ".join(produtos_formatados)

@vendas_bp.route('/sales', methods=['GET', 'POST'])
def sales():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    clientes = obter_dados_tabela("clientes", user_id)
    produtos = obter_dados_tabela("produtos", user_id)
    vendedores = obter_dados_tabela("vendedores", user_id)

    clientes_df = pd.DataFrame(clientes)
    vendas = supabase.table("vendas").select("*").eq("user_id", user_id).execute().data

    # Processamento de vendas existentes
    if vendas:
        for venda in vendas:
            venda['produtos_formatados'] = formatar_produtos(venda.get('produtos'))
        vendas_df = pd.DataFrame(vendas)
    else:
        vendas_df = pd.DataFrame()

    # Inserção de uma nova venda
    if request.method == "POST":
        produto = request.form.get("produto")
        cliente = request.form.get("cliente")
        vendedor = request.form.get("vendedor")
        data_venda = request.form.get("data_venda")
        pagamento = request.form.get("pagamento")
        quantidade = request.form.get("quantidade")

        # Buscar preço do produto
        preco_unitario = next((p['preco'] for p in produtos if p['nome'] == produto), None)
        if preco_unitario is None:
            flash("Erro: Produto não encontrado.", "fail")
            return redirect(url_for('vendas.sales'))

        valor = int(quantidade) * float(preco_unitario)

        venda = {
            "user_id": user_id,
            "produtos": produto,
            "cliente": cliente,
            "vendedor": vendedor,
            "data_venda": data_venda,
            "pagamento": pagamento,
            "quantidade": quantidade,
            "valor": valor,
        }

        try:
            supabase.table("vendas").insert(venda).execute()
            flash("Venda cadastrada com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao cadastrar venda: {e}", "fail")

        return redirect(url_for('vendas.sales'))  # Redirecionamento após POST

    return render_template(
        'sales.html',
        clientes_df=clientes_df.to_dict('records'),
        vendas=vendas_df.to_dict(orient='records'),
        vendedores=vendedores,
        produtos=produtos,
    )