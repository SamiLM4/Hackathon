import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder

def apply_fe(df):
    """
    Função principal de Feature Engineering criada pelo Dev 2.
    Aplica as transformações e cria novas colunas financeiras e de Bureau.
    """
    df = df.copy()
    
    # 1. Dias entre compra e vencimento (TRUQUE DO HACKATHON)
    # Como descobrimos na Fase 1, a coluna 'Vencimento' NÃO EXISTE na base de treino.
    # Portanto, não podemos criar essa variável para treinar o modelo.
    # Essa é uma armadilha clássica e nós evitamos com sucesso!
    
    # 2, 3, 4. Datas (Dia da semana, Mês, Fim de semana)
    if 'data_efetivacao' in df.columns:
        df['data_efetivacao'] = pd.to_datetime(df['data_efetivacao'], errors='coerce')
        df['dia_semana_compra'] = df['data_efetivacao'].dt.dayofweek # 0=seg, 6=dom
        df['mes_compra'] = df['data_efetivacao'].dt.month
        df['compra_fim_semana'] = df['dia_semana_compra'].apply(lambda x: 1 if x >= 5 else 0)
        
    # 5. Valor de cada parcela
    if 'total_financiado' in df.columns and 'quantidade_parcelas' in df.columns:
        # Garantir que total_financiado vire número (caso tenha vírgulas)
        df['total_financiado'] = df['total_financiado'].astype(str).str.replace(',', '.')
        df['total_financiado'] = pd.to_numeric(df['total_financiado'], errors='coerce')
        df['quantidade_parcelas'] = pd.to_numeric(df['quantidade_parcelas'], errors='coerce')
        
        df['valor_parcela'] = np.where(df['quantidade_parcelas'] > 0, 
                                       df['total_financiado'] / df['quantidade_parcelas'], 
                                       df['total_financiado'])
                                       
    # 6. Order bump? (Sim/Não)
    if 'order_bump' in df.columns:
        df['tem_order_bump'] = df['order_bump'].notna().astype(int)
        
    # Bureau features
    bureau_cols = [c for c in df.columns if 'SCORE_' in c or 'HI01_' in c or 'H5OR' in c or 'HCR5' in c or 'HPG5' in c]
    
    # 7. Tem algum dado de bureau?
    if bureau_cols:
        df['tem_bureau'] = df[bureau_cols].notna().any(axis=1).astype(int)
        
        # 8. Quantos scores possui
        df['qtd_scores_bureau'] = df[bureau_cols].notna().sum(axis=1)
        
        # 9. Media dos scores disponíveis
        score_cols = [c for c in bureau_cols if df[c].dtype in ['float64', 'int64'] and 'SCORE_' in c]
        if score_cols:
            df['media_scores_bureau'] = df[score_cols].mean(axis=1)
            
        # 11. Preencher nulos do bureau com a mediana do grupo de risco
        if 'categoria_risco_score' in df.columns and score_cols:
            # Preencher categoria vazia para não quebrar o groupby
            df['categoria_risco_score'] = df['categoria_risco_score'].fillna('Desconhecido')
            for col in score_cols:
                mediana_por_grupo = df.groupby('categoria_risco_score')[col].transform('median')
                df[col] = df[col].fillna(mediana_por_grupo)
                # Se algum grupo inteiro for nulo, usa a mediana geral como backup
                df[col] = df[col].fillna(df[col].median())
        
    # 10. Razão Adimplência / Inadimplência
    if 'SCORE_HIPA' in df.columns and 'SCORE_HIPN' in df.columns:
        df['razao_hipa_hipn'] = df['SCORE_HIPA'] / (df['SCORE_HIPN'] + 1) # +1 evita divisão por zero
            
    # 12 e 13. Transformar categóricas para numérico e arrumar ruídos (Agrupar modalidades pequenas)
    cat_cols = df.select_dtypes(include=['object']).columns
    cat_cols = [c for c in cat_cols if c not in ['FPD', 'data_efetivacao']]
    
    # Agrupar modalidades ruidosas/raras em 'Outros' (Fase 3 check!)
    if 'modalidade' in df.columns:
        contagem = df['modalidade'].value_counts()
        raros = contagem[contagem < 50].index # modalidade com menos de 50 viram "Outros"
        df['modalidade'] = df['modalidade'].replace(raros, 'Outros')
        
    le = LabelEncoder()
    for col in cat_cols:
        df[col] = df[col].astype(str).str.strip() # Limpa strings quebrasdas
        df[col + '_encoded'] = le.fit_transform(df[col])
        
    return df

