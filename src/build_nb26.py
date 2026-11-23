# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells=[]; md=lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code=lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 26 · Testes pedidos pela revisão independente: desenho conjunto no tempo e no espaço, calibração e modelo de linguagem na mesma cobertura

{HEADER_RULE}

**Por que este passo.** Duas revisões independentes do artigo (22/11) pediram três testes curtos. (1) A conferência no tempo ajusta e confere nas mesmas células; falta um desenho que esconda ao mesmo tempo os anos futuros e os trechos conferidos. (2) As notas são usadas como ordem; falta dizer quanto valem como probabilidade (Brier e inclinação de calibração). (3) O modelo de linguagem foi comparado ao TF-IDF em coberturas diferentes; falta compará-los na mesma cobertura.

**Desenho, declarado antes de rodar.** (1) Origem móvel com janela expansiva, como no notebook 21: horizonte de 3 anos (origens 2015 a 2022) e de 1 ano (2014 a 2024); em cada origem, os trechos entre pátios ficam fora do ajuste em cinco grupos, cinco sorteios. (2) Protocolo espacial do notebook 24, 10 sorteios, logística com atributos e gradient boosting. (3) Mesmo TF-IDF e mesma amostra B do notebook 04b; o TF-IDF se abstém nas narrativas de menor confiança até a cobertura do Sonnet.

**Gates.** Contagens e regra iguais ao notebook 24; mesmas células com H = 3 iguais ao notebook 18 (0,752 e 0,665; regra 0,580); Brier da taxa-base igual a p(1 − p); TF-IDF perto do notebook 04b (0,613 e 0,802, tolerância 0,03); Sonnet igual ao notebook 04b (0,866).""")
code(SETUP_CODE); code(open('nb26_code.py').read())
md(f"""---
## Referências

Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

## Limites

A padronização e a mediana usadas para preencher ausentes são calculadas na malha inteira, como nos notebooks anteriores e na dissertação; a resposta não entra nelas. Os atributos da via são os da Declaração de Rede de 2025. Os intervalos tratam a dependência espacial pela reamostragem de linhas inteiras; os sorteios não são independentes entre si.

{DECLARACAO_IA}""")
nb=nbf.v4.new_notebook(); nb["cells"]=cells; nb["metadata"]={"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"},"colab":{"name":"26_testes_da_revisao.ipynb"}}
nbf.write(nb,"26_testes_da_revisao.ipynb"); print("ok 26")
