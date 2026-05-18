import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, precision_recall_curve, auc, recall_score
from scipy.stats import ks_2samp

def calculate_metrics(y_true, y_prob, threshold=0.5):
    """
    Calcula as principais métricas de negócio e técnica para o problema de FPD.
    Métricas principais (Leaderboard e Desempate): ROC AUC, KS, PR AUC, Recall.
    """
    # 1. ROC AUC: Mede a capacidade geral do modelo de ordenar clientes.
    # Na prática, avalia se um inadimplente (FPD=1) recebe uma nota de risco
    # maior que um adimplente (FPD=0). É a métrica mais importante do ranking do hackathon.
    roc_auc = roc_auc_score(y_true, y_prob)
    
    # 2. KS (Kolmogorov-Smirnov): Mede a distância máxima entre as curvas de distribuição
    # de risco dos bons pagadores e dos maus pagadores. Quanto maior, mais nítida a separação.
    score_0 = y_prob[y_true == 0] # Probabilidades dadas aos pagadores
    score_1 = y_prob[y_true == 1] # Probabilidades dadas aos inadimplentes (FPD)
    
    if len(score_0) > 0 and len(score_1) > 0:
        ks_stat, _ = ks_2samp(score_0, score_1)
    else:
        ks_stat = 0.0
    
    # 3. PR AUC (Precision-Recall Area Under Curve): Extremamente útil para o FPD, 
    # já que clientes FPD representam uma minoria na base (são casos desbalanceados).
    # Mede a área sob a curva de Precisão vs Recall em vários pontos de corte.
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = auc(recall, precision)
    
    # 4. Recall no limiar (threshold): O threshold padrão de 0.5 nem sempre é bom.
    # Se diminuirmos esse threshold (ex: 0.3), capturamos mais FPDs reais (aumentamos Recall),
    # porém corremos o risco de alarmar Falsos Positivos.
    y_pred = (y_prob >= threshold).astype(int)
    recall_val = recall_score(y_true, y_pred, zero_division=0)
    
    return {
        'ROC_AUC': roc_auc,
        'KS': ks_stat,
        'PR_AUC': pr_auc,
        'Recall_at_threshold': recall_val
    }