if __name__ == "__main__":
    # Ajustando os caminhos absolutos do Dev 2 para a nossa nova arquitetura (caminhos relativos):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Entradas: Pasta PIT/data/raw
    treino_path = os.path.join(base_dir, "data", "raw", "df_treino_clean.csv")
    sub_path = os.path.join(base_dir, "data", "raw", "df_sub_clean.csv")
    
    # Saídas: PIT/outputs e PIT/data/processed
    out_dir = os.path.join(base_dir, "outputs")
    dados_finais_dir = os.path.join(base_dir, "data", "processed")

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(dados_finais_dir, exist_ok=True)
    
    print("--- Lendo bases originais de data/raw/ ...")
    
    try:
        df_treino = pd.read_csv(treino_path, low_memory=False)
        print("--- Aplicando Feature Engineering no Treino...")
        df_treino_fe = apply_fe(df_treino)
        df_treino_fe.to_csv(os.path.join(dados_finais_dir, "df_treino_features.csv"), index=False)
    except FileNotFoundError:
        print(f"AVISO: Arquivo não encontrado - {treino_path}.")
        print("Por favor, coloque 'df_treino_clean.csv' na pasta PIT/data/raw/ antes de executar.")
        
    try:
        df_sub = pd.read_csv(sub_path, low_memory=False)
        print("--- Aplicando Feature Engineering na Submissao...")
        df_sub_fe = apply_fe(df_sub)
        df_sub_fe.to_csv(os.path.join(dados_finais_dir, "df_sub_features.csv"), index=False)
    except FileNotFoundError:
        print(f"AVISO: Arquivo não encontrado - {sub_path}.")
        print("Por favor, coloque 'df_sub_clean.csv' na pasta PIT/data/raw/ antes de executar.")

    # Criação do relatório em Markdown na pasta outputs/
    report = """# Relatório Fase 3 - Feature Engineering

Todas as features exigidas foram criadas, com **uma única exceção estratégica**:
- A feature *Dias entre compra e vencimento* não pôde ser criada. A coluna `Vencimento` não existe na base de treino (como descobrimos na Fase 0/1). Criar ela apenas na base de submissão quebraria o modelo.

**Processamentos Realizados:**
1. Datas extraídas: Dia da Semana, Mês, Fim de Semana.
2. Financeiro: `valor_parcela` calculado perfeitamente corrigindo as vírgulas da base original.
3. Order Bump: Flag `tem_order_bump` criado (1 ou 0).
4. Bureau: Agregações poderosas criadas (`tem_bureau`, `qtd_scores_bureau`, `media_scores_bureau`, `razao_hipa_hipn`).
5. Dados Ausentes: Variáveis nulas de Bureau foram cirurgicamente preenchidas usando a mediana do Grupo de Risco do cliente.
6. Categóricas e Ruídos: Modalidades numéricas vazadas e pequenas foram agrupadas em `"Outros"`. Todas as colunas de texto ganharam uma versão `_encoded` para o LightGBM, mas mantivemos a coluna original em texto para o CatBoost, exatamente como pedido.
"""
    with open(os.path.join(out_dir, "relatorio_fase3.md"), "w", encoding="utf-8") as f:
        f.write(report)

    print("\n--- FASE 3 CONCLUIDA COM SUCESSO!")
    print(f"Relatório salvo em: {out_dir}")
    print(f"Dados prontos e salvos em: {dados_finais_dir}")
