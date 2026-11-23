---
title: "Parâmetros do EAR atualizados com o registro de acidentes"
subtitle: "ET 261400 · Fábio Lucien David Maciel · 23/11/2026 · notebooks 29, 30 e 31, revisados por ChatGPT, Gemini e Claude"
---

## 1. Em cinco linhas

1. Dos 12 atributos da Declaração de Rede, só o tráfego vinculado e a carga por eixo mudam o risco **dentro** de uma ferrovia. Velocidade, rampa, dormente, trilho, bitola e sinalização parecem importar no país, mas isso é diferença entre ferrovias.
2. A tabela de multiplicadores (pátio, raio e tráfego) ordena uma ferrovia que ficou fora do ajuste melhor que as faixas da FICO: 0,65 contra 0,60 nas células a até 20 km de um pátio, e é melhor em 11 de 12 malhas.
3. O erro de posição (km do acidente e posição do AMV) não derruba o ganho nem o excesso de risco perto do pátio e nas curvas abaixo de 300 m. O limite de 1 km, porém, não é firme: oscila com 500 m.
4. Os descarrilamentos registrados dentro da extensão do pátio sustentam sozinhos o excesso da célula do pátio. O km seguinte mantém o excesso sem eles (1,81).
5. O tráfego é exposição, e não suscetibilidade da via: no EAR, entra na etapa de frequência, e não nas faixas.

## 2. Como a validação foi feita

1. **Unidade e resposta.** 20.936 células de cerca de 1 km em operação nas 13 malhas federais; a resposta é a célula ter tido descarrilamento por causa de via em 2011–2025 (2.123 km).
2. **Trechos fora do ajuste.** Trechos inteiros entre pátios repartidos em 5 grupos; ajuste com 4, nota no 5º. A partição é repetida 30 vezes, com as sementes 42 a 71, fixadas antes. O notebook 28 conferiu a partição, a estabilidade e o acaso (permutação e nulo espacial).
3. **Sem vazamento.** Os limites das faixas são reescolhidos só nos grupos de ajuste. No teste de ferrovia nova, também sem a malha testada.
4. **Ferrovia nova.** Cada malha inteira fica fora do ajuste, inclusive na escolha dos limites e dos multiplicadores, e é ordenada pelo que se aprendeu nas outras.
5. **Intervalos e testes.** IC 95% por 300 reamostragens de linhas inteiras; teste de sinal entre malhas; correção de Holm para 12 fatores; intervalo de predição entre malhas (efeitos aleatórios).
6. **Gates declarados antes de cada código**, com o gate loop registrado quando um falhou (placebo do notebook 29; posição dos eventos no notebook 31).

## 3. Fatores da Declaração de Rede: o que é parâmetro do EAR (notebook 29)

Regra declarada antes: o fator entra se (a) varia dentro de pelo menos 3 malhas, (b) alguma classe tem risco relativo dentro das malhas com IC que exclui 1 e (c) melhora a ordenação dentro das malhas em trechos fora do ajuste, com IC acima de zero. Os dois aprovados passam também na correção de Holm.

| Fator (classe comparada) | RR no país, bruto | RR dentro das malhas, ajustado (IC 95%) | Decisão |
|---|---|---|---|
| Tráfego, 3 a 10 trens/dia (contra 1 a 3) | 0,85 | 1,46 (1,10 a 2,06) | aprovado; ganho de +0,037 (0,018 a 0,064) |
| Carga por eixo, acima de 30 t (contra até 20 t) | 0,48 | 1,92 (1,37 a 3,22) | aprovado; ganho de +0,015 (0,004 a 0,030) |
| Velocidade, acima de 60 km/h (contra até 30) | 0,28 | 1,13 (0,43 a 2,33) | reprovado |
| Rampa, acima de 2% (contra até 1%) | 2,50 | 1,33 (0,98 a 1,94) | reprovado |
| Dormente de concreto (contra madeira) | 0,36 | 1,00 (0,71 a 1,29) | reprovado |
| Sinalização CTC, CBTC ou ATC (contra ABS) | 0,44 | 2,48 (1,93 a 3,69) | não estimável: só 2 malhas variam |
| Bitola larga (contra métrica) | 0,31 | 1,05 (0,55 a 2,50) | não estimável: só 1 malha varia |

**Leitura.** No país, velocidade alta e dormente de concreto "protegem" porque as ferrovias que os têm descarrilam menos. Dentro da mesma ferrovia, o efeito some, e a carga por eixo até se inverte (paradoxo de Simpson).

**Conciliação com o artigo.** O artigo diz que os atributos, em conjunto, não acrescentam nada mensurável dentro das malhas (+0,009). O teste que decide confirmou a frase e acrescentou um dado: o tráfego, sozinho, soma +0,020 (0,006 a 0,041) mesmo sobre os critérios contínuos. A frase foi ajustada na v10.

## 4. Tabela para replicar num EAR (notebook 30, variante B)

Os multiplicadores são riscos relativos dentro das malhas (Mantel-Haenszel), com IC por linhas. O intervalo de predição mostra a faixa provável numa ferrovia que não está nos dados (efeitos aleatórios entre malhas).

