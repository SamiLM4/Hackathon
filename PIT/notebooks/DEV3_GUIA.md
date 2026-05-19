# 🎯 GUIA DO DEV 3 — Hackathon FPD TMB 2026

## Seus Notebooks

| Arquivo | Módulos | O que tem dentro |
|---------|---------|-----------------|
| `dev3_pitch_completo.ipynb` | 0 → 4 | Setup, carregamento, distribuição de scores, curvas ROC/KS/PR, análise por decil |
| `dev3_pitch_modulos5a9.ipynb` | 5 → 9 | Feature importance, segmento, política 12A, resumo executivo, checklist final |

---

## 📂 Onde ficam os arquivos

```
PIT/
├── notebooks/
│   ├── dev3_pitch_completo.ipynb     ← SEU NOTEBOOK PRINCIPAL (Mód. 0–4)
│   ├── dev3_pitch_modulos5a9.ipynb   ← SEU NOTEBOOK SECUNDÁRIO (Mód. 5–9)
│   └── DEV3_GUIA.md                  ← ESTE ARQUIVO
│
├── data/
│   └── processed/
│       ├── X_val_baseline.csv         ← JÁ DISPONÍVEL (base validação)
│       └── X_hold_baseline.csv        ← JÁ DISPONÍVEL (base hold-out)
│
└── outputs/
    ├── metricas.json                  ← ⏳ Dev 1/2 vão preencher
    ├── submission.csv                 ← ⏳ Dev 2 vai preencher
    ├── y_val_results.csv              ← ⏳ Dev 2 vai criar
    ├── feature_importance.csv         ← ⏳ Dev 1 vai criar
    ├── figures/                       ← ✅ VOCÊ gera aqui (auto)
    ├── politica_12A.md                ← ✅ VOCÊ gera (Mód. 7)
    └── resumo_executivo.md            ← ✅ VOCÊ gera (Mód. 8)
```

---

## ⚡ Ordem de execução por fase

### FASE 1 — Agora (sem esperar ninguém)
1. Abra `dev3_pitch_completo.ipynb`
2. Execute **Módulo 0** → verifica quais arquivos existem
3. Execute **Módulo 1** → carrega o que estiver disponível
4. Comece a estrutura do pitch (5 slides) no Google Slides / PowerPoint

### FASE 2 — Quando Dev 2 entregar `submission.csv` preenchido
5. Execute **Módulo 2** → distribuição de scores e faixas de risco
6. Execute **Módulo 7** (no segundo notebook) → gera política 12A automaticamente

### FASE 2 — Quando Dev 2 entregar `y_val_results.csv`
7. Execute **Módulo 3** → curvas ROC, KS e PR AUC (gráficos prontos)
8. Execute **Módulo 4** → tabela de ganho por decil (essencial para a banca)
9. Execute **Módulo 6** (no segundo notebook) → AUC por segmento

### FASE 3 — Quando Dev 1 entregar `feature_importance.csv`
10. Execute **Módulo 5** → gráfico de feature importance
11. Execute **Módulo 8** → gera resumo executivo completo (.md)
12. Execute **Módulo 9** → checklist final

---

## 📁 O que os colegas precisam te entregar

### Dev 1 deve criar:
```python
# No notebook dele, ao final do treinamento:
import pandas as pd

feature_importance = pd.DataFrame({
    'feature': model.feature_name_,      # LightGBM
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

feature_importance.to_csv('../outputs/feature_importance.csv', index=False)
```

### Dev 2 deve criar:
```python
# y_val_results.csv — previsões na validação
pd.DataFrame({
    'y_true': y_val,
    'y_pred_proba': y_val_pred_proba
}).to_csv('../outputs/y_val_results.csv', index=False)

# submission.csv preenchido
sub_final.to_csv('../outputs/submission.csv', index=False)
# Colunas: pedido_id, prob_fpd, faixa_risco
```

### Dev 1/2 devem atualizar `metricas.json`:
```json
{
    "ROC_AUC": 0.7842,
    "KS": 0.4231,
    "PR_AUC": 0.5123,
    "Recall_at_threshold": 0.7012,
    "threshold_usado": 0.45,
    "modelo": "LightGBM com class_weight"
}
```

---

## 📊 Gráficos que você vai gerar (para o pitch)

| Arquivo | Módulo | Usa no slide |
|---------|--------|-------------|
| `figures/mod2_distribuicao_scores.png` | 2 | Slide 3 — Resultado do modelo |
| `figures/mod3_curvas_roc_ks_pr.png` | 3 | Slide 3 — Métricas de performance |
| `figures/mod4_analise_decil.png` | 4 | Slide 4 — Capacidade de ordenação |
| `figures/mod5_feature_importance.png` | 5 | Slide 3 — Explicabilidade |
| `figures/mod6_auc_por_segmento.png` | 6 | Slide 4 — Robustez |
| `figures/mod7_politica_12A_distribuicao.png` | 7 | Slide 5 — Política de cobrança |

---

## 🗂️ Estrutura sugerida dos 5 slides

| Slide | Título | Conteúdo |
|-------|--------|---------|
| 1 | **O Problema** | O que é FPD, impacto 40%, jornada do cliente, 5 arquétipos |
| 2 | **Nossa Solução** | Modelo preditivo checkout-only, pipeline, split temporal |
| 3 | **Performance do Modelo** | ROC AUC, KS, PR AUC, top features, gráficos mod3 e mod5 |
| 4 | **Ordenação e Robustez** | Curva de ganho por decil, AUC por segmento, gráficos mod4 e mod6 |
| 5 | **Política de Cobrança 12A** | 4 faixas, ações, canais, custo operacional, gráfico mod7 |

---

## 🏁 Checklist de entrega (prazo 11h30 do Dia 3)

- [ ] `submission.csv` — `pedido_id`, `prob_fpd`, `faixa_risco`
- [ ] Notebook executável (`dev3_pitch_completo.ipynb` + `dev3_pitch_modulos5a9.ipynb`)
- [ ] `README.md` com instruções (Dev 2)
- [ ] `resumo_executivo.md` → converter para PDF/slides (2 páginas ou 5 slides)
- [ ] `politica_12A.md` → Seção 12A obrigatória
- [ ] Apresentação (5 slides com gráficos gerados)

---

*Guia gerado automaticamente para o Dev 3 | Science Hackathon TMB 2026*
