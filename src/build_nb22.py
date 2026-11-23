# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells=[]; md=lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code=lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 22 · Tabelas e figuras do short paper: partição no tempo, mapa, taxas por fator e modelo de linguagem

{HEADER_RULE}

**Para que serve.** Gera, a partir dos dados, cada número e cada figura que entra no artigo e que ainda não tinha notebook próprio: (1) a partição no tempo usada na dissertação (calibra de 2011 a 2020, confere de 2021 a 2025; Chung e Fabbri, 2003), com o mapa da classe muito alta e a curva de taxa de predição; (2) a taxa de descarrilamentos por fator, que tinha sido calculada à mão em 16/11; (3) o kappa e a cobertura do modelo de linguagem na amostra confirmatória, recalculados dos rótulos gravados.

**Gates.** 20.936 células; 2.681 descarrilamentos por via; AUC do EAR calibrado na partição dentro da faixa já vista para janelas de 10 por 5 anos (0,70 a 0,85); 18.618 células com posição; soma dos eventos por bitola igual a 2.681; 600 narrativas na amostra B; kappa de 0,866 e cobertura de 0,652 do notebook 04b (tolerância de 0,001).""")
code(SETUP_CODE); code(open('nb22_code.py').read()); code(open('nb22_fig.py').read())
md(f"""---
## Limites

A partição única de 2011 a 2020 contra 2021 a 2025 é uma das 185 avaliações do notebook 21 e serve para o mapa; o resultado principal do artigo é a média da origem móvel. As taxas por fator olham um fator por vez e os fatores andam juntos (bitola métrica costuma ter dormente de madeira e trilho leve): mostram associação, não causa. 11% das células não têm posição no mapa (notebook 13) e não aparecem na figura, mas entram em todos os números.

{DECLARACAO_IA}""")
nb=nbf.v4.new_notebook(); nb["cells"]=cells; nb["metadata"]={"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"},"colab":{"name":"22_artigo_tabelas_figuras.ipynb"}}
nbf.write(nb,"22_artigo_tabelas_figuras.ipynb"); print("ok 22")