| Critério | Classe | Multiplicador (IC 95%) | Intervalo de predição (ferrovia nova) |
|---|---|---|---|
| Pátio/AMV | célula do pátio (até 250 m) | 1,98 (1,70 a 2,31) | 1,13 a 3,34 |
| | 250 m a 1 km | 1,91 (1,49 a 2,36) | 0,80 a 5,43 |
| | 1 a 1,5 km | 1,17 (0,96 a 1,46) | 0,48 a 3,61 |
| | 1,5 a 3 km | 1,06 (0,91 a 1,23) | 0,54 a 1,96 |
| | 3 a 20 km (referência) | 1 | |
| | acima de 20 km | 0,31 (0,17 a 0,69) | não usar em linha nova (mede linha pouco usada) |
| Raio | abaixo de 250 m | 1,76 (1,38 a 2,42) | 0,55 a 7,76 |
| | 250 a 300 m | 1,30 (1,09 a 1,64) | 0,66 a 2,97 |
| | 300 a 600 m | 1,15 (1,02 a 1,30) | 0,86 a 1,53 |
| | 600 m ou mais e tangente (referência) | 1 | |
| Tráfego (exposição) | até 1 trem/dia | 0,57 (0,27 a 0,87) | 0,12 a 1,87 |
| | 1 a 3 trens/dia (referência) | 1 | |
| | 3 a 10 trens/dia | 1,44 (1,09 a 2,05) | 0,93 a 2,55 |
| | acima de 10 trens/dia | 1,42 (0,99 a 1,96) | 1,08 a 1,95 |

Na ferrovia nova, só dois intervalos de predição ficam inteiros acima de 1: o da célula do pátio e o do tráfego acima de 10 trens por dia. Os demais multiplicadores valem para ordenar, mas a malha pode mudá-los bastante.

**Como aplicar** (ferramenta `ear_v3_aplicar.py` no repositório):

1. Dividir o traçado em células de 1 km.
2. Para cada célula, informar a distância à ponta do pátio ou ao AMV mais próximo, o raio mínimo e o tráfego previsto (trens por dia).
3. Índice técnico = multiplicador do pátio × multiplicador do raio. Índice com exposição = índice técnico × multiplicador do tráfego.
4. Classes do mapa pela extensão da própria linha: 10% muito alta, 20% alta, 30% moderada, 40% baixa.
5. O índice ordena; não é probabilidade. Para a frequência do EAR, a taxa de base por trem-km vem de outra fonte.

Exemplo: na Norte-Sul (FNSTN), a classe muito alta (10% da extensão, 72 km) reúne 9 dos 19 km atingidos em 2011–2025. É uma ilustração com a tabela de todas as malhas; o teste sem a FNSTN está no item 5.

## 5. Ferrovia nova e caso Norte-Sul (notebook 30)

| Escore | Malha fora, todas as células | Malha fora, até 20 km de pátio | Malhas acima da FICO |
|---|---|---|---|
| Regra da FICO | 0,589 | 0,596 | n.a. |
| Regra aferida (limites reescolhidos sem a malha) | 0,607 | 0,618 | 8 e 9 de 12 |
| Logística com os 9 atributos | 0,633 | 0,614 | 8 e 7 de 12 |
| Pátio, raio e tráfego (multiplicadores) | 0,677 | 0,645 | 11 de 12 |

- Com todas as células, o ganho sobre a FICO é +0,088 (IC 0,040 a 0,125; teste de sinal, p = 0,003). Parte dele vem da classe acima de 20 km, que mede linha pouco usada. O artigo cita o recorte até 20 km.
- A logística conjunta com as mesmas classes, sem efeito de malha, fica abaixo dos multiplicadores (−0,057; IC −0,096 a −0,017). Estimar o risco dentro das malhas é o que transfere.
- A carga por eixo não melhora a malha fora (−0,004; IC −0,012 a 0,004) e derruba a ordenação nacional. A tabela fica sem ela, por parcimônia; a escolha foi feita depois dos resultados e está declarada.
- **Norte-Sul, ajustada sem ela:** faixas do EAR da FNS 0,62 (IC 0,49 a 0,76); regra aferida 0,70; pátio, raio e tráfego 0,74 (0,61 a 0,87); logística 0,77. Com 19 km atingidos, os intervalos se sobrepõem, e o caso não prova nada sozinho.

## 6. Monte Carlo, SIMEX e artefato de pátio (notebook 31)

| Cenário (200 réplicas) | Ganho sobre a FICO | Limites de pátio iguais aos do artigo | Limites de raio iguais |
|---|---|---|---|
| S1 km do acidente ±0,5 km | +0,023, em 100% | 77% | 64% |
| S2 km do acidente ±1 km | +0,024, em 100% | 40% | 33% |
| S3 pátio ±250 m | +0,021, em 100% | 10% | 100% |
| S4 S1 e S3 juntos | +0,022, em 100% | 9% | 64% |
| S5 pátio ±500 m | +0,021, em 100% | 3% | 100% |
| S6 deslocamento comum por linha ±0,5 km | +0,023, em 100% | 80% | 54% |

