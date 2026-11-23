# Conferência independente: taxa de acerto por origem móvel (malha ferroviária existente)

Você atua como revisor PhD em aprendizado de máquina aplicado a transportes e em estatística. Trabalho de mestrado (IME, Engenharia de Transportes). Nada pode ser inventado: rode o código nos dois arquivos anexos e reporte só o que o código devolver. Se algo não puder ser calculado, diga.

## Arquivos

- `celulas_operacao.csv`: 20.936 linhas, uma por célula de cerca de 1 km de via em operação (13 malhas federais do Brasil). Colunas de identificação: `cel_id`, `ferrovia`, `linha`, `seg_id`, `len_km`.
- `eventos_via.csv`: 2.681 linhas, um descarrilamento por causa de via por linha (RAAF/ANTT, 2011 a 2025). Colunas: `cel_id`, `ano`.

## Protocolo (não altere)

Para cada ano de origem T de 2015 a 2022 (oito origens):

1. `y_cal` = 1 se a célula teve ao menos um evento de 2011 a T. `y_conf` = 1 se teve ao menos um evento de T+1 a T+3. `n_conf` = número de eventos de T+1 a T+3 na célula.
2. Regra do EAR (sem ajuste): c = 4 se dmin_patio <= 300; 3 se <= 600; 2 se <= 1200; 1 se <= 1800; senão 0 (ausente vale 0). r = 3 se rmin_geo < 500; 2 se < 1200; 1 se < 2300; senão 0 (ausente vale 0). Nota = 0,5*c/4 + 0,5*r/3.
3. Dummy da malha: nota = média de `y_cal` na `ferrovia` da célula.
4. EAR calibrado: regressão logística do scikit-learn (C=0.5, max_iter=3000, solver padrão), ajustada em todas as células com `y_cal`, nota = probabilidade prevista para todas as células. Atributos numéricos (imputar a mediana e acrescentar um indicador de ausente para cada um): dmin_patio, dmin_amv, frac_zona_patio, f16p0 a f16p4, f16a0 a f16a4, rmin_geo, fr_lt300, fr_lt400, fr_lt500, fr_lt600, fr_lt800, rampa_max_pct, carga_eixo_t, taxa_dorm, gab_vert_m, gab_horiz_m, cap_vinc, dias_op, raio_min_m, vma_carregado. Atributos categóricos em one-hot (texto sem espaços nas pontas; ausente vira "NA"): dormente, perfil_trilho, fixacao, sinalizacao, controle_circ, bitola, sentido, n_linhas. Padronizar todas as colunas (StandardScaler) antes do ajuste. O histórico de acidentes não entra como atributo.
5. Medidas, sempre contra `y_conf`: (a) AUC em todas as 20.936 células; (b) AUC dentro da malha: AUC calculada em cada `ferrovia` com pelo menos 5 células com y_conf = 1, média ponderada pelo número dessas células; (c) taxa de acerto em 20%: ordenar as células por nota decrescente (empates em ordem aleatória com semente 42), marcar enquanto a soma acumulada de `len_km` dividida pelo total for <= 0,20, e dividir a soma de `n_conf` nas células marcadas pela soma total de `n_conf`; (d) o mesmo com 0,40; (e) concentração de risco em 20%: média de `y_conf` nas marcadas dividida pela média nas não marcadas.

## O que devolver

1. Tabela com a média das oito origens, por método (regra, Dummy, EAR calibrado): AUC, AUC dentro da malha, acerto em 20%, acerto em 40%, concentração em 20%. Três casas decimais.
2. Tabela da AUC por origem (oito linhas, três métodos).
3. Em até dez linhas, sua avaliação crítica, sem elogios: (i) a origem móvel para frente é a forma estatisticamente correta de estimar a taxa de acerto quando ela varia conforme o ano? que alternativa você usaria? (ii) com esses atributos públicos, AUC entre 0,8 e 0,9 é meta realista? (iii) "alarme falso" é medida adequada para evento raro (cerca de 2% das células com evento em três anos)? (iv) que critério de via ainda falta e poderia ser obtido de fonte pública?
