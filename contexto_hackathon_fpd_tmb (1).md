# Contexto — Hackathon FPD TMB
> Arquivo de contexto para uso com LLMs. Contém toda a informação necessária para assistir uma equipe participante do Science Hackathon by TMB (18–20/mai/2026).

---

## 1. Sobre o evento

- **Nome:** Science Hackathon by TMB — 4ª edição Science & Business Connection (by Colmeia)
- **Datas:** 18 a 20 de maio de 2026
- **Dia 1 (18/mai):** Online (Discord)
- **Dias 2 e 3 (19–20/mai):** Presencial no PIT-SJC (São José dos Campos, SP)
- **Organizadores:** TMB (Fintech), PIT-SJC, Colmeia, NIMAS, UFF
- **Prêmios:** 1º lugar R$4.000 | 2º R$2.000 | 3º R$1.000 (+ brindes TMB)

---

## 2. A empresa — TMB

A TMB é uma fintech especializada em parcelamento via **boleto e Pix** para infoprodutores (criadores de cursos online, produtos digitais). Funciona como intermediária financeira no checkout: o aluno parcela o curso pela TMB, que repassa ao produtor e assume o risco de inadimplência.

**Diferencial:** equipe própria de cobrança + ecossistema de ferramentas (CRM, discador, agente virtual IA, WhatsApp API, portal de autonegociação).

---

## 3. O problema — First Payment Default (FPD)

### Definição
**FPD = cliente paga o boleto de entrada (1ª parcela) mas não paga nenhuma das parcelas seguintes.** É inadimplência imediata, logo no início da jornada.

### Impacto na TMB
- ~40% da inadimplência total da TMB vem de FPD
- Impacto triplo: receita comprometida + operação de cobrança sobrecarregada + carteira financiada deteriorada

### Por que é diferente do FPD bancário
O cliente FPD da TMB tem perfil único:
- Sem cartão de crédito / sem limite → usa boleto por exclusão financeira
- Score majoritariamente baixo (70% com alto risco estrutural)
- Compra por impulso emocional, sem planejamento financeiro
- Muitos não sabem que a TMB intermedeia — veem apenas o curso
- Histórico serial de abandono de cursos
- 80% consomem apenas ~10% do curso antes de abandonar
- Muitos nunca abrem o curso sequer uma vez após pagar a entrada

### Jornada típica do cliente FPD (menos de 30 dias)
1. **Descoberta** — vê o infoprodutor no Instagram, oferta com cronômetro
2. **Promessa** — acredita na multiplicação de ganhos a curto prazo
3. **Aquisição TMB** — nome negativado ou sem limite no cartão → boleto é a saída
4. **1ª semana** — percebe que o curso exige dedicação, curva de aprendizado; entusiasmo cai
5. **Abandono** — para de assistir, some silenciosamente (não cancela, não liga)
6. **FPD** — 2º boleto não é pago; dívida fica em aberto indefinidamente

> **Insight chave:** o abandono é silencioso. O cliente não cancela, não liga, não responde — ele simplesmente para. Isso exige detecção preditiva, não reativa.

### 5 arquétipos de FPD identificados na TMB

| # | Arquétipo | Descrição |
|---|-----------|-----------|
| 01 | Desorganização financeira | Tinha intenção real de pagar; realidade orçamentária impossibilitou. Maior abertura à renegociação. |
| 02 | Compra emocional | Decisão impulsiva pelo infoprodutor e promessa de ganho rápido. Emoção não se sustenta. |
| 03 | Falta de clareza | Não compreendeu o modelo de parcelamento, vencimentos ou consequências. Educação financeira ausente. |
| 04 | Arrependimento mascarado | Insatisfação com o curso/infoprodutor. Prefere parar de pagar e perde a data de cancelamento. |
| 05 | Fraude / oportunismo | Sem intenção real de pagar desde o início. Uso indevido do modelo de crédito. Menor abertura, foco em prevenção. |

---

## 4. O desafio técnico

### Objetivo
Construir um **modelo supervisionado de classificação binária** que estime a probabilidade de FPD (`prob_fpd`) para cada operação do conjunto de teste, usando **apenas informações disponíveis no momento do checkout**.

### Variável alvo
- `FPD = 1` → inadimplência no primeiro pagamento
- `FPD = 0` → sem default no primeiro pagamento

### Regra inegociável (leakage)
O modelo deve usar **somente dados disponíveis no checkout**. Qualquer coluna gerada ou atualizada após a venda, o primeiro vencimento ou a cobrança **invalida a solução**.

### Arquivos fornecidos
| Arquivo | Conteúdo |
|---------|----------|
| `dados.csv` | Base com `fpd_target` para treino e validação |
| `submission.csv` | Base sem rótulo para submissão final |
| `data_dictionary.csv` | Dicionário de dados |

Dados externos são permitidos, **desde que disponíveis no momento do checkout e sem vazamento temporal**.

---

## 5. Entregáveis obrigatórios

