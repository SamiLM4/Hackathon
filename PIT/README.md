# Projeto Hackathon FPD TMB

## 1. Descrição do Problema
O First Payment Default (FPD) é quando o cliente paga a entrada (1ª parcela) via boleto ou Pix, mas não realiza nenhum dos pagamentos seguintes. Nosso modelo visa prever a probabilidade (`prob_fpd`) deste evento no momento do checkout, utilizando exclusivamente dados disponíveis nesta etapa.

## 2. Estrutura do Projeto
- `data/`: Contém os dados brutos (`raw/`) e processados (`processed/`).
- `notebooks/`: Notebooks Jupyter para exploração de dados (EDA), experimentação, treinamento, e consolidação de visualizações para o Pitch (Dev 3).
- `src/`: Código-fonte para a lógica central do modelo.
  - `feature_engineering.py`: Script do Dev 2 para limpeza, tratamento de valores faltantes (ex: preenchimento de features de bureau) e criação de variáveis. Lê de `raw/` e salva em `processed/`.
  - `validation.py`: Regras de split temporal (70/15/15) como requerido no regulamento.
  - `metrics.py`: Cálculo das métricas avaliadoras, como ROC AUC, KS e PR AUC.
  - `thresholds.py`: Definição de faixas de risco (Baixo, Médio, Alto, Crítico) para ancorar a Política de Cobrança (Seção 12A).
- `outputs/`: Arquivos gerados para submissão final (`submission.csv`, `metricas.json`).

## 3. Como Reproduzir
1. Crie o ambiente e instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Adicione seus arquivos de dados em `data/raw/`.
3. Execute as etapas de modelagem no diretório `src/` ou nos `notebooks/`.
