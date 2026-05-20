# FPD Pipeline — CI/CD com Dashboard Web

Executa automaticamente todos os notebooks ao fazer `git push` e publica um dashboard visual no GitHub Pages.

## 🚀 Setup em 5 minutos

### 1. Estrutura de pastas esperada

```
seu-repo/
├── .github/workflows/run-notebooks.yml   # ← do pipeline
├── scripts/generate_report.py            # ← do pipeline
├── web/index.html                        # ← dashboard
├── notebooks/
│   ├── dev3_metrics.ipynb
│   ├── dev3_pitch_modulos5a9.ipynb
│   └── dev3_pitch_completo.ipynb
├── outputs/                              # criado automaticamente
│   ├── metricas.json
│   ├── submission.csv
│   ├── feature_importance.csv
│   ├── y_val_results.csv
│   ├── tabela_decil.csv
│   └── figures/
│       ├── mod2_distribuicao_scores.png
│       ├── mod3_curvas_roc_ks_pr.png
│       └── ...
├── data/processed/
│   ├── X_val_baseline.csv
│   └── X_hold_baseline.csv
└── requirements.txt
```

### 2. Ativar GitHub Pages

1. Vá em **Settings → Pages**
2. Em *Source*, selecione **GitHub Actions**
3. Salve

### 3. Adicionar `requirements.txt`

```txt
pandas
numpy
matplotlib
seaborn
scikit-learn
lightgbm
xgboost
papermill
nbformat
nbconvert
ipykernel
```

### 4. Fazer push

```bash
git add .
git commit -m "feat: adicionar pipeline CI/CD"
git push origin main
```

O GitHub Actions vai:
1. Executar os 3 notebooks em sequência
2. Rodar `generate_report.py` que agrega os outputs em JSONs
3. Publicar o dashboard no GitHub Pages

### 5. Ver o dashboard

`https://<seu-usuario>.github.io/<seu-repo>/`

---

## 📊 O que o dashboard mostra

| Seção | Dados |
|-------|-------|
| **ROC AUC / KS / PR AUC / Recall** | Do `outputs/metricas.json` |
| **Gauge visual** | ROC AUC animado com código de cores |
| **Faixas de risco** | Do `outputs/submission.csv` |
| **Top features** | Do `outputs/feature_importance.csv` |
| **Gráficos** | Todas as PNGs em `outputs/figures/` |
| **Tabela de Decil** | Do `outputs/tabela_decil.csv` |
| **Resumo Executivo** | Do `outputs/resumo_executivo.md` |
| **Política 12A** | Do `outputs/politica_12A.md` |

---

## ⚙️ Como adicionar mais notebooks

Edite `.github/workflows/run-notebooks.yml` e adicione um novo step:

```yaml
- name: 📓 Executar meu_novo_notebook.ipynb
  run: |
    papermill notebooks/meu_novo_notebook.ipynb \
      outputs/executed/meu_novo_notebook_out.ipynb \
      --log-output --no-progress-bar \
      2>&1 | tee outputs/logs/meu_novo_notebook.log || true
  continue-on-error: true
```

Depois atualize `generate_report.py` para incluir o novo notebook na lista de `notebooks`.

---

## 🔍 Troubleshooting

**Notebook falhou mas o workflow continuou?**
O `continue-on-error: true` garante que falhas parciais não bloqueiem o dashboard. O badge de status no topo mostra ✅/❌ por notebook.

**Arquivos de dados não encontrados?**
Os notebooks usam `../outputs/` e `../data/processed/`. Certifique-se de que os arquivos estão commitados no repositório ou gerados por notebooks anteriores.

**Dashboard em branco?**
Verifique se o GitHub Pages está configurado para usar *GitHub Actions* (não branch) e aguarde ~2 minutos após o push.