1. **`submission.csv`** com colunas: `pedido_id`, `prob_fpd`, `faixa_risco`
2. **Código/notebook** executável + `README.md` com instruções de reprodução
3. **Resumo executivo** (até 2 páginas ou 5 slides) cobrindo:
   - Problema atacado
   - Dados usados
   - Tratamento de missing e desbalanceamento
   - Algoritmo escolhido
   - Métricas locais
   - Top features
   - Proposta de uso operacional
   - Principais riscos e limitações
   - Política de cobrança derivada do modelo
4. **Política de cobrança por faixa de risco** (Seção 12A — obrigatório)
5. **Apresentação** com racional técnico e de negócio

---

## 6. Métricas de avaliação

### Métrica principal (leaderboard)
**ROC AUC** — mede capacidade de ordenação, padrão em risco de crédito, estável para ranking.

### Métricas secundárias (desempate e avaliação técnica)
- KS (Kolmogorov-Smirnov)
- PR AUC
- Recall
- FP/TP no threshold proposto pela equipe
- Taxa real de FPD por decil de score
- Coerência da política de cobrança com o perfil de risco

### Critérios de avaliação da banca (rubrica)
| Critério | Pontos |
|----------|--------|
| Performance técnica (AUC, KS, PR AUC, captura por decil) | 25 pts |
| Robustez e reprodutibilidade (código, pipeline, consistência) | 15 pts |
| Explicabilidade (features, faixas de risco, leitura por segmento) | 15 pts |
| Viabilidade operacional (checkout-only, sensibilidade a bureau) | 10 pts |
| Política de cobrança (coerência, acionabilidade, segmentação) | 20 pts |
| Qualidade da apresentação (pitch, defesa de trade-offs) | 15 pts |
| **Total** | **100 pts** |

---

## 7. Política de cobrança por faixa de risco (Seção 12A)

A política traduz o score em ações operacionais concretas. A TMB **não rejeita ninguém** — o objetivo é ajustar as condições de pagamento e acionar a cobrança de forma segmentada.

### Template de referência (sugestivo — equipe deve justificar os cortes nos dados)

| Faixa | prob_fpd | Ação | Canal / Timing | Escalada |
|-------|----------|------|----------------|----------|
| Baixo | 0,00–0,20 | Comunicação preventiva leve | E-mail D+1 | Sem escalada imediata |
| Médio | 0,21–0,45 | Notificação ativa + SMS | SMS/E-mail D+1 a D+3 | Para Alto em 5 dias sem pagamento |
| Alto | 0,46–0,70 | Ligação + oferta de renegociação | Ligação D+1 a D+5 | Para Crítico em 7 dias sem pagamento |
| Crítico | 0,71–1,00 | Acionamento prioritário + análise de negativação | Agente humano D+1 | Negativação após 30 dias |

### O que a equipe deve entregar na política
- Faixas de risco com intervalos de `prob_fpd` justificados pelos dados (curvas de ganho, tabelas de decil)
- Ação de cobrança por faixa
- Canal prioritário e timing de acionamento
- Proposta de renegociação, se aplicável
- Critério de escalada entre faixas
- Quantidade de clientes em cada faixa na base de teste
- Custo estimado de cobrança por faixa (se os dados permitirem)

---

## 8. Abordagem técnica recomendada

### Modelos que costumam funcionar bem neste tipo de problema
- **Baseline:** Regressão Logística bem tratada
- **Modelos principais:** LightGBM, XGBoost, CatBoost
- **Ensembles:** simples e defensáveis (voting, stacking leve)

### Boas práticas obrigatórias
- **Split temporal** (não random) — respeitar a ordem cronológica dos dados
- **Avaliar drift** entre treino e validação
- **Tratar missing explicitamente** (não simplesmente dropar)
- **Comparar modelo com e sem variáveis de bureau** — a banca vai perguntar
- **Calibrar probabilidades** se o modelo for usado para decisão (Platt Scaling ou Isotonic Regression)
- **Medir performance por subgrupo** (segmento, modalidade, estado)
- **Checar leakage linha por linha**
- **Analisar ganho em top decil e top ventil**
- **Desbalanceamento:** tratar com class_weight, undersampling ou oversampling (SMOTE) — explicar o racional
- Separação recomendada: 80/10/10 ou 70/15/15 (treino/validação/teste)

### Erros que eliminam soluções
- Random split (sem respeitar temporalidade)
- Usar variável pós-evento sem perceber (leakage)
- Confiar apenas em accuracy
- Ignorar desbalanceamento
- Usar IDs como feature
- Superajustar em uma safra específica
- Entregar score sem interpretação
- Propor threshold sem mostrar impacto em bons clientes barrados
- Propor política de cobrança sem ancorar nos scores do próprio modelo
- Definir faixas de risco arbitrariamente sem justificativa nos dados

---

## 9. Perguntas que a banca pode fazer