- Em todos os cenários: risco relativo da célula do pátio de 1,8 a 2,1, e das curvas abaixo de 300 m de 1,4 a 1,6. Com erro de pátio, o limite intermediário passa de 1.000 m a 500 m.
- **SIMEX** (extrapola para erro zero no km): célula do pátio 1,91; até 1 km 2,18; 1 a 1,5 km 1,08; raio abaixo de 300 m 1,55. O erro atenua pouco os resultados.
- **Artefato de pátio:** os km inteiros não se concentram na célula do pátio (25% contra 29% nas demais). Sem os eventos no km exato do pátio, a célula mantém excesso (1,72). Sem todos os eventos dentro da extensão do pátio, a célula do pátio cai para 0,69, e o km seguinte mantém 1,81. O RAAF de 2011–2025 não separa linha de pátio e linha principal, então essa parte fica em aberto.

## 7. Revisão externa (ChatGPT, Gemini e Claude, 22/11, 23h10)

Notas das três análises: 29, de 7,5 a 8,5; 30, de 7,0 a 7,5; 31, de 7,0 a 8,5. Pontos em comum, todos atendidos antes desta nota:

1. Tráfego como exposição.
2. Escolha da variante pela malha fora, por parcimônia.
3. Parar de cravar 1 km no artigo.
4. Análise 30 como exploratória.

Correções pedidas e feitas:

- referência do pátio igual à do artigo;
- limites reescolhidos sem vazamento;
- Holm;
- intervalo de predição;
- IC pareado e teste de sinal na malha fora;
- AUC dentro das linhas;
- erro-padrão no caso Norte-Sul;
- cenário sistemático por linha;
- SIMEX;
- artefato de pátio;
- conciliação com a frase do artigo.

Registro completo em `revisoes/revisao3_respostas.md`.

## 8. O que mudou no artigo (v10) e o que ficou fora

**Entrou na v10:**

- **Seção 3.1:** só o tráfego e a carga mudam o risco dentro das malhas; o tráfego soma 0,020.
- **Seção 3.2:**
  - o Monte Carlo (ganho e excessos firmes; o limite de 1 km volta em só 3% a 80% das réplicas);
  - o artefato de pátio (0,69 e 1,81);
  - o teste de ferrovia nova (0,65 contra 0,60, melhor em 11 de 12 malhas).
- **Conclusões:** alta "entre 500 m e 1 km"; o tráfego vai para a etapa de frequência; limitação sobre linha de pátio.
- **Contagem:** 2.994 palavras na contagem conservadora; resumo com 198.

**Versão 11 (revisão externa 4, 23/11, 0h15 a 0h40):** resumo coerente com o Monte Carlo (o excesso perto do pátio resiste ao erro de posição; o limite exato, não); Holm e efeito fixo de malha nomeados em Dados e Métodos; carga por eixo informada (acima de 30 t, RR 1,92; IC 1,37 a 3,22); teste do sinal na ferrovia nova (p = 0,003); matriz de confusão que soma 20.936; verbos calibrados ("partly", "limit leakage", "better match"); Dados e Métodos com 999 palavras; total de 2.985.

**Execução do zero (23/11, 23h40 a 0h35):** 17 passos, 153 de 153 gates; as tabelas dos passos 15 a 28 saíram idênticas byte a byte às da execução anterior, e o texto do artigo preenchido com as tabelas novas não mudou em nenhum número.

**Ficou no repositório e nos slides de reserva:** a tabela completa de multiplicadores, os 12 fatores, os seis cenários, o caso Norte-Sul e a ferramenta de aplicação.

## 9. Limites honestos

- O tráfego é capacidade vinculada de 2025, não tráfego observado em cada ano. A tonelagem por trecho não entrou (ver o item 10).
- Não há cadastro público de AMV, PN e OAE.
- A ferrovia nova foi simulada com malhas existentes: falta conferir numa linha nova quando ela entrar em operação.
- O raio vem do eixo público, não do projeto.

## 10. Tonelagem e tipo de produto: próximo passo possível

A tonelagem por trecho e o tipo de produto não vêm prontos na Declaração de Rede, mas dá para derivá-los. A ANTT publica a produção mensal por fluxo de origem e destino, com mercadoria, TU e TKU, de 2017 a 2025, no SIADE, sob licença Creative Commons Atribuição. O caminho:

1. distribuir cada fluxo pela rota entre as estações de origem e de destino, no eixo da malha;
2. somar TU e TKU por célula e por mercadoria;
3. repetir o notebook 29 com tonelagem bruta e grupo de produto, separando exposição (toneladas) de suscetibilidade.

Não foi feito nesta rodada, porque a atribuição de rotas exige conferir o nome das estações contra os pátios da Declaração de Rede.

## 11. Uso de IA

Claude (Anthropic) escreveu o código dos notebooks 29 a 31 a partir das especificações FOCUS, com gates declarados antes, e redigiu esta nota. ChatGPT, Gemini e Claude revisaram as análises como banca. Os números foram conferidos por rota independente (statsmodels e sklearn). O autor responde pelo conteúdo.
