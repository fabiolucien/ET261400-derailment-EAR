# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells=[]; md=lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code=lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 24 · Testes finais: modelos da aula 6, matriz de confusão, hiperparâmetros e malha nunca vista

{HEADER_RULE}

**Por que este passo.** A avaliação do short paper da edição 2026.1 (Prof. Tiago, 15/06/2026) apontou quatro lacunas: base empírica com uma única partição e sem repetições; falta de incerteza e de teste de significância; falta de matriz de confusão; falta de busca de hiperparâmetros. Este notebook fecha essas lacunas no mesmo protocolo da dissertação (versão 4 dos resultados da fase 11, 10/11/2026).

**Protocolo, igual ao notebook 23 e à dissertação.** Resposta: ter ao menos um descarrilamento por causa de via em 2011 a 2025 (2.123 de 20.936 km). Validação: trechos inteiros entre pátios fora do ajuste, cinco grupos, 30 sorteios (sementes 42 a 71), com a nota de cada quilômetro dada por um modelo que não viu o seu trecho (Roberts et al., 2017).

**Modelos, todos com os mesmos atributos e os mesmos sorteios.** Regra do EAR como adotada; Dummy pela taxa da malha; critérios do EAR contínuos (logística); com os atributos declarados da via: regressão logística, árvore de decisão, Random Forest, gradient boosting e MLP, os modelos da aula 6. Hiperparâmetros fixados antes de rodar; a seção 3 mede quanto o resultado muda com eles.

**Medidas.** AUC no país, dentro de cada malha e dentro de cada linha; PR-AUC (Saito e Rehmsmeier, 2015), porque só 10,1% dos quilômetros são atingidos; matriz de confusão, recall, precisão e F1 na classe muito alta, os 20% da extensão de maior nota (quintil superior, classe da dissertação).

**Gates.** Contagens; regra do EAR 0,588; logística com atributos, critérios contínuos e Dummy iguais ao notebook 23 (0,759; 0,632; 0,693; tolerância 0,002, mesmos sorteios); recall da logística igual à captura do notebook 23 (0,510); gradient boosting dentro das malhas perto da dissertação (0,671; tolerância 0,02, hiperparâmetros diferentes); malha nunca vista com critérios contínuos perto da dissertação (0,643; tolerância 0,02); rótulos embaralhados entre 0,45 e 0,55.""")
code(SETUP_CODE); code(open('nb24_code.py').read())
md(f"""---
## Referências

Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLoS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

## Limites

A padronização e a mediana usadas para preencher ausentes são calculadas na malha inteira, como nos notebooks anteriores e na dissertação; a resposta não entra nelas. Os atributos da via são os da Declaração de Rede de 2025. Os intervalos tratam a dependência espacial pela reamostragem de linhas inteiras; os sorteios não são independentes entre si.

{DECLARACAO_IA}""")
nb=nbf.v4.new_notebook(); nb["cells"]=cells; nb["metadata"]={"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"},"colab":{"name":"24_testes_finais_modelos.ipynb"}}
nbf.write(nb,"24_testes_finais_modelos.ipynb"); print("ok 24")
