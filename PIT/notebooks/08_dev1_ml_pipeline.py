import os
import json
import warnings
import pandas as pd
import numpy as np

# ML libs
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score
from scipy.stats import ks_2samp

import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier
import optuna

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)

RANDOM_STATE = 42
BASE_DIR = r"c:/dev/PIT/v2"
MODELOS_DIR = os.path.join(BASE_DIR, "dados", "modelos")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs", "ml")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*70)
print("PIPELINE DEV 1 — FASES 5 a 9 (CORRIGIDO E OTIMIZADO)")
print("="*70)

# ── 1. Carregar Metadados (Fase 4/6) ──────────────────────────────────────────
with open(os.path.join(MODELOS_DIR, 'FEATURES_FINAIS.json'), 'r', encoding='utf-8') as f:
    meta = json.load(f)

scale_pos_weight = meta['scale_pos_weight_treino']
cat_features = meta['catboost']['cat_features']
print(f"[✓] Metadados carregados. scale_pos_weight: {scale_pos_weight:.4f}")
print(f"[✓] Variáveis categóricas do CatBoost ({len(cat_features)}): {cat_features}")

# ── 2. Carregar Dados ─────────────────────────────────────────────────────────
# LGBM/XGBoost (100% numérico)
df_train_num = pd.read_csv(os.path.join(MODELOS_DIR, 'X_train_lgbm.csv'), encoding='utf-8')
df_val_num   = pd.read_csv(os.path.join(MODELOS_DIR, 'X_val_lgbm.csv'), encoding='utf-8')

# CatBoost (mantém textos)
df_train_cat = pd.read_csv(os.path.join(MODELOS_DIR, 'X_train_catboost.csv'), encoding='utf-8')
df_val_cat   = pd.read_csv(os.path.join(MODELOS_DIR, 'X_val_catboost.csv'), encoding='utf-8')

y_train = df_train_num['FPD'].values
y_val   = df_val_num['FPD'].values

X_train_num = df_train_num.drop(columns=['FPD', 'pedido_id'])
X_val_num   = df_val_num.drop(columns=['FPD', 'pedido_id'])

X_train_cat = df_train_cat.drop(columns=['FPD', 'pedido_id'])
X_val_cat   = df_val_cat.drop(columns=['FPD', 'pedido_id'])

# Garante que as colunas categóricas são string para o CatBoost
for c in cat_features:
    X_train_cat[c] = X_train_cat[c].fillna("Missing").astype(str)
    X_val_cat[c]   = X_val_cat[c].fillna("Missing").astype(str)

print(f"[✓] Dados carregados. Treino: {X_train_num.shape}, Val: {X_val_num.shape}")

# ── FASE 5: Baseline LR ─────────────────────────────────────────────────────
print("\n--- FASE 5: Baseline (Regressão Logística) ---")
scaler = StandardScaler()
X_tr_s = scaler.fit_transform(X_train_num)
X_vl_s = scaler.transform(X_val_num)

lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=RANDOM_STATE)
lr.fit(X_tr_s, y_train)
prob_val_lr = lr.predict_proba(X_vl_s)[:, 1]
auc_lr = roc_auc_score(y_val, prob_val_lr)
print(f"[Baseline LR] AUC: {auc_lr:.4f}")

# ── FASE 6: Modelos Avançados ───────────────────────────────────────────────
print("\n--- FASE 6: Modelos Avançados ---")

# LightGBM
print("Treinando LightGBM...")
lgbm = lgb.LGBMClassifier(
    objective='binary', metric='auc', n_estimators=1000, learning_rate=0.05, 
    num_leaves=63, scale_pos_weight=scale_pos_weight, random_state=RANDOM_STATE, verbose=-1
)
lgbm.fit(X_train_num, y_train, eval_set=[(X_val_num, y_val)], callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)])
prob_val_lgbm = lgbm.predict_proba(X_val_num)[:, 1]
auc_lgbm = roc_auc_score(y_val, prob_val_lgbm)

# XGBoost
print("Treinando XGBoost...")
xgb_model = xgb.XGBClassifier(
    n_estimators=1000, learning_rate=0.05, max_depth=6, scale_pos_weight=scale_pos_weight,
    eval_metric='auc', early_stopping_rounds=50, random_state=RANDOM_STATE, verbosity=0
)
xgb_model.fit(X_train_num, y_train, eval_set=[(X_val_num, y_val)], verbose=False)
prob_val_xgb = xgb_model.predict_proba(X_val_num)[:, 1]
auc_xgb = roc_auc_score(y_val, prob_val_xgb)

# CatBoost (CORRIGIDO: Passando os textos e cat_features)
print("Treinando CatBoost (com cat_features corrigido!)...")
cat_model = CatBoostClassifier(
    iterations=1000, learning_rate=0.05, depth=6, scale_pos_weight=scale_pos_weight,
    eval_metric='AUC', early_stopping_rounds=50, cat_features=cat_features, 
    random_seed=RANDOM_STATE, verbose=0
)
cat_model.fit(X_train_cat, y_train, eval_set=(X_val_cat, y_val))
prob_val_cat = cat_model.predict_proba(X_val_cat)[:, 1]
auc_cat = roc_auc_score(y_val, prob_val_cat)