1. Qual foi a melhor métrica do modelo e em qual janela temporal?
2. Quais são as 10 variáveis mais relevantes?
3. O que acontece quando falta bureau?
4. Quanto FPD o modelo captura nos 10% piores casos?
5. Quantos bons clientes são barrados para cada FPD capturado?
6. Como o modelo se comporta por segmento, modalidade e estado?
7. Qual threshold recomendam para uso piloto — e por quê?
8. Quais são os critérios que definem cada faixa da política de cobrança?
9. Qual é o canal e timing de acionamento para cada faixa de risco?
10. Qual é o impacto esperado da política em volume de cobrança e custo operacional?

---

## 10. Composição da equipe e divisão de trabalho

| Perfil | Responsabilidades principais |
|--------|------------------------------|
| Dev 1 (ML/dados) | EDA, treinamento dos modelos, feature importance, fine tuning, análise sem bureau |
| Dev 2 (pipeline/engenharia) | Pipeline base, split temporal, pré-processamento, calibração, submission.csv, README |
| Dev 3 (visualização/pitch) | Template de slides, resumo executivo, gráficos de apoio para a apresentação |
| Economista | Mapeamento dos arquétipos de FPD, definição das faixas de risco com os dados, redação da política de cobrança (seção 12A), defesa do trade-off aprovação × cobrança no pitch |

### Roteiro por fase

**Fase 1 — Dia 1 tarde (13h30–17h30)**
- Todos: leitura do PDF desafio (seções 3, 4, 5, 8, 12, 12A), definição da abordagem
- Dev 1: EDA dos dados (taxa de FPD, missings, bureau)
- Dev 2: pipeline base (split temporal, encoding, missings)
- Dev 3: estrutura do pitch (5 slides)
- Economista: mapeamento dos 5 arquétipos + rascunho da política

**Fase 2 — Dia 2 manhã (09h–12h)**
- Dev 1: treinar LightGBM/XGBoost, tratar desbalanceamento, feature importance
- Dev 2: calibrar probabilidades, gerar submission.csv base
- Economista: definir faixas de risco com curva de ganho por decil

**Fase 3 — Dia 2 tarde (13h–17h30) + noite**
- Dev 1: fine tuning, ensemble, threshold final
- Dev 2: README.md + notebook limpo e reproduzível
- Dev 3: montar 5 slides do pitch
- Economista + Dev 3: redigir política 12A completa

**Fase 4 — Dia 3 (08h–12h entrega + 13h–15h pitch)**
- Todos: simular as 10 perguntas da banca, ensaiar pitch
- Checklist final: submission.csv + notebook + README + resumo executivo + apresentação (prazo 11h30)

---

## 11. Jornada de cobrança da TMB (referência para a política)

A TMB opera uma régua de cobrança multicanal com os seguintes marcos:

| Marco | Ações |
|-------|-------|
| Antes do vencimento (D-5, D-3, D-1) | E-mail + MIA (agente IA) + WhatsApp |
| D+0 (Marco crítico) | E-mail + WhatsApp |
| D+1 a D+2 | E-mail + MIA + Discador |
| D+5 a D+10 | E-mail + Discador + WhatsApp |
| D+15 | Enriquecimento de base + Discador + WhatsApp |
| D+30 | Negativação + Protesto |
| D+365 | Assessoria + Discador + WhatsApp + E-mail |

**Ferramentas disponíveis na TMB:** CRM (Cobrança 2.0), portal de autonegociação, agente virtual IA (MIA), WhatsApp API oficial, discador, RCS Google, SMS, e-mail, enriquecimento de base, Serasa Experian, Protesto24h, CAMEC (câmara arbitral), ajuizamento para high ticket.

---

## 12. Política de checkout da TMB (contexto adicional)

A TMB prioriza **aprovação com baixa fricção**, não rejeição. Os pilares são:
- Validação antifraude (parceiros especializados em identidade e análise comportamental)
- Baixa fricção (aprovação automatizada, fluxo otimizado para PIX e boleto)
- Sem restrição por inadimplência (foco na autenticidade da transação)
- Monitoramento contínuo (taxa de conversão, fraude, qualidade cadastral)

> A política de cobrança proposta pelas equipes deve ser consistente com essa diretriz: **ninguém é rejeitado no checkout** — o score de FPD serve para ajustar condições de pagamento e segmentar a régua de cobrança pós-venda.

---

## 13. Critérios de desempate

Em caso de empate no ranking:
1. Maior KS
2. Maior PR AUC
3. Melhor recall no top 10% de risco
4. Menor FP/TP no threshold apresentado
5. Qualidade e coerência da política de cobrança
6. Melhor nota da banca técnica

---

*Gerado em 18/05/2026 com base nos materiais oficiais do Science Hackathon by TMB: PDF-HACKATON.pdf, PROGRAMACAO.pdf, O_que_e_FPD.pdf, Workshop_Machine_Learning.pdf, Apresentacao_Recuperacao.pdf.*
