from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from routes.load_supabase import load_supabase
import datetime

supabase = load_supabase()
clientes_bp = Blueprint('clientes', __name__)

min_date = datetime.date(1900, 1, 1)

@clientes_bp.route("/clientes", methods=["GET", "POST"])
def clientes():
    user_id = session['user_id']
    # Recuperar clientes e vendas do banco de dados
    clientes = supabase.table("clientes").select("*").eq("user_id", user_id).execute().data
    vendas = supabase.table("vendas").select("*").eq("user_id", user_id).execute().data

    # Dados para o gráfico de vendas (agrupando por mês, como exemplo)
    vendas_por_mes = {}
    for venda in vendas:
        mes = venda["data_venda"].split("-")[1]  # Supondo que a data está no formato "YYYY-MM-DD"
        vendas_por_mes[mes] = vendas_por_mes.get(mes, 0) + venda["valor"]

    vendas_labels = list(vendas_por_mes.keys())
    vendas_values = list(vendas_por_mes.values())

    # Dados para o gráfico de clientes ativos/inativos
    ativos = sum(1 for cliente in clientes if cliente["ativo"])
    inativos = len(clientes) - ativos

        # Convertendo a coluna 'ativo' de True/False para texto
    for cliente in clientes:
        cliente["ativo"] = "Ativo" if cliente["ativo"] else "Inativo"

    # Calcular Vendas x Clientes
    vendas_vs_clientes = {}
    cliente_vendas = 0
    for cliente in clientes:
        cliente_vendas = sum(1 for venda in vendas if venda["cliente"] == cliente["nome"])  # contagem de vendas por cliente
        vendas_vs_clientes[cliente["nome"]] = cliente_vendas + 1

    if request.method == "POST":
        # Atualizar cliente
        cliente_id = request.form.get("clientid")
        print(cliente_id)
        nome = request.form.get("editNome")
        contato = request.form.get("editContato")
        endereco = request.form.get("editEndereco")
        email = request.form.get("editEmail")
        bairro = request.form.get("editBairro")
        cidade = request.form.get("editCidade")
        estado = request.form.get("editEstado")
        cep = request.form.get("editCep")
        genero = request.form.get("editGenero")
        data_nascimento = request.form.get("editDataNascimento")

        if not data_nascimento:
            data_nascimento = None

        ativo = request.form.get("editAtivo") == "true"  # Convertendo string para booleano

        cliente_atualizado = {
            "nome": nome,
            "contato": contato,
            "endereco": endereco,
            "email": email,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep,
            "genero": genero,
            "data_nascimento": data_nascimento,
            "ativo": ativo,
        }

        supabase.table("clientes").update(cliente_atualizado).eq("client__c", cliente_id).execute()
        flash("Cliente atualizado com sucesso!", "success")

        clientes = supabase.table("clientes").select("*").eq("user_id", user_id).execute().data
        vendas = supabase.table("vendas").select("*").eq("user_id", user_id).execute().data

        # Dados para o gráfico de vendas (agrupando por mês, como exemplo)
        vendas_por_mes = {}
        for venda in vendas:
            mes = venda["data_venda"].split("-")[1]  # Supondo que a data está no formato "YYYY-MM-DD"
            vendas_por_mes[mes] = vendas_por_mes.get(mes, 0) + venda["valor"]

        vendas_labels = list(vendas_por_mes.keys())
        vendas_values = list(vendas_por_mes.values())

        # Calcular Vendas x Clientes
        vendas_vs_clientes = {}
        for cliente in clientes:
            cliente_vendas = sum(1 for venda in vendas if venda["cliente"] == cliente["nome"])  # contagem de vendas por cliente
            vendas_vs_clientes[cliente["nome"]] = cliente_vendas  # Armazenar a quantidade de vendas por cliente


        # Passar para o template
        return render_template(
            "editar_clientes.html",
            clientes=clientes,
            vendas=vendas,
            vendas_labels=vendas_labels,
            vendas_values=vendas_values,
            vendas_vs_clientes=vendas_vs_clientes,  # Passando os dados para o histograma
            active_clients_count=ativos,
            inactive_clients_count=inativos,
            min_date=min_date
        )

    # Passar para o template
    return render_template(
        "editar_clientes.html",
        clientes=clientes,
        vendas=vendas,
        vendas_labels=vendas_labels,
        vendas_values=vendas_values,
        vendas_vs_clientes=vendas_vs_clientes,  # Passando os dados para o histograma
        active_clients_count=ativos,
        inactive_clients_count=inativos,
        min_date=min_date
    )