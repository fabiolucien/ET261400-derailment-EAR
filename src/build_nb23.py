# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells=[]; md=lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code=lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 23 · Teste geral: todos os acidentes de 2011 a 2025, sem recorte de tempo

{HEADER_RULE}

**Pedido do autor (18/11, 0h58).** Além dos testes por janela de tempo, fazer a conta geral: usar todo o intervalo de acidentes de uma vez e ver se a nota funciona, sem depender da escolha de um período.

**O que é o teste geral.** A resposta de cada quilômetro é ter tido ao menos um descarrilamento por via em qualquer ano de 2011 a 2025. A nota de cada quilômetro é dada por um modelo que não viu aquele trecho: a malha é dividida em cinco grupos, quatro calibram e o quinto é conferido, e isso se repete até todos serem conferidos.

**Desenhos, declarados antes dos resultados, e de onde vêm.**

| Desenho | O que fica fora do ajuste | Base na literatura |
|---|---|---|
| G1 (principal) | trechos inteiros entre pátios, 30 sorteios | validação cruzada em blocos espaciais: quilômetros vizinhos são dependentes e precisam ficar do mesmo lado da divisão (Roberts et al., 2017) |
| G2 (mais exigente) | linhas inteiras, 10 sorteios | o mesmo, com blocos maiores |
| G0 (só referência) | quilômetros sorteados ao acaso, 10 sorteios | é a divisão ao acaso da aula 6; aqui é otimista, porque o vizinho do quilômetro conferido está no ajuste (Roberts et al., 2017) |

**Como este teste se relaciona com os testes no tempo (notebook 21).** O teste geral pergunta se a nota separa os quilômetros com e sem acidente em trechos que o modelo não viu. Os testes no tempo perguntam se a nota calibrada no passado antecipa os acidentes dos anos seguintes (Tashman, 2000; Chung e Fabbri, 2003). São perguntas diferentes; a última célula põe os resultados lado a lado.

**Gates.** 20.936 células; 2.681 descarrilamentos por via; 2.123 quilômetros atingidos; regra do EAR no período inteiro 0,588; G1 reproduz o notebook 11 (EAR calibrado 0,761, critérios contínuos 0,634, Dummy da malha 0,693; tolerância de 0,005, porque o sorteio dos grupos não é o mesmo); rótulos embaralhados dão AUC entre 0,45 e 0,55.""")
code(SETUP_CODE); code(open('nb23_code.py').read())
md(f"""---
## Referência

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881 (registro conferido na Scopus em 18/11/2026; resumo lido)

## Limites

No teste geral o modelo é calibrado com acidentes de todos os anos, inclusive os mais recentes; ele mede se a nota vale para trechos não vistos, não se antecipa o futuro. Os atributos da via são os da Declaração de Rede de 2025. A AUC do país inclui a diferença entre malhas (o Dummy da malha mostra quanto); a AUC dentro da malha mede só a separação entre quilômetros da mesma malha.

{DECLARACAO_IA}""")
nb=nbf.v4.new_notebook(); nb["cells"]=cells; nb["metadata"]={"kernelspec":{"name":"python3","display_name":"Python 3"},"language_info":{"name":"python"},"colab":{"name":"23_teste_geral_periodo_inteiro.ipynb"}}
nbf.write(nb,"23_teste_geral_periodo_inteiro.ipynb"); print("ok 23")
