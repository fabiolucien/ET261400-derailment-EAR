# -*- coding: utf-8 -*-
import nbformat as nbf
from nb_common import HEADER_RULE, SETUP_CODE, DECLARACAO_IA
cells = []; md = lambda s: cells.append(nbf.v4.new_markdown_cell(s)); code = lambda s: cells.append(nbf.v4.new_code_cell(s))
md(f"""# 28 · Auditoria dos sorteios: o resultado depende do acaso da partição?

{HEADER_RULE}

**Por que este passo.** A validação do artigo reparte os trechos inteiros entre pátios em cinco grupos, ao acaso, 30 vezes (sementes 42 a 71). O sorteio decide só quais trechos ficam fora do ajuste em cada rodada; não escolhe resultado. Este notebook confere, com os dados, quatro coisas: (i) a partição está correta (nenhum trecho dividido, cada quilômetro avaliado uma vez por sorteio); (ii) 30 sorteios bastam (a média não muda com mais sorteios); (iii) o resultado não é obra do acaso (teste de permutação de Ojala e Garriga, 2010, e um nulo que preserva o agrupamento espacial dos descarrilamentos); (iv) o bloco espacial tem a ordem de grandeza do alcance da dependência entre quilômetros vizinhos (Roberts et al., 2017). A repetição da partição responde à baixa replicabilidade de uma partição única (Bouckaert e Frank, 2004).

**Gates, declarados antes do código:** 0 trechos divididos; 20.936 células avaliadas por sorteio; pelo menos 100 km atingidos em cada grupo; regra do EAR 0,588; logística com atributos 0,759 (notebook 24); média da AUC com rótulos embaralhados entre 0,45 e 0,55.""")
code(SETUP_CODE)
code(open("nb27_base.py").read().replace('log_ia("27.0', 'log_ia("28.0'))
code(open("nb28_auditoria.py").read() + '\nexportar_registros("28")')
md(f"""---
## Referências

Bouckaert, R. R., & Frank, E. (2004). Evaluating the replicability of significance tests for comparing learning algorithms. In *PAKDD 2004* (LNCS 3056, pp. 3–12). Springer. https://doi.org/10.1007/978-3-540-24775-3_3

Ojala, M., & Garriga, G. C. (2010). Permutation tests for studying classifier performance. *Journal of Machine Learning Research, 11*, 1833–1863.

Roberts, D. R., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881

{DECLARACAO_IA}""")
nb = nbf.v4.new_notebook(); nb["cells"] = cells; nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"}, "language_info": {"name": "python"}, "colab": {"name": "28_auditoria_sorteios.ipynb"}}
nbf.write(nb, "28_auditoria_sorteios.ipynb"); print("ok 28")
