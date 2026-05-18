import numpy as np
import pandas as pd

def define_risk_bands(y_prob, num_bins=10):
    """
    Define faixas de risco baseando-se nas probabilidades previstas.
    O objetivo é mapear a probabilidade contínua (0 a 1) para as faixas 
    da Política de Cobrança exigida (Baixo, Médio, Alto, Crítico).
    """
    # Cria um DataFrame contendo as probabilidades previstas pelo modelo
    df = pd.DataFrame({'prob_fpd': y_prob})
    
    # 1. Definição manual de limites (Thresholds). 
    # Em um cenário real de hackathon, o ideal é não usar valores fixos, 
    # mas sim decis, quartis ou limites otimizados pelas curvas de Ganho.
    # Exemplo atual (baseado em corte direto nas probabilidades):
    # - Baixo: < 20% de chance de inadimplência (FPD)
    # - Médio: 20% a 45% de chance
    # - Alto: 45% a 70% de chance
    # - Crítico: > 70% de chance
    
    # 2. Cria as condições lógicas para classificar as probabilidades em cada faixa
    conditions = [
        (df['prob_fpd'] <= 0.20),
        (df['prob_fpd'] > 0.20) & (df['prob_fpd'] <= 0.45),
        (df['prob_fpd'] > 0.45) & (df['prob_fpd'] <= 0.70),
        (df['prob_fpd'] > 0.70)
    ]
    
    # 3. Mapeia os nomes das faixas equivalentes a cada condição respectiva
    choices = ['Baixo', 'Médio', 'Alto', 'Crítico']
    
    # 4. Aplica as regras: np.select checa a lista de condições e aplica a string (ex: 'Baixo')
    # Se, por algum motivo atípico, uma probabilidade escapar das regras, ele marca como 'Desconhecido'
    df['faixa_risco'] = np.select(conditions, choices, default='Desconhecido')
    
    return df
