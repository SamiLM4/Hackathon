# Política de Cobrança por Faixa de Risco — Seção 12A

> Política derivada do modelo preditivo de FPD. Cortes definidos com base na
> curva de ganho por decil e na distribuição real das probabilidades na base de submissão.

## Tabela de Faixas

| Faixa | prob_fpd | Clientes | % Carteira | Ação de Cobrança | Canal / Timing | Escalada |
|-------|----------|----------|------------|-----------------|----------------|----------|
| 🟢 Baixo | 0,00–0,20 | 10737 | 46.0% | Comunicação preventiva leve | E-mail D+1 | Nenhuma imediata |
| 🟡 Médio | 0,21–0,45 | 10789 | 46.2% | Notificação ativa + WhatsApp | SMS/WhatsApp D+1 a D+3 | Para Alto se 5 dias sem pagar |
| 🟠 Alto | 0,46–0,70 | 1791 | 7.7% | Ligação + oferta de renegociação | Discador D+1 a D+5 | Para Crítico se 7 dias sem pagar |
| 🔴 Crítico | 0,71–1,00 | 37 | 0.2% | Acionamento prioritário + análise de negativação | Agente humano D+1 | Negativação após 30 dias |

## Diretrizes Gerais

- **A TMB não rejeita ninguém no checkout.** O score de FPD ajusta a intensidade da cobrança pós-venda.
- Faixas calibradas pelo Economista da equipe com base na curva de ganho por decil.
- Todos os cortes devem ser revisados antes da apresentação final.

## Ferramentas TMB por Faixa

| Faixa | Ferramentas |
|-------|------------|
| Baixo | E-mail automatizado, MIA (agente IA) |
| Médio | MIA + WhatsApp API + SMS |
| Alto | Discador + WhatsApp + Portal de Autonegociação |
| Crítico | Agente humano (CRM 2.0) + Serasa Experian + Protesto24h |

*Gerado automaticamente pelo Módulo 7 do notebook Dev 3.*
