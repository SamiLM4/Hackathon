import pandas as pd

def temporal_split(df, date_column, test_size=0.15, val_size=0.15):
    """
    Realiza o split temporal dos dados (train, val, test)
    respeitando a ordem cronológica, conforme as regras inegociáveis do hackathon.
    (Split sugerido: 70/15/15)
    """
    # 1. Ordena o dataframe inteiro pela coluna de data (ex: data_compra).
    # Isso é crucial para evitar 'data leakage' (vazamento de dados do futuro para o passado).
    # Modelos financeiros sempre devem ser treinados no passado para prever o futuro.
    df_sorted = df.sort_values(by=date_column).copy()
    
    # 2. Calcula a quantidade exata de linhas para cada divisão (teste, validação e treino).
    n_total = len(df_sorted)
    n_test = int(n_total * test_size)
    n_val = int(n_total * val_size)
    
    # O treino fica com o restante dos dados (aprox. 70%)
    n_train = n_total - n_test - n_val
    
    # 3. Divide o dataset mantendo a ordem cronológica estritamente intacta:
    
    # Os primeiros dados (mais antigos) vão para treino
    train = df_sorted.iloc[:n_train]
    
    # O bloco do meio vai para validação (usado para ajustar hiperparâmetros e testar ao longo do treino)
    val = df_sorted.iloc[n_train:n_train+n_val]
    
    # Os últimos dados (mais recentes, que o modelo nunca viu) vão para teste
    test = df_sorted.iloc[-n_test:]
    
    return train, val, test
