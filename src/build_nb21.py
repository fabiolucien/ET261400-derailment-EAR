# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells=[]; md=lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code=lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 21 · Validação temporal: cinco desenhos da literatura, para frente, para trás e em blocos

{HEADER_RULE}

**Pedido do autor (18/11).** Não ficar só no teste de três em três anos: testar ano a ano, cinco para frente, cinco para trás, um período contra o outro, e dizer com base em que metodologia publicada cada teste é feito.

**De onde vem cada desenho (declarado antes dos resultados).**

| Desenho | O que faz | Base na literatura |
|---|---|---|
| D1 · origem móvel, janela expansiva | calibra com 2011 até o ano T e confere em T+1 até T+H, para H de 1 a 5 anos; repete para todo T com pelo menos 4 anos de calibração | Tashman (2000): avaliação fora da amostra com origem móvel, recalibração a cada origem e vários períodos de teste |
| D2 · origem móvel, janela fixa | o mesmo, calibrando só com os últimos 3, 5 ou 7 anos | Tashman (2000): janela fixa contra janela expansiva |
| D3 · espelho para trás | calibra com os anos posteriores e confere os anteriores | robustez; não é previsão. Cerqueira, Torgo e Mozetič (2020) recomendam, para séries não estacionárias, os métodos que respeitam a ordem do tempo; por isso D1 é o principal e D3 só confere a estabilidade |
| D4 · validação cruzada em blocos | divide 2011 a 2025 em blocos contíguos de 5, 3 ou 1 ano; cada bloco é conferido com o modelo calibrado em todos os outros | Bergmeir e Benítez (2012); Roberts et al. (2017) |
| D5 · um ano de fora, com lacuna | como o D4 de 1 ano, retirando também o ano anterior e o posterior ao conferido | Bergmeir e Benítez (2012), variante que afasta os vizinhos dependentes |

**Por que avaliar em vários períodos, e não em um só.** Na avaliação de métodos de identificação de pontos críticos, os critérios clássicos comparam dois períodos consecutivos (Cheng e Washington, 2008; Montella, 2010); Guo, Wu e Lord (2020) mostram que isso ignora a instabilidade temporal dos acidentes e propõem critérios sobre vários períodos. A leitura do resultado como taxa de predição, com pesos calibrados no passado e conferidos no futuro, é a de Chung e Fabbri (2003).

**Por que três anos como horizonte principal.** A orientação de triagem de rede da Federal Highway Administration usa a média dos três a cinco anos mais recentes de acidentes; três anos é o menor horizonte dessa faixa e o que deixa mais origens. Os horizontes de 1 a 5 anos são todos reportados.

**Regras.** Nota só com atributos da via (regressão logística do notebook 18, hiperparâmetros fixos); no D1 também o modelo com histórico de acidentes. Todas as avaliações são reportadas; nenhuma é escolhida como resultado principal depois de vista. Avaliações com menos de 20 quilômetros atingidos na calibração ou na conferência são descartadas.

**Gates.** 20.936 células; 2.681 descarrilamentos por via; soma da matriz ano por célula igual a 2.681; D1 com H = 3 e origens de 2015 a 2022 reproduz o notebook 18 (0,752 sem histórico e 0,791 com histórico, tolerância de 0,002).""")
code(SETUP_CODE); code(open('nb21_code.py').read() + '\nlog_ia("21.1 desenhos declarados", "Claude", "FOCUS: cinco desenhos de validação temporal com referência; só atributos da via, mais histórico no D1", "lista J", "3 gates de contagem; gate do número de avaliações")')
code(open('nb21_run.py').read()); code(open('nb21_fig.py').read())
md(f"""---
## Referências (registro conferido na Scopus em 18/11/2026, pelo acesso do IME; resumo lido)

Bergmeir, C., & Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation. *Information Sciences, 191*, 192–213. https://doi.org/10.1016/j.ins.2011.12.028

Cerqueira, V., Torgo, L., & Mozetič, I. (2020). Evaluating time series forecasting models: An empirical study on performance estimation methods. *Machine Learning, 109*(11), 1997–2028. https://doi.org/10.1007/s10994-020-05910-7

Cheng, W., & Washington, S. (2008). New criteria for evaluating methods of identifying hot spots. *Transportation Research Record, 2083*, 76–85. https://doi.org/10.3141/2083-09

Chung, C.-J. F., & Fabbri, A. G. (2003). Validation of spatial prediction models for landslide hazard mapping. *Natural Hazards, 30*(3), 451–472. https://doi.org/10.1023/B:NHAZ.0000007172.62651.2b

Guo, X., Wu, L., & Lord, D. (2020). Generalized criteria for evaluating hotspot identification methods. *Accident Analysis & Prevention, 145*, 105684. https://doi.org/10.1016/j.aap.2020.105684

Montella, A. (2010). A comparative analysis of hotspot identification methods. *Accident Analysis & Prevention, 42*(2), 571–581. https://doi.org/10.1016/j.aap.2009.09.025

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881

Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: An analysis and review. *International Journal of Forecasting, 16*(4), 437–450. https://doi.org/10.1016/S0169-2070(00)00065-0

Federal Highway Administration. (s.d.). *Step 2. Conduct network screening*. Improving Safety on Rural Local and Tribal Roads: Safety Toolkit. https://highways.dot.gov/safety/local-rural/improving-safety-rural-local-and-tribal-roads-safety-toolkit/step-2-conduct (lida em 18/11/2026)

## Limites

Os atributos da via são os da Declaração de Rede de 2025 em todas as avaliações. As avaliações se sobrepõem no tempo e não são independentes: a média resume cada desenho e o intervalo por reamostragem de linhas trata a dependência espacial, não a temporal. No D2, as janelas mais longas só existem para origens mais recentes, o que confunde o efeito do tamanho da janela com o do período conferido. No D4 e no D5 a calibração usa anos posteriores ao conferido; servem para medir estabilidade, não para simular o uso.

{DECLARACAO_IA}""")
nb=nbf.v4.new_notebook(); nb["cells"]=cells; nb["metadata"]={"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"},"colab":{"name":"21_validacao_temporal_desenhos.ipynb"}}
nbf.write(nb,"21_validacao_temporal_desenhos.ipynb"); print("ok 21")
