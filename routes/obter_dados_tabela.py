from routes.load_supabase import load_supabase

supabase = load_supabase()

def obter_dados_tabela(nome_tabela, user_id=None):
    try:
        query = supabase.table(nome_tabela).select("*")
        if user_id:
            query = query.eq("user_id", user_id)
        dados = query.execute().data
        return dados or []
    except Exception as e:
        print(f"Erro ao buscar {nome_tabela}: {e}")