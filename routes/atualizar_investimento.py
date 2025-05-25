from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from flask import jsonify
from routes.obter_dados_tabela import obter_dados_tabela
from routes.load_supabase import load_supabase
import json

supabase = load_supabase()
atualizar_investmentos_bp = Blueprint('atualizar_investmentos', __name__)

@atualizar_investmentos_bp.route('/', methods=['GET', 'POST'])
def atualizar_investimento():
        
    if request.method == "POST":
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Usuário não autenticado"}), 401

        if not request.is_json:
            return jsonify({"error": "Requisição deve ser JSON"}), 400

        data = request.get_json()
        flash("Dados encontrados")

        # Validação dos dados recebidos
        investment_id = data.get('investment_id')
        flash(f"Id do investimento: {investment_id}")
        pagamento_data = data.get('data_pagamento')
        flash(f"Data do pagamento: {pagamento_data}")
        pagamento_valor = data.get('valor_pagamento')
        flash(f"Valor do pagamento {pagamento_valor}")
        sentido = data.get('sentido', True)
        flash(f"Sentido: {sentido}")
        encerrar = data.get('encerrar', False)
        flash(f"Encerrar: {encerrar}")

        if not investment_id or not pagamento_data or not pagamento_valor:
            return jsonify({"error": "Dados insuficientes"}), 400

        try:
            pagamento_valor = float(pagamento_valor)
        except ValueError:
            return jsonify({"error": "Valor do pagamento inválido"}), 400

        # Obtém o investimento específico do banco de dados
        investimentos = obter_dados_tabela("investimento", user_id)
        flash(f"Obteve a tabela de investimentos.")
        investimento = next((inv for inv in investimentos if inv["investimento__c"] == investment_id), None)
        flash(f'Encontrou o investimento: {investimento}')

        if not investimento:
            flash(f"Investimento não encontrado.")
            return jsonify({"error": "Investimento não encontrado"}), 404

        # Atualização do histórico de pagamentos
        historico_pagamentos = investimento.get("historico_pagamentos", [])
        historico_pagamentos.append({"data": pagamento_data, "valor": pagamento_valor})

        # Atualização do contador de pagamentos e cálculo do restante
        pagamentos = investimento.get("pagamentos", 0) + 1
        duracao = investimento.get("duracao", 0)
        restante = max(0, (duracao - pagamentos) * investimento.get("valor", 0))

        # Atualização do status do investimento
        investimento["sentido"] = sentido
        investimento["encerrado"] = encerrar or not sentido
        investimento["historico_pagamentos"] = json.dumps(historico_pagamentos)  # Salva como string JSON
        investimento["pagamentos"] = pagamentos

        # Atualiza o banco de dados
        supabase.table("investimento").update({
            "sentido": investimento["sentido"],
            "encerrado": investimento["encerrado"],
            "historico_pagamentos": investimento["historico_pagamentos"],
            "pagamentos": pagamentos
        }).eq("investimento__c", investment_id).execute()

        # Mensagem de retorno
        if investimento["encerrado"]:
            message = "Investimento encerrado com sucesso!"
        else:
            message = f"Pagamento adicionado com sucesso! Restante a pagar: R$ {restante:.2f}"

    return jsonify({"message": message}), 200