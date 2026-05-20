# Resumo Executivo — Modelo de Predição de FPD
**Science Hackathon by TMB — 2026 | Equipe PIT**

---

## 1. Problema
A TMB enfrenta um **First Payment Default (FPD)** responsável por ~40% da inadimplência total.
Clientes pagam a 1ª parcela mas abandonam silenciosamente o restante, sem cancelamento formal.
O desafio é prever, **apenas com dados disponíveis no checkout**, quais clientes têm maior probabilidade de FPD.

## 2. Dados Utilizados
- **Base de treino:** `base-treinamento.xlsx` (~70 mil registros)
- **Features selecionadas:** 34 variáveis — dados cadastrais, operação, produto, score TMB e bureau externo (Serasa Experian)
- **Split:** temporal (sem random) — 70/15/15 treino/validação/hold-out
- **Desbalanceamento:** tratado com `class_weight` e análise de impacto

## 3. Tratamento de Dados
- Missing values tratados explicitamente (não descartados)
- Encoding categórico aplicado (Label / Target Encoding)
- Calibração de probabilidades: Platt Scaling ou Isotonic Regression
- Leakage verificado coluna a coluna — apenas dados de checkout

## 4. Algoritmo e Performance
- **Modelo:** LightGBM / XGBoost
- **ROC AUC:** 0.7842
- **KS:** 0.4364
- **PR AUC:** 0.3306
- **Recall (threshold 0.5):** 0.4274

## 5. Top Features
- **quantidade_parcelas** (importância: 554.0000)
- **score** (importância: 490.0000)
- **endereco_cep_encoded** (importância: 418.0000)
- **lancamento_encoded** (importância: 403.0000)
- **nascimento_encoded** (importância: 401.0000)

## 6. Distribuição de Risco na Base de Submissão
- **Baixo**: 10737 clientes (46.0%)
- **Médio**: 10789 clientes (46.2%)
- **Alto**: 1791 clientes (7.7%)
- **Crítico**: 37 clientes (0.2%)

## 7. Proposta de Uso Operacional
O score `prob_fpd` é gerado no **momento do checkout** e segmenta automaticamente o cliente em uma das 4 faixas de risco.
A régua de cobrança da TMB é ativada proporcionalmente ao risco, otimizando custo operacional e maximizando recuperação.

## 8. Principais Riscos e Limitações
- Dependência do bureau externo (degradação de performance sem Serasa)
- Deriva temporal: modelo deve ser retreinado periodicamente
- Superajuste a safras específicas — validado por split temporal
- Threshold deve ser ajustado conforme custo operacional real da TMB

## 9. Política de Cobrança (12A)
Ver documento completo em `outputs/politica_12A.md`.

---
*Gerado automaticamente pelo Módulo 8 do notebook Dev 3 | 20/05/2026 00:27*