print(f"[LightGBM] AUC: {auc_lgbm:.4f}")
print(f"[XGBoost]  AUC: {auc_xgb:.4f}")
print(f"[CatBoost] AUC: {auc_cat:.4f} (Olha a diferença com textos!)")

# ── FASE 7: Métricas Completas ──────────────────────────────────────────────
print("\n--- FASE 7: Tabela de Métricas Comparativa ---")
def calcular_ks(y_true, y_prob):
    pos = y_prob[y_true == 1]
    neg = y_prob[y_true == 0]
    return ks_2samp(pos, neg)[0]

modelos_val = {
    'Baseline LR': prob_val_lr,
    'LightGBM': prob_val_lgbm,
    'XGBoost': prob_val_xgb,
    'CatBoost (Fix)': prob_val_cat
}

rows = []
for nome, probs in modelos_val.items():
    rows.append({
        'Modelo': nome,
        'AUC': round(roc_auc_score(y_val, probs), 4),
        'KS': round(calcular_ks(y_val, probs), 4),
        'PR AUC': round(average_precision_score(y_val, probs), 4)
    })

df_metricas = pd.DataFrame(rows).sort_values('AUC', ascending=False).reset_index(drop=True)
print(df_metricas.to_string(index=False))

# ── FASE 8: Optuna LightGBM ────────────────────────────────────────────────
print("\n--- FASE 8: Optuna (LightGBM) ---")
print("Iniciando 50 trials (pode levar 1-2 minutos)...")

def objective(trial):
    params = dict(
        objective='binary', metric='auc', n_estimators=1000,
        learning_rate=trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        num_leaves=trial.suggest_int('num_leaves', 20, 150),
        max_depth=trial.suggest_int('max_depth', 3, 8),
        min_child_samples=trial.suggest_int('min_child_samples', 20, 100),
        subsample=trial.suggest_float('subsample', 0.6, 1.0),
        colsample_bytree=trial.suggest_float('colsample_bytree', 0.6, 1.0),
        reg_alpha=trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        reg_lambda=trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        scale_pos_weight=scale_pos_weight, random_state=RANDOM_STATE, verbose=-1
    )
    m = lgb.LGBMClassifier(**params)
    m.fit(X_train_num, y_train, eval_set=[(X_val_num, y_val)], callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(0)])
    return roc_auc_score(y_val, m.predict_proba(X_val_num)[:, 1])

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=50)

print(f"Melhor AUC Optuna: {study.best_value:.4f}")
print("Treinando LGBM otimizado...")
lgbm_opt = lgb.LGBMClassifier(
    objective='binary', metric='auc', n_estimators=2000, scale_pos_weight=scale_pos_weight,
    random_state=RANDOM_STATE, verbose=-1, **study.best_params
)
lgbm_opt.fit(X_train_num, y_train, eval_set=[(X_val_num, y_val)], callbacks=[lgb.early_stopping(100, verbose=False), lgb.log_evaluation(0)])
prob_val_lgbm_opt = lgbm_opt.predict_proba(X_val_num)[:, 1]
auc_lgbm_opt = roc_auc_score(y_val, prob_val_lgbm_opt)

if auc_lgbm_opt > auc_lgbm:
    print(f"-> Otimização aprovada: de {auc_lgbm:.4f} para {auc_lgbm_opt:.4f}")
    prob_val_lgbm_final = prob_val_lgbm_opt
    auc_lgbm_final = auc_lgbm_opt
else:
    print(f"-> Optuna não superou. Mantendo baseline: {auc_lgbm:.4f}")
    prob_val_lgbm_final = prob_val_lgbm
    auc_lgbm_final = auc_lgbm

# ── FASE 9: Ensemble Ponderado (Corrigido) ─────────────────────────────────
print("\n--- FASE 9: Ensemble Ponderado ---")
probs_dict = {
    'LightGBM': (prob_val_lgbm_final, auc_lgbm_final),
    'XGBoost': (prob_val_xgb, auc_xgb),
    'CatBoost': (prob_val_cat, auc_cat)
}

melhor_indiv_nome = max(probs_dict, key=lambda k: probs_dict[k][1])
melhor_indiv_auc = probs_dict[melhor_indiv_nome][1]

total_auc = sum(auc for _, auc in probs_dict.values())
pesos = {k: auc / total_auc for k, (_, auc) in probs_dict.items()}

print("Pesos calculados (proporcionais ao AUC):")
for k, w in pesos.items():
    print(f"  {k}: {w:.4f} (AUC {probs_dict[k][1]:.4f})")

prob_ensemble = sum(pesos[k] * p for k, (p, _) in probs_dict.items())
auc_ens = roc_auc_score(y_val, prob_ensemble)

print(f"\nAUC Melhor Individual ({melhor_indiv_nome}): {melhor_indiv_auc:.4f}")
print(f"AUC Ensemble: {auc_ens:.4f}")

if auc_ens >= melhor_indiv_auc:
    print("-> USAR ENSEMBLE COMO MODELO FINAL")
else:
    print(f"-> USAR {melhor_indiv_nome} COMO MODELO FINAL (Ensemble não superou)")

print("\nPIPELINE DEV 1 (Fases 5-9) finalizado com sucesso!")
