# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells=[]; md=lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code=lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 25 · Decomposição do ganho dos critérios do EAR: faixas, pesos, AMV e medida contínua

{HEADER_RULE}

**Por que este passo.** A revisão independente de 22/11 apontou que a logística sobre os critérios contínuos muda três coisas de uma vez em relação à regra do EAR: aprende os pesos, acrescenta a distância ao AMV estimado e troca as faixas pela medida contínua. Sem separar as três, a frase "a medida importa mais que as faixas" não decorre do desenho.

**Desenho, declarado antes de rodar.** Mesmos dados, resposta, 30 sorteios e grupos do notebook 24 (trechos inteiros entre pátios fora do ajuste). R0: regra do EAR como adotada. R1: as mesmas faixas de distância ao pátio e classes de raio, com pesos aprendidos (logística). R2: R1 mais as faixas de distância ao AMV estimado. R3: os critérios contínuos do notebook 24. As diferenças R1 − R0, R2 − R1 e R3 − R2 somam R3 − R0.

**Gates.** Contagens e regra iguais ao notebook 24; R3 igual aos critérios contínuos do notebook 24 (0,632 no país e 0,655 dentro das malhas, tolerância 0,002); soma das parcelas igual ao total; rótulos embaralhados entre 0,45 e 0,55.""")
code(SETUP_CODE); code(open('nb25_code.py').read())
md(f"""---
## Referências

Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

## Limites

A padronização e a mediana usadas para preencher ausentes são calculadas na malha inteira, como nos notebooks anteriores e na dissertação; a resposta não entra nelas. Os atributos da via são os da Declaração de Rede de 2025. Os intervalos tratam a dependência espacial pela reamostragem de linhas inteiras; os sorteios não são independentes entre si.

{DECLARACAO_IA}""")
nb=nbf.v4.new_notebook(); nb["cells"]=cells; nb["metadata"]={"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"},"colab":{"name":"25_decomposicao_criterios_ear.ipynb"}}
nbf.write(nb,"25_decomposicao_criterios_ear.ipynb"); print("ok 25")
