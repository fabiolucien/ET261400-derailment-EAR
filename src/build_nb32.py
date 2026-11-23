# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
REFS = ("Mantel, N., & Haenszel, W. (1959). Statistical aspects of the analysis of data from retrospective studies of disease. *Journal of the National Cancer Institute, 22*(4), 719–748.\n\n"
        "Agência Nacional de Transportes Terrestres. Relatório de Acompanhamento de Acidentes Ferroviários (RAAF), campos PN e Perímetro_Urbano; dados abertos, CC BY.")
cells = []; md = lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md("# 32 · Antes e depois do pátio, limite de 500 m ou 1 km, linhas duplicadas e de pouco tráfego, critério novo\n\n" + HEADER_RULE + "\n\n"
   "**Por que este passo.** Responde a cinco dúvidas do autor sobre os parâmetros do EAR: (1) o excesso de risco no km antes e depois do pátio não seria acidente de PN ou OAE vizinhos? "
   "(2) a faixa deve valer dos dois lados do pátio? (3) a faixa alta termina em 500 m ou em 1 km, para frente, para trás no tempo e numa ferrovia fora do ajuste? "
   "(4) tirar as linhas duplicadas da Vale, as malhas pequenas e os trechos de pouco tráfego muda o resultado? (5) algum critério novo deve entrar no EAR? "
   "As regras de decisão estão no início do código e foram escritas antes dos resultados. Os campos PN e local registrado vêm do RAAF por `data/processed/32_raaf_pn_local.csv`, "
   "gerado por `prep32_raaf_pn_local.py` sem ler o campo Equipagem.")
code(SETUP_CODE); code(open("nb27_base.py").read().replace('log_ia("27.0', 'log_ia("32.0'))
code(open("nb32_antes_depois_dominio.py").read() + '\nexportar_registros("32")')
md(f"---\n## Referências\n\n{REFS}\n\n{DECLARACAO_IA}")
nb = nbf.v4.new_notebook(); nb["cells"] = cells; nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "32_antes_depois_dominio.ipynb"}}
nbf.write(nb, "32_antes_depois_dominio.ipynb"); print("ok 32")
