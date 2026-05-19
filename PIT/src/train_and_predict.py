import pandas as pd
import numpy as np
import json
import os
import lightgbm as lgb
from pathlib import Path
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_curve, auc

def train_and_generate_outputs():
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / 'data' / 'processed'
    outputs_dir = base_dir / 'outputs'
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== TREINAMENTO DO MODELO BASELINE (LightGBM) ===")
    
    # 1. Carregar os datasets alinhados
    train = pd.read_csv(processed_dir / 'X_train_aligned.csv')
    val = pd.read_csv(processed_dir / 'X_val_aligned.csv')
    hold = pd.read_csv(processed_dir / 'X_hold_aligned.csv')
    sub = pd.read_csv(processed_dir / 'X_sub_aligned.csv')
    
    # 2. Definir target e colunas preditoras (apenas numericas, excluindo ids e datas)
    target_col = 'FPD'
    exclude_cols = ['pedido_id', 'FPD', 'data_efetivacao', 'order_bump', 
                    'MENSAGEM_TIPO_REGISTRO', 'produtor', 'lancamento', 
                    'segmento', 'categoria_risco_score', 'endereco_cep', 
                    'endereco_estado', 'endereco_cidade', 'nascimento', 'modalidade']
    
    features = [c for c in train.columns if c not in exclude_cols]
    print(f"Número de features utilizadas: {len(features)}")
    
    X_train = train[features].copy()
    X_val = val[features].copy()
    X_hold = hold[features].copy()
    X_sub = sub[features].copy()
    
    # Garantir que todas as colunas sejam numericas e tratar nulos
    for col in features:
        X_train[col] = pd.to_numeric(X_train[col], errors='coerce')
        X_val[col] = pd.to_numeric(X_val[col], errors='coerce')
        X_hold[col] = pd.to_numeric(X_hold[col], errors='coerce')
        X_sub[col] = pd.to_numeric(X_sub[col], errors='coerce')
        
        # Preencher nulos com a mediana do treino
        median_val = X_train[col].median()
        if pd.isna(median_val):
            median_val = 0.0 # fallback
        X_train[col] = X_train[col].fillna(median_val)
        X_val[col] = X_val[col].fillna(median_val)
        X_hold[col] = X_hold[col].fillna(median_val)
        X_sub[col] = X_sub[col].fillna(median_val)
        
    y_train = train[target_col]
    y_val = val[target_col]
    y_hold = hold[target_col]
    
    # 3. Calcular scale_pos_weight
    n_fpd = y_train.sum()
    n_nao_fpd = len(y_train) - n_fpd
    scale_pos_weight = n_nao_fpd / n_fpd
    print(f"Taxa de FPD no treino: {n_fpd / len(y_train):.2%}")
    print(f"scale_pos_weight (XGB/LGBM): {scale_pos_weight:.2f}")
    
    # 4. Treinar LightGBM
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'n_estimators': 1000,
        'learning_rate': 0.05,
        'num_leaves': 63,
        'scale_pos_weight': scale_pos_weight,
        'random_state': 42,
        'verbose': -1
    }
    
    model = lgb.LGBMClassifier(**params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(50, verbose=False)]
    )
    
    print(f"Melhor iteracao do LightGBM: {model.best_iteration_}")
    
    # 5. Fazer predicoes na validacao
    y_val_pred_proba = model.predict_proba(X_val)[:, 1]
    val_auc = roc_auc_score(y_val, y_val_pred_proba)
    print(f"AUC na Validação: {val_auc:.4f}")
    
    # Fazer predicoes no holdout
    y_hold_pred_proba = model.predict_proba(X_hold)[:, 1]
    hold_auc = roc_auc_score(y_hold, y_hold_pred_proba)
    print(f"AUC no Holdout  : {hold_auc:.4f}")
    
    # 6. Salvar outputs/y_val_results.csv
    y_val_results = pd.DataFrame({
        'y_true': y_val,
        'y_pred_proba': y_val_pred_proba
    })
    y_val_results.to_csv(outputs_dir / 'y_val_results.csv', index=False)
    print(f"[OK] y_val_results.csv gerado e salvo em outputs/")
    
    # 7. Salvar outputs/feature_importance.csv
    fi = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values(by='importance', ascending=False)
    fi.to_csv(outputs_dir / 'feature_importance.csv', index=False)
    print(f"[OK] feature_importance.csv gerado e salvo em outputs/")
    
    # 8. Fazer predicoes na submissao
    y_sub_pred_proba = model.predict_proba(X_sub)[:, 1]
    
    # Faixas de risco baseadas nos limites definidos na politica
    # - Baixo: <= 20%
    # - Medio: 20% a 45%
    # - Alto: 45% a 70%
    # - Critico: > 70%
    faixas = []
    for p in y_sub_pred_proba:
        if p <= 0.20:
            faixas.append('Baixo')
        elif p <= 0.45:
            faixas.append('Medio')
        elif p <= 0.70:
            faixas.append('Alto')
        else:
            faixas.append('Critico')
            
    submission = pd.DataFrame({
        'pedido_id': sub['pedido_id'].astype(int),
        'prob_fpd': y_sub_pred_proba,
        'faixa_risco': faixas
    })
    submission.to_csv(outputs_dir / 'submission.csv', index=False)
    print(f"[OK] submission.csv gerado e salvo em outputs/")
    print(submission['faixa_risco'].value_counts())
    
    # 9. Calcular metricas tecnicas finais
    ks_0 = y_val_pred_proba[y_val == 0]
    ks_1 = y_val_pred_proba[y_val == 1]
    from scipy.stats import ks_2samp
    ks_stat, _ = ks_2samp(ks_0, ks_1)
    
    prec, rec, _ = precision_recall_curve(y_val, y_val_pred_proba)
    pr_auc = auc(rec, prec)
    
    metricas = {
        'ROC_AUC': float(val_auc),
        'KS': float(ks_stat),
        'PR_AUC': float(pr_auc),
        'Recall_at_threshold': float(np.mean(y_val_pred_proba >= 0.5)),
        'threshold_usado': 0.5
    }
    
    with open(outputs_dir / 'metricas.json', 'w') as f:
        json.dump(metricas, f, indent=4)
    print(f"[OK] metricas.json gerado e salvo em outputs/")
    print(metricas)

if __name__ == '__main__':
    train_and_generate_outputs()
